"""Codificación multietiqueta con un orden fijo de columnas."""

CLASES = ["NORM", "MI", "STTC", "CD", "HYP"]

def codificar_etiquetas(etiquetas):
    etiquetas = set(etiquetas)
    desconocidas = etiquetas - set(CLASES)
    if desconocidas:
        raise ValueError(f"Categorías desconocidas: {sorted(desconocidas)}")

    resultado = []
    for categoria in CLASES:
        if categoria in etiquetas:
            resultado.append(1)
        else:
            resultado.append(0)
    return resultado


if __name__ == "__main__":
    ejemplo = ["MI", "STTC"]
    print(codificar_etiquetas(ejemplo))
