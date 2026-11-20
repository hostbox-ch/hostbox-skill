# HostBox-Skill: Webseite mit KI erstellen und veröffentlichen

Ein [Agent Skill](https://agentskills.io) für KI-Assistenten wie Claude, Claude Code, Codex oder Cursor. Der Skill begleitet einen Menschen von der Idee bis zur fertigen Webseite unter der eigenen Domain bei [HostBox](https://hostbox.ch), dem Schweizer Hosting für Webseiten und Anwendungen aus der KI.

**Ablauf:** nachfragen → Webseite bauen → auf GitHub ablegen → Hosting-Bestellung vorbereiten → der Mensch prüft und bezahlt → der Assistent prüft, ob alles online ist.

Bestellen, AGB akzeptieren und bezahlen macht immer der Mensch selbst. Der Assistent gibt ihm dafür einen Link. Kartendaten oder Passwörter fragt der Skill nie ab.

## Installation

**Claude Code** (als Plugin):

```
/plugin marketplace add hostbox-ch/hostbox-skill
/plugin install hostbox-webseite@hostbox
```

oder direkt als Skill:

```bash
curl -LO https://hostbox.ch/skills/hostbox-webseite.zip
unzip hostbox-webseite.zip -d ~/.claude/skills/
```

**Claude (App und Web):** [ZIP herunterladen](https://hostbox.ch/skills/hostbox-webseite.zip) und in den Einstellungen bei den Skills hochladen. Damit der Assistent selbst bestellen kann, in den Einstellungen zur Code-Ausführung die Domain `hostbox.ch` erlauben. Sonst erstellt er einen fertig ausgefüllten Bestell-Link.

**Andere Werkzeuge mit Agent Skills:** den Ordner [`skills/hostbox-webseite`](skills/hostbox-webseite) in den Skills-Ordner des Werkzeugs kopieren.

Voraussetzung: Python 3, ohne zusätzliche Pakete.

## Inhalt

| Datei | Zweck |
|---|---|
| [`skills/hostbox-webseite/SKILL.md`](skills/hostbox-webseite/SKILL.md) | Ablauf und Regeln für den Assistenten |
| [`scripts/hostbox.py`](skills/hostbox-webseite/scripts/hostbox.py) | Bestell-Link, Bestell-API, Status, Hostings, Ausrollen |
| [`references/API.md`](skills/hostbox-webseite/references/API.md) | Bestell-API und Parameter des Bestell-Links |
| [`references/HOSTING.md`](skills/hostbox-webseite/references/HOSTING.md) | Wie ein Projekt für HostBox aufgebaut sein muss |

Abholcode und Kunden-Token speichert das Skript in `.hostbox/` im Arbeitsordner (nur für den Benutzer lesbar, mit eigener `.gitignore`) und gibt sie nie aus.

## Ohne Skill

- Anfrage zum Kopieren für jeden Chat-Assistenten: <https://hostbox.ch/ratgeber/webseite-mit-ki-bestellen>
- Beschreibung für KI-Agenten: <https://hostbox.ch/llms.txt>
- REST-API (OpenAPI): <https://hostbox.ch/api/v1/openapi.json> · MCP-Server: `https://hostbox.ch/api/mcp`

## Fragen

<https://hostbox.ch/kontakt> · Lizenz: MIT
