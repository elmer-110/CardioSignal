"""Primera práctica: descargar un ECG de PTB-XL y visualizar la derivación II."""

from pathlib import Path
from urllib.request import urlopen
from scipy.signal import find_peaks

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import wfdb


ROOT = Path(__file__).resolve().parent
SOURCE = "https://physionet.org/files/ptb-xl/1.0.3/records100/00000"
RECORD = "00001_lr"


def main():
    # Un registro consta de una cabecera (.hea) y las muestras (.dat).
    data_dir = ROOT / "data" / "sample"
    data_dir.mkdir(parents=True, exist_ok=True)
    for suffix in ("hea", "dat"):
        destination = data_dir / f"{RECORD}.{suffix}"
        if not destination.exists():
            print(f"Descargando {destination.name}...")
            with urlopen(f"{SOURCE}/{destination.name}", timeout=60) as response:
                content = response.read()
            temporary = destination.with_suffix(destination.suffix + ".tmp")
            temporary.write_bytes(content)
            temporary.replace(destination)

    record = wfdb.rdrecord(str(data_dir / RECORD))
    # p_signal contiene valores físicos, convertidos usando la cabecera.
    signals = record.p_signal
    channel = record.sig_name.index("II")
    # Cada muestra está separada de la siguiente por 1/fs segundos.
    time_seconds = np.arange(record.sig_len) / record.fs

    print("Primeros cinco tiempos:", time_seconds[:5])
    print("Primeras cinco amplitudes:", signals[:5, channel])

    print(f"Forma de los datos (muestras, derivaciones): {signals.shape}")
    print(f"Frecuencia de muestreo: {record.fs:g} Hz")
    print(f"Duración del registro: {record.sig_len / record.fs:g} s")
    print(f"Derivaciones: {', '.join(record.sig_name)}")
    print(f"Unidad de la derivación II: {record.units[channel]}")


    # Medición manual aproximada realizada en el primer ejercicio.
    t1 = 0.2
    t2 = 1.125

    rr = t2 - t1
    frecuencia_cardiaca = 60 / rr

    print(f"Intervalo RR: {rr:.3f} s")
    print(f"Frecuencia estimada:{frecuencia_cardiaca:.1f} latidos/min")

    #seleccionamos la derivación II para graficar
    ecg = signals[:, channel]


    #buscamos max separados al menos 0,4 s y prominencia de 0,2 mV

    peaks, _ = find_peaks(
        ecg,
        distance=int(0.4 * record.fs),
        prominence=0.2,
    )

    # Convertimos las posiciones de los picos a segundos.

    peak_times = time_seconds[peaks]
    rr_intervals = np.diff(peak_times)
    print("tiempos de los picos detectados:",peak_times)

    if len(rr_intervals) > 0:
        mean_rr = np.mean(rr_intervals)
        estimated_hr = 60 / mean_rr
        print(f"RR medio :{mean_rr:.3f}s")
        print(f"Frecuencia automática:{estimated_hr:.1f} latidos/min")
        print("Número de picos:", len(peaks))
        print("Intervalos RR (s):", np.round(rr_intervals, 3))
        print(f"RR más corto: {np.min(rr_intervals):.3f} s")
        print(f"RR más largo: {np.max(rr_intervals):.3f} s")

    else:
        print("no hay suficientes picos para la frecuencia.")

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(time_seconds, signals[:, channel], linewidth=0.9, color="#176b87")
    ax.scatter(peak_times,
               ecg[peaks],
               color="red",
               label="Picos candidatos",
               zorder=3,
               )
    ax.legend()

    ax.set(title="Primer ECG real · PTB-XL · derivación II",
           xlabel="Tiempo (s)", ylabel=f"Amplitud ({record.units[channel]})")
    ax.grid(alpha=0.25)
    ax.set_xlim(0,10)
    fig.text(0.5, 0.01, "Fuente: PTB-XL 1.0.3 / PhysioNet · CC BY 4.0 · Registro 00001_lr",
             ha="center", fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    figures_dir = ROOT / "figures"
    figures_dir.mkdir(exist_ok=True)
    output = figures_dir / "primer_ecg.png"
    fig.savefig(output, dpi=160)
    plt.close(fig)
    print(f"Gráfico guardado en: {output}")


    # Un punto por cada intervalo entre picos consecutivos.
    if len(rr_intervals) > 0:
        fig_rr, ax_rr = plt.subplots(figsize=(10, 4))

        interval_numbers = np.arange(1, len(rr_intervals) + 1)

        ax_rr.plot(interval_numbers, rr_intervals, "o-")
        ax_rr.axhline(
            np.mean(rr_intervals),
            color="orange",
            linestyle="--",
            label="RR medio",
        )

        ax_rr.set(
            xlabel="Número de intervalo",
            ylabel="Intervalo RR (s)",
            title="Separación temporal entre los picos detectados",
        )
        ax_rr.set_xticks(interval_numbers)
        ax_rr.grid(alpha=0.25)
        ax_rr.legend()

        fig_rr.tight_layout()
        fig_rr.savefig(figures_dir / "intervalos_rr.png", dpi=160)
        plt.close(fig_rr)

if __name__ == "__main__":
    main()
