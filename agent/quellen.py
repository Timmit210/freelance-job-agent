"""Jobquellen. Jede Quelle liefert eine Liste von Job-Objekten."""

import html
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

USER_AGENT = "Mozilla/5.0 (compatible; tims-job-agent/1.0)"


@dataclass
class Job:
    id: str
    quelle: str
    titel: str
    url: str
    firma: str = ""
    ort: str = ""
    koord: tuple | None = None
    text: str = ""
    art: str | None = None  # "freelance", "fest" oder None (unklar)
    datum: str = ""
    # wird von der Bewertung gefüllt
    punkte: int = 0
    stufe: str = ""
    gruende: list = field(default_factory=list)
    entfernung: float | None = None


def _get(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def _ohne_html(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


# --- Jobbörse der Bundesagentur für Arbeit (offizielle, kostenlose Schnittstelle) ---

BA_URL = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs"
BA_KEY = "jobboerse-jobsuche"  # öffentlicher Schlüssel aus der Doku (jobsuche.api.bund.dev)


def arbeitsagentur(cfg, heimat):
    jobs = {}
    for begriff in cfg["suchbegriffe"]:
        for angebotsart, art in (("2", "freelance"), ("1", "fest")):
            params = {
                "was": begriff,
                "wo": heimat["name"],
                "umkreis": cfg["umkreis_km"],
                "angebotsart": angebotsart,
                "veroeffentlichtseit": cfg["tage"],
                "size": 100,
            }
            daten = json.loads(_get(f"{BA_URL}?{urllib.parse.urlencode(params)}", {"X-API-Key": BA_KEY}))
            for s in daten.get("stellenangebote") or []:
                refnr = s.get("refnr")
                if not refnr or refnr in jobs:
                    continue
                ort = s.get("arbeitsort") or {}
                k = ort.get("koordinaten") or {}
                jobs[refnr] = Job(
                    id=f"ba:{refnr}",
                    quelle="Arbeitsagentur",
                    titel=s.get("titel") or s.get("beruf") or "",
                    url=s.get("externeUrl") or f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{refnr}",
                    firma=s.get("arbeitgeber") or "",
                    ort=ort.get("ort") or "",
                    koord=(k["lat"], k["lon"]) if "lat" in k and "lon" in k else None,
                    text=s.get("beruf") or "",
                    art=art,
                    datum=s.get("aktuelleVeroeffentlichungsdatum") or "",
                )
    return list(jobs.values())


# --- RSS-Feeds (z. B. dasauge) ---

def rss(feeds, quelle):
    jobs = []
    for feed in feeds:
        root = ET.fromstring(_get(feed["url"]))
        for item in root.iter("item"):
            link = (item.findtext("link") or "").strip()
            titel = _ohne_html(item.findtext("title"))
            if not link or not titel:
                continue
            jobs.append(Job(
                id=f"{quelle.lower()}:{item.findtext('guid') or link}",
                quelle=quelle,
                titel=titel,
                url=link,
                text=_ohne_html(item.findtext("description")),
                art=feed.get("art"),
                datum=(item.findtext("pubDate") or "").strip(),
            ))
    return jobs
