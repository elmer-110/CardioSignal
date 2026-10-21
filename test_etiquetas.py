"""Pruebas de la conversión de códigos a categorías diagnósticas."""

import unittest

from explorar_etiquetas import diagnostic_classes


class TestDiagnosticClasses(unittest.TestCase):
    def test_agrupa_codigos_sin_duplicar_categorias(self):
        # Dos códigos distintos pertenecen a CD; debe aparecer una sola vez.
        mapping = {
            "codigo_a": "CD",
            "codigo_b": "CD",
            "codigo_c": "MI",
        }
        codes = {
            "codigo_a": 100,
            "codigo_b": 100,
            "codigo_c": 100,
        }

        resultado = diagnostic_classes(codes, mapping)

        self.assertEqual(resultado, ["CD", "MI"])

    def test_codigo_sin_categoria_diagnostica(self):
        mapping = {"codigo_a": "CD"}
        codes = {"codigo_sin_categoria": 100}

        resultado = diagnostic_classes(codes, mapping)

        self.assertEqual(resultado, [])

    def test_conserva_codigo_con_confianza_cero(self):
        mapping = {"codigo_a": "CD"}
        codes = {"codigo_a": 0}

        resultado = diagnostic_classes(codes, mapping)

        self.assertEqual(resultado, ["CD"])


if __name__ == "__main__":
    unittest.main()
