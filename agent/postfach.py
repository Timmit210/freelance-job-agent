"""Liest Job-Benachrichtigungen der Portale aus dem Postfach (nur lesen, Mails bleiben ungelesen)."""

import email
import imaplib
import os
import re
from datetime import date, timedelta
from email.header import decode_header, make_header
from html.parser import HTMLParser

from .quellen import Job

# Floskel-Links, die keine Jobs sind
RAUSCHEN = re.compile(
    r"abmelden|unsubscribe|einstellungen|datenschutz|impressum|alle (jobs|projekte|ergebnisse)|"
    r"mehr (jobs|anzeigen)|\bapp\b|profil|hilfe|kontakt|agb|newsletter|suche (bearbeiten|ändern)|login|anmelden",
    re.I,
)


class _Links(HTMLParser):
    """Sammelt Links mit ihrem Text und dem Text, der direkt danach folgt (Firma, Ort ...)."""

    def __init__(self):
        super().__init__()
        self.links = []  # [href, titel, kontext]
        self._href = None
        self._text = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append([self._href, " ".join(self._text).strip(), ""])
            self._href = None

    def handle_data(self, data):
        t = re.sub(r"\s+", " ", data).strip()
        if not t:
            return
        if self._href is not None:
            self._text.append(t)
        elif self.links and len(self.links[-1][2]) < 200:
            self.links[-1][2] += " " + t


def _html(msg):
    for teil in msg.walk():
        if teil.get_content_type() == "text/html":
            return teil.get_payload(decode=True).decode(teil.get_content_charset() or "utf-8", "replace")
    return ""


def jobs_aus_mail(html_text, portal, muster=None, min_laenge=8):
    p = _Links()
    p.feed(html_text)
    jobs, gesehen = [], set()
    muster = re.compile(muster or portal["link"], re.I)
    for href, titel, kontext in p.links:
        if not href or not muster.search(href) or len(titel) < min_laenge or RAUSCHEN.search(titel):
            continue
        schluessel = titel.lower()
        if schluessel in gesehen:
            continue
        gesehen.add(schluessel)
        jobs.append(Job(
            id=f"{portal['name'].lower()}:{schluessel}",
            quelle=portal["name"],
            titel=titel,
            url=href,
            text=kontext.strip(),
        ))
    if not jobs and muster.pattern != "^http":
        # Links laufen oft über Klick-Zähler mit fremder Adresse: dann alle längeren Linktexte nehmen
        return jobs_aus_mail(html_text, portal, "^http", 20)
    return jobs


def postfach(cfg):
    host = os.environ.get("IMAP_HOST") or os.environ["SMTP_HOST"].replace("smtp.", "imap.", 1)
    seit = (date.today() - timedelta(days=cfg["tage"])).strftime("%d-%b-%Y")
    jobs = []
    with imaplib.IMAP4_SSL(host) as imap:
        imap.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        imap.select("INBOX", readonly=True)
        for portal in cfg["portale"]:
            _, daten = imap.search(None, "SINCE", seit, "FROM", f'"{portal["absender"]}"')
            nummern = daten[0].split()
            neu = 0
            for nr in nummern:
                _, roh = imap.fetch(nr, "(BODY.PEEK[])")
                msg = email.message_from_bytes(roh[0][1])
                gefunden = jobs_aus_mail(_html(msg), portal)
                if not gefunden:
                    print(f"  {portal['name']}: keine Jobs erkannt in Mail „{make_header(decode_header(msg.get('Subject', '')))}“")
                jobs += gefunden
                neu += len(gefunden)
            print(f"  {portal['name']}: {len(nummern)} Mails, {neu} Jobs")
    return jobs
