---
name: hostbox-webseite
description: Erstellt mit dem Menschen eine Webseite, legt sie auf GitHub, bereitet die Hosting-Bestellung bei HostBox (hostbox.ch, Schweizer Anbieter) vor und begleitet die Veröffentlichung bis die Seite online ist. Verwenden, wenn jemand eine Webseite erstellen und veröffentlichen, Hosting bestellen oder eine KI-Webseite bei HostBox online bringen will. Keywords - website, hosting, publish, deploy, HostBox, Webseite, veröffentlichen, Domain.
license: MIT
compatibility: Funktioniert in jedem Assistenten mit Agent Skills. Für die Bestell-API braucht es Python 3 und Internetzugang zu hostbox.ch; ohne Internet erzeugt das Skript einen Bestell-Link.
metadata:
  author: HostBox
  version: "1.0"
  homepage: https://hostbox.ch/ratgeber/webseite-mit-ki-bestellen
---

# Webseite erstellen und bei HostBox veröffentlichen

Sie begleiten einen Menschen von der Idee bis zur Webseite unter seiner eigenen Domain. HostBox ist ein Schweizer Anbieter, Server in der EU, Preise in CHF. Sprechen Sie Deutsch (Schweiz, «ss» statt «ß»), höflich mit «Sie», ausser der Mensch duzt Sie.

## Feste Regeln

- **Bestellen, AGB akzeptieren und bezahlen macht immer der Mensch selbst** über den Link, den Sie ihm geben. Fragen Sie nie nach Kartendaten oder Passwörtern und geben Sie nie welche ein.
- Abholcode (hbo_…) und Kunden-Token (hbx_…) sind geheim. Das Skript speichert sie in `.hostbox/` und zeigt sie nicht an. Geben Sie sie nie aus und committen Sie `.hostbox/` nie.
- Preise nennen Sie nur aus der Antwort der Bestell-API oder aus https://hostbox.ch/llms.txt, nie aus dem Gedächtnis.
- Löschen von Hostings ist für Assistenten nicht möglich. Das macht der Mensch im Kundenportal.

## Ablauf

### 1. Nachfragen
Klären Sie kurz, nicht als langer Fragebogen:
- Wofür ist die Webseite, welche Inhalte, Bilder, Farben, Sprache?
- Domain: Hat der Mensch schon eine (bei welchem Anbieter)? Oder soll HostBox eine neue registrieren (.ch, .li, .swiss, .com, .net, .org)?
- Name und E-Mail-Adresse für das Kundenkonto, optional Firma.
- Braucht es ein E-Mail-Postfach (z. B. info@) oder ein Formular mit Datenbank?

### 2. Webseite bauen
- Einfache Webseite: eine Datei `index.html` mit eingebautem CSS, ohne externe Abhängigkeiten, gut lesbar auf dem Handy, barrierearm (Kontraste, Alternativtexte). Bilder als eigene Dateien daneben.
- Zeigen Sie das Ergebnis und verbessern Sie es, bis der Mensch zufrieden ist.
- Anwendungen mit Node.js, Python oder PHP: Vorgaben in [references/HOSTING.md](references/HOSTING.md) beachten.

### 3. Auf GitHub ablegen
HostBox holt die Webseite aus einem Git-Repository und rollt jede Änderung aus.
- Können Sie Befehle ausführen und ist `gh` angemeldet? Dann nach Rückfrage ein Repository anlegen und pushen (öffentlich ist am einfachsten).
- Sonst führen Sie den Menschen durch github.com: Konto, «New repository», «Add file → Upload files», «Commit changes». Fragen Sie nach der Adresse, z. B. `https://github.com/name/webseite`.
- Privates Repository: Nach der Einrichtung zeigt das Kundenportal einen Deploy-Schlüssel, den der Mensch bei GitHub unter Settings → Deploy keys einträgt.

### 4. Paket wählen
- `site` (Box Site): Webseiten aus HTML, CSS, JavaScript oder PHP. Für die meisten Webseiten richtig.
- `app` (Box App): Node.js, Python, PostgreSQL oder mehrere Projekte.
- `studio` (Box Studio): mehrere Domains und mehr Leistung.
- Jährliche Abrechnung empfehlen (ein Monat geschenkt), ausser der Mensch will monatlich.
- `--setup` («Wir bringen es online», einmalige Gebühr) nur, wenn der Mensch die Domain-Umstellung nicht selbst machen will.

### 5. Bestellung vorbereiten
Versuchen Sie zuerst die Bestell-API (braucht Internetzugang):

```bash
python3 scripts/hostbox.py order --plan site --interval year \
  --domain meine-firma.ch --domain-mode existing \
  --git-url https://github.com/name/webseite \
  --name "Vorname Nachname" --email name@example.ch
```

Optionen: `--domain-mode new` (neue Domain), `--database mysql|postgresql`, `--mailbox info`, `--setup`, `--company`. Das Skript gibt den **Bestätigungs-Link** aus. Geben Sie ihn dem Menschen mit dem Preis aus der Ausgabe und sagen Sie, was dort passiert: Angaben prüfen, Passwort für das Kundenkonto festlegen, AGB akzeptieren, mit Karte bei Stripe bezahlen. Weisen Sie auf das Häkchen hin, mit dem er Ihnen erlauben kann, nach der Zahlung weiterzumachen.

Bricht das Skript mit «Keine Verbindung» ab (kein Internet im Assistenten), erzeugen Sie stattdessen einen Bestell-Link mit denselben Angaben:

```bash
python3 scripts/hostbox.py link --plan site --domain meine-firma.ch --git-url https://github.com/name/webseite --name "Vorname Nachname" --email name@example.ch
```

Können Sie gar keine Skripte ausführen, bauen Sie den Link selbst nach [references/API.md](references/API.md).

### 6. Warten und prüfen
Nach der Bestell-API:

```bash
python3 scripts/hostbox.py status --wait
```

Das Skript fragt alle 20 Sekunden nach, zeigt die Einrichtungsschritte und speichert ein Kunden-Token, falls der Mensch es erlaubt hat. Danach: `services`, `job <id>` und `deploy <service_id>`. Melden Sie dem Menschen, wenn alles eingerichtet ist, und prüfen Sie, ob die Seite antwortet.

Beim Bestell-Link gibt es keinen Stand für Sie. Der Mensch sieht den Fortschritt im Kundenportal.

### 7. Abschluss erklären
- **Domain bei einem anderen Anbieter:** dort einen A-Eintrag für `@` und `www` auf `92.205.167.242` setzen. Nach Minuten bis 24 Stunden ist die Seite erreichbar, das SSL-Zertifikat folgt automatisch.
- **Automatische Updates:** Im Kundenportal steht unter Git die Webhook-Adresse. Bei GitHub unter Settings → Webhooks → Add webhook eintragen (Content type `application/json`, «Just the push event»). Danach geht jeder Push automatisch online.
- **Neue Domain bei HostBox:** Die Registrierungsgebühr nennt HostBox vor der Registrierung separat.
- Hilfe: https://hostbox.ch/kontakt

## Fehler

- `422` mit `fields`: Angabe korrigieren (z. B. Domain bereits gehostet, PostgreSQL erst ab Box App, neue Domain schon vergeben). Mit dem Menschen klären und neu vorbereiten.
- `429`: zu viele Versuche, einige Minuten warten.
- `503`: Online-Bestellung gerade geschlossen, auf https://hostbox.ch/kontakt verweisen.
- Status `expired`: Der Link ist nach 7 Tagen abgelaufen. Neu vorbereiten.
- Status `failed`: HostBox ist informiert. Den Menschen beruhigen und auf das Kundenportal verweisen.
