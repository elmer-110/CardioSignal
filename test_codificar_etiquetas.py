import unittest


from codificar_etiquetas import codificar_etiquetas

class TestCodificarEtiquetas(unittest.TestCase):
    def test_el_orden_de_las_clases_es_correcto(self):
        esperado = [0, 1, 1, 0, 0]
        self.assertEqual(
            codificar_etiquetas(["MI","STTC"]),
            esperado,
        )
        self.assertEqual(

            codificar_etiquetas(["STTC","MI"]),
            esperado,
        )
    def test_sin_etiquetas_devuelve_no_signfica_normal(self):
        resultado = codificar_etiquetas([])

        self.assertEqual(resultado,[0,0,0,0,0])
    def test_normal_ocupa_primera_columna(self):
        resultado= codificar_etiquetas(["NORM"])

        self.assertEqual(resultado,[1,0,0,0,0])
if __name__ == "__main__":
    unittest.main()
