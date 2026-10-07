# Tims Job-Agent

Schickt jeden Morgen eine Mail mit neuen Social-Media- und Video-Jobs, sortiert nach Tims Kriterien:

- **Gold:** Freelance mit der ganzen Pipeline (Dreh, Produktion, Posting), nicht weiter als Hamburg/Hannover
- **Gut:** passt teilweise oder liegt etwas weiter weg
- **Festanstellung – anderes Modell vorschlagen:** Content-Creator-Stellen als Festanstellung
- **Weiter weg:** z. B. NRW, nur zur Info

## Quellen

- Jobbörse der Bundesagentur für Arbeit (offizielle Schnittstelle, Umkreissuche um Bremen)
- dasauge (RSS-Feeds für Freelance und Festanstellung)

## Anpassen

Suchbegriffe, Entfernungen und Stichwörter stehen in `config.toml`.

## Technik

Läuft täglich als GitHub Action (`.github/workflows/job-agent.yml`). Schon gesehene Jobs merkt sich der Agent in `daten/gesehen.json`, damit nichts doppelt kommt.

Benötigte Secrets (Settings → Secrets and variables → Actions):
`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `MAIL_FROM`, `MAIL_TO`.

Lokal testen ohne Mailversand: `python -m agent --probe` (schreibt `vorschau.html`).
