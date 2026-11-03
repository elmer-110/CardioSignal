"""Pruebas de integración de códigos diagnósticos y vectores multietiqueta."""

import unittest

from codificar_etiquetas import codificar_etiquetas
from explorar_etiquetas import preparar_objetivo


class TestPrepararObjetivos(unittest.TestCase):
    def test_codigos_a_vector_multietiqueta(self):
        # Códigos ficticios: dos clases, un duplicado y un código no diagnóstico.
        mapping = {"a": "MI", "b": "STTC", "c": "MI"}
        codes = {"a": 0, "b": 100, "c": 50, "ritmo": 0}
        self.assertEqual(preparar_objetivo(codes, mapping), [0, 1, 1, 0, 0])

    def test_excluye_sin_categoria_pero_conserva_normal(self):
        mapping = {"normal": "NORM"}
        self.assertIsNone(preparar_objetivo({"ritmo": 0}, mapping))
        self.assertIsNone(preparar_objetivo({}, mapping))
        self.assertEqual(preparar_objetivo({"normal": 100}, mapping),
                         [1, 0, 0, 0, 0])

    def test_rechaza_categoria_desconocida(self):
        # Evita convertir una errata en un vector de ceros silenciosamente.
        with self.assertRaises(ValueError):
            codificar_etiquetas(["NORRM"])


if __name__ == "__main__":
    unittest.main()
