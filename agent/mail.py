"""Baut die Morgen-Mail und verschickt sie per SMTP."""

import html
import os
import smtplib
import ssl
from datetime import date
from email.message import EmailMessage
from email.utils import formataddr

from .bewertung import FEST, GOLD, GUT, REIHENFOLGE, WEITER

# (Akzent, Hintergrund, Symbol) pro Kategorie
STIL = {
    GOLD: ("#b8860b", "#fff6d6", "🥇"),
    GUT: ("#1e8e3e", "#e6f4ea", "✅"),
    FEST: ("#1a73e8", "#e8f0fe", "💼"),
    WEITER: ("#80868b", "#f1f3f4", "🚗"),
}


def baue_html(jobs):
    e = html.escape
    teile = ['<div style="font-family:-apple-system,Segoe UI,Arial,sans-serif;max-width:640px;color:#222">']

    # Übersicht oben: farbige Kästchen mit Anzahl je Kategorie
    teile.append('<table role="presentation" style="border-collapse:separate;border-spacing:6px;margin:0 -6px 8px"><tr>')
    for stufe in REIHENFOLGE:
        n = sum(j.stufe == stufe for j in jobs)
        akzent, hg, symbol = STIL[stufe]
        kurz = stufe.split(" – ")[0]
        teile.append(f'<td style="background:{hg};border-radius:8px;padding:8px 10px;text-align:center;font-size:13px;color:{akzent}">'
                     f'<div style="font-size:20px;font-weight:700">{n}</div>{symbol} {e(kurz)}</td>')
    teile.append('</tr></table>')

    for stufe in REIHENFOLGE:
        gruppe = [j for j in jobs if j.stufe == stufe]
        if not gruppe:
            continue
        akzent, hg, symbol = STIL[stufe]
        teile.append(f'<h2 style="color:{akzent};font-size:18px;margin:24px 0 8px">{symbol} {e(stufe)} ({len(gruppe)})</h2>')
        for j in gruppe:
            meta = " · ".join(x for x in (j.firma, j.ort, j.quelle) if x)
            teile.append(
                f'<div style="background:{hg};border-left:4px solid {akzent};border-radius:6px;padding:10px 12px;margin:0 0 10px">'
                f'<a href="{e(j.url)}" style="font-size:16px;font-weight:600;color:#0b57d0;text-decoration:none">{e(j.titel)}</a>'
                f'<div style="font-size:13px;color:#555;margin-top:2px">{e(meta)}</div>'
                f'<div style="font-size:14px;margin-top:4px">{e(" · ".join(j.gruende))}</div></div>'
            )
    teile.append('<p style="font-size:12px;color:#888;margin-top:32px">Automatisch verschickt von deinem Job-Agenten '
                 '(github.com/Timmit210/freelance-job-agent).</p></div>')
    return "\n".join(teile)


def baue_text(jobs):
    zeilen = []
    for stufe in REIHENFOLGE:
        gruppe = [j for j in jobs if j.stufe == stufe]
        if gruppe:
            zeilen.append(f"\n== {stufe} ({len(gruppe)}) ==")
            for j in gruppe:
                zeilen.append(f"- {j.titel} ({', '.join(x for x in (j.firma, j.ort) if x)})\n  {' · '.join(j.gruende)}\n  {j.url}")
    return "\n".join(zeilen).strip()


def betreff(jobs, cfg):
    gold = sum(j.stufe == GOLD for j in jobs)
    teil = f"{len(jobs)} neue Treffer" + (f", davon {gold} Gold" if gold else "")
    return f"{cfg['mail']['betreff_prefix']}: {teil} ({date.today():%d.%m.})"


def sende(jobs, cfg):
    msg = EmailMessage()
    msg["Subject"] = betreff(jobs, cfg)
    msg["From"] = formataddr((cfg["mail"]["absender_name"], os.environ["MAIL_FROM"]))
    msg["To"] = os.environ["MAIL_TO"]
    msg.set_content(baue_text(jobs))
    msg.add_alternative(baue_html(jobs), subtype="html")

    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT") or "465")
    ctx = ssl.create_default_context()
    if port == 465:
        server = smtplib.SMTP_SSL(host, port, context=ctx, timeout=30)
    else:
        server = smtplib.SMTP(host, port, timeout=30)
        server.starttls(context=ctx)
    with server:
        server.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        server.send_message(msg)
