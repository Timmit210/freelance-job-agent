import tomllib
import unittest
from pathlib import Path

from agent.bewertung import FEST, GOLD, GUT, WEITER, bewerte
from agent.quellen import Job

CFG = tomllib.loads((Path(__file__).parent.parent / "config.toml").read_text())


def job(titel, text="", ort="", art=None):
    return bewerte(Job(id=titel, quelle="test", titel=titel, url="https://x", text=text, ort=ort, art=art), CFG)


class Bewertung(unittest.TestCase):
    def test_gold_freelance_pipeline_oldenburg(self):
        j = job("Freelance Videograf für Social Media", "Dreh, Schnitt und Posting unserer Reels", "Oldenburg")
        self.assertEqual(j.stufe, GOLD)

    def test_hamburg_noch_gold(self):
        j = job("Content Creator (freelance)", "Filmen, Editing, Community-Betreuung", "Hamburg")
        self.assertEqual(j.stufe, GOLD)

    def test_festanstellung(self):
        j = job("Content Creator (m/w/d) in Vollzeit", "Videos drehen für Instagram", "Bremen")
        self.assertEqual(j.stufe, FEST)

    def test_nrw_weiter_weg(self):
        j = job("Freelance Social Media Videograf", "Dreh und Schnitt", "Köln")
        self.assertEqual(j.stufe, WEITER)

    def test_teilpipeline_gut(self):
        j = job("Cutter für Social Media Videos gesucht", "Schnitt auf Projektbasis", "Bremen")
        self.assertEqual(j.stufe, GUT)

    def test_fremdes_thema_raus(self):
        self.assertIsNone(job("Java Entwickler", "Spring Boot", "Bremen"))

    def test_praktikum_raus(self):
        self.assertIsNone(job("Praktikum Social Media", "Instagram", "Bremen"))


if __name__ == "__main__":
    unittest.main()
