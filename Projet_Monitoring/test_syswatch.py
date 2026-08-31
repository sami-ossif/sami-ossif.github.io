"""Tests unitaires de SysWatch (executables avec `python -m unittest`).

Ces tests couvrent la logique pure (analyse des ports, formatage) et le
comportement reseau via un petit serveur TCP local ephemere, sans dependance
externe.
"""

import socket
import threading
import unittest

import syswatch


class TestParsingPorts(unittest.TestCase):
    def test_port_unique(self):
        self.assertEqual(syswatch.parser_plage_ports("80"), [80])

    def test_plage(self):
        self.assertEqual(syswatch.parser_plage_ports("20-22"), [20, 21, 22])

    def test_liste(self):
        self.assertEqual(syswatch.parser_plage_ports("443,22,80"), [22, 80, 443])

    def test_plage_inversee(self):
        self.assertEqual(syswatch.parser_plage_ports("22-20"), [20, 21, 22])

    def test_dedoublonnage(self):
        self.assertEqual(syswatch.parser_plage_ports("80,80,80"), [80])

    def test_hors_intervalle(self):
        with self.assertRaises(ValueError):
            syswatch.parser_plage_ports("70000")


class TestFormatageOctets(unittest.TestCase):
    def test_octets(self):
        self.assertEqual(syswatch.formater_octets(512), "512.0 o")

    def test_kilo(self):
        self.assertEqual(syswatch.formater_octets(2048), "2.0 Ko")

    def test_giga(self):
        self.assertEqual(syswatch.formater_octets(3 * 1024 ** 3), "3.0 Go")


class TestTesterPort(unittest.TestCase):
    """Verifie tester_port contre un vrai serveur TCP local ephemere."""

    @classmethod
    def setUpClass(cls):
        cls.serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cls.serveur.bind(("127.0.0.1", 0))  # port libre attribue par l'OS
        cls.serveur.listen(1)
        cls.port = cls.serveur.getsockname()[1]

        def _accepter():
            while True:
                try:
                    conn, _ = cls.serveur.accept()
                    conn.close()
                except OSError:
                    break

        cls.thread = threading.Thread(target=_accepter, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.serveur.close()

    def test_port_ouvert(self):
        ouvert, latence = syswatch.tester_port("127.0.0.1", self.port, timeout=1.0)
        self.assertTrue(ouvert)
        self.assertIsNotNone(latence)

    def test_port_ferme(self):
        # Port tres probablement ferme sur la boucle locale.
        ouvert, latence = syswatch.tester_port("127.0.0.1", 1, timeout=0.5)
        self.assertFalse(ouvert)
        self.assertIsNone(latence)


if __name__ == "__main__":
    unittest.main()
