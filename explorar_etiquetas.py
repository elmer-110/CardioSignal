"""Práctica 4: etiquetas diagnósticas y particiones oficiales de PTB-XL.

Solo utiliza la biblioteca estándar de Python. No entrena un modelo.
"""

import ast
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent
SOURCE = "https://physionet.org/files/ptb-xl/1.0.3"
CLASSES = {
    "NORM": "ECG normal (etiqueta del conjunto)",
    "MI": "Infarto de miocardio (categoría de anotación del ECG)",
    "STTC": "Alteraciones ST/T",
    "CD": "Alteraciones de conducción",
    "HYP": "Hipertrofia",
}


def read_metadata(filename):
    folder = ROOT / "data" / "metadata"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / filename
    if not path.exists():
        print(f"Descargando {filename}...", flush=True)
        with urlopen(f"{SOURCE}/{filename}", timeout=90) as response:
            content = response.read()
        temporary = path.with_suffix(".tmp")
        temporary.write_bytes(content)
        temporary.replace(path)
    with path.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    return rows, hashlib.sha256(path.read_bytes()).hexdigest()


def diagnostic_classes(codes, mapping):
    # La presencia del código cuenta; no interpretamos likelihood=0 como ausencia.
    # set evita contar dos veces una clase con varios códigos asociados.
    return sorted({mapping[code] for code in codes if code in mapping})


def main():
    rows, database_hash = read_metadata("ptbxl_database.csv")
    statements, statements_hash = read_metadata("scp_statements.csv")
    code_column = next(iter(statements[0]))
    mapping = {
        row[code_column]: row["diagnostic_class"]
        for row in statements
        if row["diagnostic"] and float(row["diagnostic"]) == 1
        and row["diagnostic_class"]
    }
    known_codes = {row[code_column] for row in statements}
    if not set(mapping.values()) <= set(CLASSES):
        raise ValueError("Se encontraron categorías diagnósticas no previstas")

    patient_folds = defaultdict(set)
    counts = Counter()
    records_per_patient = Counter()
    split_records = Counter()
    split_patients = defaultdict(set)
    label_counts = Counter()
    examples = []
    seen_ecgs = set()
    for row in rows:
        ecg_id = int(row["ecg_id"])
        if ecg_id in seen_ecgs:
            raise ValueError(f"Identificador ECG duplicado: {ecg_id}")
        seen_ecgs.add(ecg_id)
        patient = row["patient_id"]
        if not patient:
            raise ValueError("Registro sin identificador de paciente")
        fold = int(row["strat_fold"])
        if fold not in range(1, 11):
            raise ValueError(f"Partición inválida: {fold}")
        split = "train" if fold <= 8 else "validation" if fold == 9 else "test"
        codes = ast.literal_eval(row["scp_codes"])
        if not isinstance(codes, dict) or not set(codes) <= known_codes:
            raise ValueError(f"Códigos inválidos o desconocidos en ECG {ecg_id}")
        labels = diagnostic_classes(codes, mapping)
        counts.update(labels)
        label_counts[len(labels)] += 1
        patient_folds[patient].add(fold)
        records_per_patient[patient] += 1
        split_records[split] += 1
        split_patients[split].add(patient)
        if ecg_id in range(1, 6):
            examples.append({"ecg_id": ecg_id, "classes": labels,
                             "fold": fold, "split": split})

    # Cada paciente debe estar en un único fold oficial, incluso dentro de train.
    if any(len(folds) != 1 for folds in patient_folds.values()):
        raise ValueError("Un paciente aparece en más de un fold")
    if any(split_patients[a] & split_patients[b]
           for a, b in [("train", "validation"), ("train", "test"),
                        ("validation", "test")]):
        raise ValueError("Hay pacientes compartidos entre particiones")

    report = {
        "dataset": "PTB-XL 1.0.3",
        "sha256": {"ptbxl_database.csv": database_hash,
                   "scp_statements.csv": statements_hash},
        "label_policy": "Presencia de códigos diagnósticos; sin umbral de likelihood",
        "records": len(rows), "patients": len(patient_folds),
        "patients_with_multiple_records": sum(n > 1 for n in records_per_patient.values()),
        "class_counts": {key: counts[key] for key in CLASSES},
        "records_without_diagnostic_class": label_counts[0],
        "records_with_multiple_classes": sum(n for k, n in label_counts.items() if k > 1),
        "splits": {key: {"records": split_records[key],
                         "patients": len(split_patients[key])}
                   for key in ("train", "validation", "test")},
        "patient_overlap": False,
        "explored_examples": sorted(examples, key=lambda item: item["ecg_id"]),
    }
    output = ROOT / "reports" / "etiquetas_resumen.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")

    print(f"Registros: {len(rows)} | Pacientes: {len(patient_folds)}")
    print(f"Pacientes con varios registros: {report['patients_with_multiple_records']}")
    print("\nCategorías (pueden coexistir en un ECG):")
    for key, description in CLASSES.items():
        print(f"  {key:4}: {counts[key]:5} | {description}")
    print(f"Sin categoría diagnóstica: {label_counts[0]} (no significa normal)")
    print(f"Con varias categorías: {report['records_with_multiple_classes']}")
    print("\nNuestros cinco ejemplos:")
    for example in report["explored_examples"]:
        labels = ', '.join(example['classes']) or 'sin categoría diagnóstica'
        print(f"  ECG {example['ecg_id']:05}: {labels} | {example['split']}")
    print("\nParticiones oficiales:")
    for key, summary in report["splits"].items():
        print(f"  {key}: {summary['records']} ECG / {summary['patients']} pacientes")
    print("Comprobación: ningún paciente compartido entre folds.")
    print(f"Resumen guardado en: {output}")


if __name__ == "__main__":
    main()
