"""Einstiegspunkt: python -m agent [--probe | --aufraeumen]

Sammelt neue Jobs, bewertet sie und schickt eine Mail.
--probe: nichts verschicken, nichts merken, sondern die Mail als vorschau.html speichern.
--aufraeumen: nur die Portal-Mails aus dem Posteingang in den Job-Alerts-Ordner schieben.
"""

import json
import os
import sys
import tomllib
import traceback
from pathlib import Path

from . import postfach, quellen
from .bewertung import REIHENFOLGE, bewerte
from .mail import baue_html, betreff, sende

ROOT = Path(__file__).resolve().parent.parent
GESEHEN = ROOT / "daten" / "gesehen.json"


def sammle(cfg, probe=False):
    jobs, fehler = [], []
    laeufe = [
        ("Arbeitsagentur", lambda: quellen.arbeitsagentur(cfg["arbeitsagentur"], cfg["heimat"])),
        ("dasauge", lambda: quellen.rss(cfg["dasauge"]["feeds"], "dasauge")),
        ("Postfach", lambda: postfach.postfach(cfg["postfach"], aufraeumen=not probe)),
    ]
    for name, lauf in laeufe:
        try:
            neu = lauf()
            print(f"{name}: {len(neu)} Einträge")
            jobs += neu
        except Exception:
            traceback.print_exc()
            fehler.append(name)
    return jobs, fehler


def main():
    probe = "--probe" in sys.argv
    if "--aufraeumen" in sys.argv:
        cfg = tomllib.loads((ROOT / "config.toml").read_text())
        postfach.postfach(cfg["postfach"])
        return
    cfg = tomllib.loads((ROOT / "config.toml").read_text())
    gesehen = set(json.loads(GESEHEN.read_text())) if GESEHEN.exists() else set()

    jobs, fehler = sammle(cfg, probe)
    neu = [j for j in jobs if j.id not in gesehen]
    treffer = [j for j in (bewerte(j, cfg) for j in neu) if j]
    treffer.sort(key=lambda j: (REIHENFOLGE.index(j.stufe), -j.punkte))
    print(f"{len(neu)} neu, {len(treffer)} passend")

    if probe:
        (ROOT / "vorschau.html").write_text(f"<h1>{betreff(treffer, cfg)}</h1>" + baue_html(treffer))
        print("Vorschau gespeichert: vorschau.html")
        return
    if treffer and not os.environ.get("SMTP_HOST"):
        sys.exit("Mail-Zugang fehlt: bitte die SMTP-Secrets im Repository eintragen (siehe README).")
    if treffer:
        sende(treffer, cfg)
        print("Mail verschickt")
    GESEHEN.parent.mkdir(exist_ok=True)
    GESEHEN.write_text(json.dumps(sorted(gesehen | {j.id for j in jobs}), indent=0))
    if fehler and not jobs:
        sys.exit(f"Alle Quellen fehlgeschlagen: {', '.join(fehler)}")


if __name__ == "__main__":
    main()
