# HostBox Bestell-API und Bestell-Link

Vollständige Beschreibung: https://hostbox.ch/llms-full.txt · OpenAPI: https://hostbox.ch/api/v1/openapi.json

## Bestell-API (mit Internetzugang)

`POST https://hostbox.ch/api/v1/orders` (JSON, ohne Token für Neukunden)

| Feld | Werte | Standard |
|---|---|---|
| plan | site, app, studio | – (Pflicht) |
| interval | year, month | year |
| domain | z. B. meine-firma.ch | – (Pflicht) |
| domain_mode | existing, new | existing |
| database | none, mysql, postgresql | none |
| mailbox | Teil vor dem @, leer = keines | "" |
| git_url | https://github.com/… | "" |
| git_branch | Branch | main |
| setup | true = «Wir bringen es online» | false |
| customer | {name, email, company?} | Pflicht ohne Token |

Mit `Authorization: Bearer hbx_…` (Kunden-Token) entfällt `customer`; die Bestellung gehört dann zu diesem Konto.

Antwort `201`: `confirm_url` (für den Menschen, 7 Tage gültig), `claim_code` (hbo_…, geheim), `status_url`, `summary` (Preise), `next_steps`.

`GET https://hostbox.ch/api/v1/orders/status` mit `Authorization: Bearer hbo_…`, höchstens alle 20 Sekunden.

Status: `awaiting_confirmation` → `awaiting_payment` → `provisioning` → `active`; sonst `failed`, `cancelled`, `expired`. Nach der Zahlung einmalig `api_token` (hbx_…), wenn der Mensch es erlaubt hat.

Mit dem Kunden-Token: `GET /api/v1/services`, `GET /api/v1/jobs/{id}`, `POST /api/v1/services/{id}/deploy`, `/git`, `/databases`, `/mailboxes`, `/backups`. Dasselbe als MCP-Server: `https://hostbox.ch/api/mcp`.

Begrenzung: 10 Bestellentwürfe pro Stunde und IP.

## Bestell-Link (ohne Internetzugang)

```
https://hostbox.ch/bestellen?paket=site&intervall=jahr&domain=meine-firma.ch&domainart=vorhanden&git=https%3A%2F%2Fgithub.com%2Fname%2Fwebseite&name=Vorname%20Nachname&email=name%40example.ch
```

| Parameter | Werte |
|---|---|
| paket | site, app, studio |
| intervall | jahr, monat |
| domain | Domain |
| domainart | vorhanden, neu |
| datenbank | keine, mysql, postgresql |
| postfach | Teil vor dem @ |
| git | Repository-Adresse |
| branch | Branch (Standard main) |
| einrichtung | 1 = «Wir bringen es online» |
| name, firma, email | Angaben für das Kundenkonto |

Alle Werte URL-kodieren. Der Mensch prüft die Angaben, legt ein Passwort fest, akzeptiert die AGB und bezahlt.
