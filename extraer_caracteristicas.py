"""Características de amplitud de señales expresadas en mV."""

import numpy as np

def extraer_caracteristicas(ecg):
    """Resume una derivación; desviación estándar poblacional (ddof=0)."""
    ecg = np.asarray(ecg, dtype=float)
    if ecg.ndim != 1 or ecg.size == 0:
        raise ValueError("Se necesita una señal unidimensional no vacía")
    if not np.isfinite(ecg).all():
        raise ValueError("La señal contiene valores no finitos")
    return {
        "media_mv": float(np.mean(ecg)),
        "desviacion_estandar_mv": float(np.std(ecg)),
        "pico_a_pico_mv": float(np.max(ecg) - np.min(ecg))
    }

if __name__ == "__main__":
    from comparar_ecgs import load_record

    record = load_record("00001_lr")
    if any(unit != "mV" for unit in record.units):
        raise ValueError("Se necesitan todas las derivaciones en mV")
    channel = record.sig_name.index("II")
    ecg = record.p_signal[:, channel]

    caracteristicas = extraer_caracteristicas(ecg)

    for nombre, valor in caracteristicas.items():
        print(f"{nombre}: {valor:.4f}")
    ecg_desplazado = ecg + 1.0
    caracteristicas_desplazadas = extraer_caracteristicas(ecg_desplazado)

    print("\nComparación al sumar 1 mV:")

    for nombre in caracteristicas:
        original = caracteristicas[nombre]
        desplazado = caracteristicas_desplazadas[nombre]

        print(f"{nombre}: {original:.4f} -> {desplazado:.4f}")

    caracteristicas_ecg = {}

    for indice, derivacion in enumerate(record.sig_name):
        señal = record.p_signal[:, indice]
        caracteristicas_derivacion = extraer_caracteristicas(señal)

        for nombre, valor in caracteristicas_derivacion.items():
            nombre_completo = f"{derivacion}_{nombre}"
            caracteristicas_ecg[nombre_completo] = valor

    print("\nCaracterísticas de las 12 derivaciones:")

    for nombre, valor in caracteristicas_ecg.items():
        print(f"{nombre}: {valor:.4f}")

    print("Total:", len(caracteristicas_ecg))
