"""Einmalige Diagnose: Welche Ordner gibt es, und wo liegen Mails der Job-Portale? Gibt nur Absender, Datum und Betreff aus."""

import email
import imaplib
import os
import re
import tomllib
from email.header import decode_header, make_header
from pathlib import Path

from .bewertung import bewerte
from .postfach import _html, jobs_aus_mail

cfg = tomllib.loads((Path(__file__).resolve().parent.parent / "config.toml").read_text())
host = os.environ.get("IMAP_HOST") or os.environ["SMTP_HOST"].replace("smtp.", "imap.", 1)
with imaplib.IMAP4_SSL(host) as imap:
    imap.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
    _, ordner = imap.list()
    for zeile in ordner:
        name = re.search(rb'"([^"]*)"$|(\S+)$', zeile)
        name = (name.group(1) or name.group(2)).decode()
        if imap.select(f'"{name}"', readonly=True)[0] != "OK":
            continue
        for portal in cfg["postfach"]["portale"]:
            _, d = imap.search(None, "FROM", f'"{portal["absender"]}"')
            nr = d[0].split()
            if not nr:
                continue
            print(f"[{name}] {portal['name']}: {len(nr)} Mails insgesamt, neueste:")
            for n in nr[-2:]:
                _, roh = imap.fetch(n, "(BODY.PEEK[HEADER.FIELDS (FROM DATE SUBJECT)])")
                h = email.message_from_bytes(roh[0][1])
                print("   ", h["Date"], "|", make_header(decode_header(h["From"] or "")), "|", str(make_header(decode_header(h["Subject"] or "")))[:80])
            # Was erkennt der Agent in der neuesten Mail?
            _, roh = imap.fetch(nr[-1], "(BODY.PEEK[])")
            for j in jobs_aus_mail(_html(email.message_from_bytes(roh[0][1])), portal)[:15]:
                b = bewerte(j, cfg)
                print(f"      -> {j.titel[:70]} | {j.text[:60]} | {b.stufe if b else 'aussortiert'}")
            if os.environ.get("DIAGNOSE_ROH") and portal["name"] == os.environ["DIAGNOSE_ROH"]:
                from html.parser import HTMLParser
                class Dump(HTMLParser):
                    def handle_starttag(self, tag, attrs):
                        if tag in ("a", "img"):
                            a = dict(attrs)
                            print(f"        <{tag} {(a.get('href') or a.get('alt') or '')[:90]}>")
                    def handle_data(self, data):
                        t = " ".join(data.split())
                        if t:
                            print("        " + t[:100])
                Dump().feed(_html(email.message_from_bytes(roh[0][1])))
