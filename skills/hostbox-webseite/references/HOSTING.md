<!-- Erzeugt aus web/src/lib/guide.ts – dort ändern, dann npm run skill:build -->
# HostBox – Projekt-Leitfaden für KI-Agenten

## Laufzeiten
- Statisch (HTML/CSS/JS): Dateien landen im Zielordner (Standard: httpdocs). Bei Build-Tools (Vite, Astro) das Build-Ergebnis (dist/) deployen oder den Zielordner auf dist setzen.
- PHP 8 (derzeit 8.4, wird aktuell gehalten): index.php im Zielordner. Composer-Abhängigkeiten committen oder per Deploy-Aktion installieren.
- Node.js (ab Box App): package.json mit "start"-Skript. Die App muss auf process.env.PORT hören. Startdatei z. B. server.js oder .next/standalone/server.js.
- Python 3 (ab Box App): requirements.txt und eine WSGI/ASGI-App (app.py mit Variable "app").

## Deployment
- Git: Repository im Portal verbinden. Jeder Push auf den Branch wird ausgerollt (Webhook bei GitHub/GitLab hinterlegen).
- Keine Geheimnisse ins Repository. Zugangsdaten (Datenbank, SMTP) als Umgebungsvariablen bzw. in einer nicht versionierten .env auf dem Server.

## Datenbank
- MySQL/MariaDB (Port 3306) oder PostgreSQL (Port 5432, ab Box App), Host "localhost".
- Zugangsdaten im Portal unter Zugangsdaten; per Werkzeug create_database neue anlegen.

## E-Mail aus Formularen
- SMTP: mail.<domain>, Port 465 (SSL) oder 587 (STARTTLS), Benutzer = volle Postfach-Adresse.
- Absender immer eine Adresse der eigenen Domain verwenden.

## Prüfen
- Nach dem Deployment get_job und get_service abfragen. Status "done" heisst ausgerollt.

Mehr: https://hostbox.ch/anleitungen
