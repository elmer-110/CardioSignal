import unittest
import numpy as np

from extraer_caracteristicas import extraer_caracteristicas


class TestExtraerCaracteristicas(unittest.TestCase):
    def test_calcula_valores_conocidos(self):
        señal=np.array([-1.0,0.0,1.0])

        resultado=extraer_caracteristicas(señal)

        self.assertEqual(resultado["media_mv"],0.0)
        self.assertAlmostEqual(
            resultado["desviacion_estandar_mv"],
            np.sqrt(2 / 3),
        )
        self.assertAlmostEqual(resultado["pico_a_pico_mv"], 2.0)


class TestCasosCaracteristicas(unittest.TestCase):
    def test_desplazamiento_constante_solo_cambia_media(self):
        señal = np.array([-0.2, 0.1, 0.7, -0.4])
        original = extraer_caracteristicas(señal)
        desplazada = extraer_caracteristicas(señal + 1.0)
        self.assertAlmostEqual(desplazada["media_mv"], original["media_mv"] + 1.0)
        for nombre in ("desviacion_estandar_mv", "pico_a_pico_mv"):
            self.assertAlmostEqual(desplazada[nombre], original[nombre])

    def test_senal_constante(self):
        self.assertEqual(extraer_caracteristicas([2.0, 2.0, 2.0]), {
            "media_mv": 2.0,
            "desviacion_estandar_mv": 0.0,
            "pico_a_pico_mv": 0.0,
        })

    def test_rechaza_entradas_invalidas(self):
        for señal in ([], 1.0, [[1.0, 2.0]], [0.0, np.nan],
                      [0.0, np.inf], [0.0, -np.inf]):
            with self.subTest(señal=señal):
                with self.assertRaises(ValueError):
                    extraer_caracteristicas(señal)


if __name__ == "__main__":
    unittest.main()
