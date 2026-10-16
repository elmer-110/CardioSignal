"""Práctica 3: comparar altura y prominencia ante un desplazamiento constante."""

import json

from comparar_ecgs import ROOT, load_record
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks


RECORD = "00004_lr"
OFFSET_MV = -1.0
THRESHOLD_MV = 0.2
MIN_DISTANCE_SECONDS = 0.4


def main():
    record = load_record(RECORD)
    channel = record.sig_name.index("II")
    signal = record.p_signal[:, channel]
    if record.units[channel] != "mV" or not np.isfinite(signal).all():
        raise ValueError("Se necesita una señal finita en mV")
    times = np.arange(len(signal)) / record.fs
    distance = max(1, int(MIN_DISTANCE_SECONDS * record.fs))
    conditions = [("Original", signal),
                  (f"Original {OFFSET_MV:+g} mV (simulado)", signal + OFFSET_MV)]
    fig, axes = plt.subplots(2, 2, figsize=(14, 7), sharex=True, sharey=True)
    report = {
        "record": RECORD, "lead": "II", "offset_mv": OFFSET_MV,
        "threshold_mv": THRESHOLD_MV,
        "min_distance_seconds": MIN_DISTANCE_SECONDS,
        "sampling_hz": float(record.fs), "detections": {},
        "limitation": "Desplazamiento constante; no simula deriva temporal ni valida picos R",
    }
    detections = {}
    for row, (condition, values) in enumerate(conditions):
        for col, (method, label) in enumerate(
                [("height", "Altura"), ("prominence", "Prominencia")]):
            peaks, _ = find_peaks(values, distance=distance,
                                 **{method: THRESHOLD_MV})
            detections[row, method] = peaks
            report["detections"][f"{row}_{method}"] = {
                "condition": condition, "count": len(peaks),
                "sample_indices": peaks.tolist(),
            }
            print(f"{condition} | {label}: {len(peaks)} picos candidatos")
            ax = axes[row, col]
            ax.plot(times, values, linewidth=0.9, color="#176b87")
            ax.scatter(times[peaks], values[peaks], color="#cc3333", s=22, zorder=3)
            if method == "height":
                ax.axhline(THRESHOLD_MV, color="#b56a00", linestyle="--",
                           label=f"Altura mínima: {THRESHOLD_MV:g} mV")
                ax.legend(fontsize=8, loc="lower left")
            ax.set_title(f"{condition}\n{label} ≥ {THRESHOLD_MV:g} mV: {len(peaks)} candidatos")
            ax.grid(alpha=0.2)
            if row == 1:
                ax.set_xlabel("Tiempo (s)")
            if col == 0:
                ax.set_ylabel("Amplitud (mV)")

    # Comparamos posiciones exactas, no solo el número de detecciones.
    same = bool(np.array_equal(detections[0, "prominence"],
                               detections[1, "prominence"]))
    report["same_prominence_peak_indices"] = same
    print(f"¿La prominencia conserva las mismas posiciones? {same}")
    fig.suptitle("Misma forma, distinto nivel respecto a cero · ECG 00004_lr", fontsize=14)
    fig.text(0.5, 0.015,
             "PTB-XL 1.0.3 / PhysioNet · CC BY 4.0 · "
             "Desplazamiento artificial: no es otro registro clínico",
             ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    (ROOT / "figures").mkdir(exist_ok=True)
    fig.savefig(ROOT / "figures" / "altura_prominencia.png", dpi=150)
    plt.close(fig)
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "altura_prominencia.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
