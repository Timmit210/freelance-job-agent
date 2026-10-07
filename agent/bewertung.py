"""Bewertet Jobs nach Tims Kriterien: Freelance, ganze Pipeline, Nähe zu Bremen."""

from .orte import finde_ort, km

GOLD = "Gold"
GUT = "Gut"
FEST = "Festanstellung – anderes Modell vorschlagen"
WEITER = "Weiter weg"

NAMEN = {"dreh": "Dreh", "produktion": "Produktion", "posting": "Posting"}


def _hat(text, woerter):
    return [w for w in woerter if w in text]


def bewerte(job, cfg):
    sw = cfg["stichwoerter"]
    ent = cfg["entfernung"]
    heimat = (cfg["heimat"]["lat"], cfg["heimat"]["lon"])
    text = f"{job.titel} {job.text} {job.ort}".lower()

    if not _hat(text, sw["thema"]) or _hat(job.titel.lower(), sw["ausschluss"]):
        return None  # hat mit Social Media/Video nichts zu tun

    # Art der Stelle
    art = job.art
    if _hat(text, sw["freelance"]):
        art = "freelance"
    elif art is None and _hat(text, sw["fest"]):
        art = "fest"

    # Pipeline: Dreh, Produktion, Posting
    teile = [name for name in ("dreh", "produktion", "posting") if _hat(text, sw[name])]
    if "social media" in text and "posting" not in teile:
        teile.append("posting")

    # Entfernung
    koord = job.koord
    if koord is None:
        name, koord = finde_ort(f"{job.ort} {job.titel} {job.text}")
        if name and not job.ort:
            job.ort = name
    remote = bool(_hat(text, sw["remote"]))
    job.entfernung = round(km(heimat, koord)) if koord else None

    punkte = 0
    gruende = []
    if art == "freelance":
        punkte += 40
        gruende.append("Freelance")
    elif art == "fest":
        gruende.append("Festanstellung")
    punkte += 15 * len(teile)
    if len(teile) == 3:
        punkte += 15
        gruende.append("ganze Pipeline (Dreh, Produktion, Posting)")
    elif teile:
        gruende.append("Teil der Pipeline: " + ", ".join(NAMEN[t] for t in teile))

    d = job.entfernung
    if d is not None:
        if d <= ent["sehr_gut"]:
            punkte += 30
        elif d <= ent["gut"]:
            punkte += 15
        elif d > ent["noch_ok"]:
            punkte -= 30
        gruende.append(f"{d} km von {cfg['heimat']['name']}")
    elif remote:
        punkte += 10
        gruende.append("remote")
    else:
        gruende.append("Ort unklar")

    job.punkte = punkte
    job.gruende = gruende

    weit = d is not None and d > ent["noch_ok"] and not remote
    if art == "fest":
        job.stufe = WEITER if weit else FEST
    elif weit:
        job.stufe = WEITER
    elif art == "freelance" and len(teile) == 3 and (d is None or d <= ent["gut"]):
        job.stufe = GOLD
    else:
        job.stufe = GUT
    return job


REIHENFOLGE = [GOLD, GUT, FEST, WEITER]
