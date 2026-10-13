"""Práctica 2: aplicar las mismas reglas a cinco ECG, sin evaluar precisión."""

import json
from urllib.request import urlopen

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import wfdb
from scipy.signal import find_peaks

from primer_ecg import ROOT, SOURCE


# Cinco registros por su orden de archivo, no una muestra representativa.
# No asumimos que pertenezcan a cinco pacientes distintos.
RECORDS = ["00001_lr", "00002_lr", "00003_lr", "00004_lr", "00005_lr"]
MIN_DISTANCE_SECONDS = 0.4
PROMINENCE_MV = 0.2


def load_record(name):
    """Descarga un registro de la primera carpeta de PTB-XL y lo reutiliza."""
    folder = ROOT / "data" / "sample"
    folder.mkdir(parents=True, exist_ok=True)
    for extension in ("hea", "dat"):
        destination = folder / f"{name}.{extension}"
        if not destination.exists():
            print(f"Descargando {destination.name}...", flush=True)
            with urlopen(f"{SOURCE}/{destination.name}", timeout=60) as response:
                content = response.read()
            temporary = destination.with_suffix(destination.suffix + ".tmp")
            temporary.write_bytes(content)
            temporary.replace(destination)
    return wfdb.rdrecord(str(folder / name))


def main():
    # Un eje por registro. La escala vertical es la misma para poder comparar.
    fig, axes = plt.subplots(len(RECORDS), 1, figsize=(13, 13),
                             sharex=True, sharey=True)
    results = []

    print("Registro    Picos   RR medio (s)   Frecuencia estimada (lat/min)")
    for name, ax in zip(RECORDS, axes):
        record = load_record(name)
        channel = record.sig_name.index("II")
        if record.units[channel] != "mV":
            raise ValueError(f"{name}: se esperaban amplitudes en mV")
        ecg = record.p_signal[:, channel]
        if not np.isfinite(ecg).all():
            raise ValueError(f"{name}: la señal contiene valores no finitos")
        times = np.arange(record.sig_len) / record.fs

        # Conservamos los mismos parámetros en todos los registros.
        peaks, _ = find_peaks(
            ecg,
            distance=max(1, int(MIN_DISTANCE_SECONDS * record.fs)),
            prominence=PROMINENCE_MV,
        )
        peak_times = times[peaks]
        rr = np.diff(peak_times)
        mean_rr = float(np.mean(rr)) if len(rr) else None
        heart_rate = 60 / mean_rr if mean_rr is not None else None

        result = {
            "record": name,
            "lead": "II",
            "sampling_hz": float(record.fs),
            "duration_seconds": float(record.sig_len / record.fs),
            "candidate_peaks": int(len(peaks)),
            "peak_times_seconds": np.round(peak_times, 6).tolist(),
            "rr_seconds": np.round(rr, 6).tolist(),
            "mean_rr_seconds": mean_rr,
            "estimated_bpm": heart_rate,
            "min_rr_seconds": float(np.min(rr)) if len(rr) else None,
            "max_rr_seconds": float(np.max(rr)) if len(rr) else None,
        }
        results.append(result)

        if mean_rr is None:
            summary = "No hay suficientes picos"
            print(f"{name:10} {len(peaks):5}   no calculable")
        else:
            summary = f"{len(peaks)} candidatos | estimación: {heart_rate:.1f} lat/min"
            print(f"{name:10} {len(peaks):5}   {mean_rr:12.3f}   {heart_rate:10.1f}")

        ax.plot(times, ecg, color="#176b87", linewidth=0.8)
        ax.scatter(peak_times, ecg[peaks], color="#cc3333", s=20,
                   zorder=3, label="Picos candidatos")
        ax.set_title(f"{name} · {summary}", fontsize=11, loc="left")
        ax.set_ylabel("mV")
        ax.grid(alpha=0.2)

    axes[0].legend(loc="upper right")
    axes[-1].set_xlabel("Tiempo (s)")
    fig.suptitle("Mismas reglas, cinco ECG · derivación II", fontsize=16)
    fig.text(0.5, 0.012,
             "Fuente: PTB-XL 1.0.3 / PhysioNet · CC BY 4.0 · "
             "Exploración sin anotaciones de referencia de picos",
             ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.035, 1, 0.97))
    figure_dir = ROOT / "figures"
    figure_dir.mkdir(exist_ok=True)
    fig.savefig(figure_dir / "comparacion_ecgs.png", dpi=150)
    plt.close(fig)

    report_dir = ROOT / "reports"
    report_dir.mkdir(exist_ok=True)
    report = {
        "dataset": "PTB-XL 1.0.3",
        "selection": "Cinco registros consecutivos; selección no representativa",
        "parameters": {"min_distance_seconds": MIN_DISTANCE_SECONDS,
                       "prominence_mv": PROMINENCE_MV},
        "limitation": "Sin referencia de picos: no se mide precisión ni se diagnostica",
        "records": results,
    }
    (report_dir / "comparacion_ecgs.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print("\nGráfico: figures/comparacion_ecgs.png")
    print("Resumen: reports/comparacion_ecgs.json")
    print("Las frecuencias dependen de las detecciones: revisa cada punto rojo.")


if __name__ == "__main__":
    main()
