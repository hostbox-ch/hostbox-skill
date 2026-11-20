#!/usr/bin/env python3
"""HostBox-Helfer für KI-Assistenten (nur Python-Standardbibliothek).

Befehle:
  link     Bestell-Link erzeugen (ohne Internet, für jeden Assistenten)
  order    Bestellung über die Bestell-API vorbereiten -> Bestätigungs-Link für den Menschen
  status   Stand der Bestellung abfragen (--wait: warten bis bezahlt und eingerichtet)
  services Eigene Hostings auflisten (braucht Kunden-Token)
  job      Stand eines Auftrags (braucht Kunden-Token)
  deploy   Neu ausrollen (braucht Kunden-Token)

Geheimnisse (Abholcode hbo_…, Kunden-Token hbx_…) speichert das Skript in .hostbox/ im
aktuellen Ordner (nur für Sie lesbar) und gibt sie nie aus. Kunden-Token alternativ per
Umgebungsvariable HOSTBOX_TOKEN. Andere Adresse zum Testen: HOSTBOX_URL.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("HOSTBOX_URL", "https://hostbox.ch").rstrip("/")
STATE_DIR = ".hostbox"
UA = "hostbox-skill/1.0"


def _state_path(name):
    os.makedirs(STATE_DIR, mode=0o700, exist_ok=True)
    ignore = os.path.join(STATE_DIR, ".gitignore")
    if not os.path.exists(ignore):
        with open(ignore, "w") as f:
            f.write("*\n")
    return os.path.join(STATE_DIR, name)


def _save(name, data):
    path = _state_path(name)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(data, f)


def _load(name):
    try:
        with open(os.path.join(STATE_DIR, name)) as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def _request(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("User-Agent", UA)
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except ValueError:
            return e.code, {"error": f"HTTP {e.code}"}
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(
            f"Keine Verbindung zu {BASE} ({e}). Ohne Internetzugang: Befehl «link» verwenden "
            "und dem Menschen den Bestell-Link geben.",
            file=sys.stderr,
        )
        sys.exit(3)


def _fail(status, data):
    print(f"Fehler {status}: {data.get('error', data)}", file=sys.stderr)
    if data.get("fields"):
        for k, v in data["fields"].items():
            print(f"  {k}: {v}", file=sys.stderr)
    sys.exit(1)


def _token():
    tok = os.environ.get("HOSTBOX_TOKEN") or (_load("token.json") or {}).get("token")
    if not tok:
        print(
            "Kein Kunden-Token. Entweder nach der Bestellung «status» aufrufen (der Mensch muss den Zugang "
            "erlaubt haben) oder den Menschen bitten, im Kundenportal unter «API und Agenten» ein Token zu "
            "erstellen und als HOSTBOX_TOKEN zu setzen.",
            file=sys.stderr,
        )
        sys.exit(2)
    return tok


def cmd_link(a):
    q = {
        "paket": a.plan,
        "intervall": "jahr" if a.interval == "year" else "monat",
        "domain": a.domain,
        "domainart": "neu" if a.domain_mode == "new" else "vorhanden",
    }
    if a.database:
        q["datenbank"] = {"none": "keine"}.get(a.database, a.database)
    if a.mailbox is not None:
        q["postfach"] = a.mailbox
    if a.git_url:
        q["git"] = a.git_url
    if a.git_branch and a.git_branch != "main":
        q["branch"] = a.git_branch
    if a.setup:
        q["einrichtung"] = "1"
    if a.name:
        q["name"] = a.name
    if a.company:
        q["firma"] = a.company
    if a.email:
        q["email"] = a.email
    print(BASE + "/bestellen?" + urllib.parse.urlencode(q, quote_via=urllib.parse.quote))


def cmd_order(a):
    body = {
        "plan": a.plan,
        "interval": a.interval,
        "domain": a.domain,
        "domain_mode": a.domain_mode,
        "database": a.database or "none",
        "mailbox": a.mailbox or "",
        "git_url": a.git_url or "",
        "git_branch": a.git_branch or "main",
        "setup": bool(a.setup),
    }
    token = os.environ.get("HOSTBOX_TOKEN")
    if not token:
        if not (a.name and a.email):
            print("Ohne Kunden-Token braucht es --name und --email des Menschen.", file=sys.stderr)
            sys.exit(2)
        body["customer"] = {"name": a.name, "email": a.email, **({"company": a.company} if a.company else {})}
    status, data = _request("POST", "/api/v1/orders", body, token)
    if status != 201:
        _fail(status, data)
    _save("order.json", {"claim_code": data["claim_code"], "domain": a.domain, "status_url": data["status_url"]})
    s = data["summary"]
    print("Bestellung vorbereitet (noch nicht bestellt).")
    print(f"Paket: {s['plan_name']}, {'jährlich' if s['interval'] == 'year' else 'monatlich'} · Domain: {s['domain']}")
    print(f"Heute fällig: {s['due_today_chf']}" + (f" (inkl. Einrichtung {s['setup_chf']})" if s.get("setup_chf") else ""))
    print("")
    print("Diesen Link dem Menschen geben (prüfen, Konto, AGB, Zahlung bei Stripe):")
    print(data["confirm_url"])
    print("")
    print(f"Gültig bis {data['expires_at']}. Danach: python3 scripts/hostbox.py status --wait")


def _show(d):
    print(f"Status: {d['status']} – {d['message']}")
    if d.get("order_number"):
        print(f"Bestellung: {d['order_number']}")
    if d.get("portal_url"):
        print(f"Kundenportal: {d['portal_url']}")
    for j in d.get("jobs") or []:
        print(f"  Auftrag {j['id']}: {j['label']} – {j['status']}" + (f" ({j['error']})" if j.get("error") else ""))
    if d.get("api_token"):
        _save("token.json", {"token": d["api_token"], "service_id": d.get("service_id"), "domain": d.get("domain")})
        print("Kunden-Token erhalten und in .hostbox/token.json gespeichert (nicht anzeigen, nicht committen).")
    elif d.get("api_token_note"):
        print(d["api_token_note"])


def cmd_status(a):
    order = _load("order.json")
    if not order:
        print("Keine vorbereitete Bestellung in .hostbox/order.json. Zuerst «order» ausführen.", file=sys.stderr)
        sys.exit(2)
    deadline = time.time() + a.timeout * 60
    last = None
    while True:
        status, d = _request("GET", "/api/v1/orders/status", token=order["claim_code"])
        if status != 200:
            _fail(status, d)
        key = (d["status"], tuple((j["id"], j["status"]) for j in d.get("jobs") or []), bool(d.get("api_token")))
        if key != last:
            _show(d)
            last = key
        done_jobs = d.get("jobs") and all(j["status"] in ("done", "failed", "needs_approval", "cancelled") for j in d["jobs"])
        if not a.wait or d["status"] in ("active", "failed", "cancelled", "expired") and (done_jobs or d["status"] != "active"):
            break
        if time.time() > deadline:
            print("Zeitlimit erreicht – später erneut «status» aufrufen.")
            break
        time.sleep(20)


def cmd_services(a):
    status, d = _request("GET", "/api/v1/services", token=_token())
    if status != 200:
        _fail(status, d)
    for s in d["services"]:
        print(f"{s['id']}: {s['domain']} – {s['plan']} – {s['status']}")


def cmd_job(a):
    status, d = _request("GET", f"/api/v1/jobs/{a.id}", token=_token())
    if status != 200:
        _fail(status, d)
    print(json.dumps(d, ensure_ascii=False, indent=2))


def cmd_deploy(a):
    status, d = _request("POST", f"/api/v1/services/{a.service_id}/deploy", {}, _token())
    if status not in (200, 202):
        _fail(status, d)
    print(f"Ausrollen gestartet, Auftrag {d.get('job_id')}. Stand: python3 scripts/hostbox.py job {d.get('job_id')}")


def main():
    p = argparse.ArgumentParser(description="HostBox-Helfer für KI-Assistenten")
    sub = p.add_subparsers(dest="cmd", required=True)

    def order_args(sp):
        sp.add_argument("--plan", choices=["site", "app", "studio"], required=True)
        sp.add_argument("--interval", choices=["year", "month"], default="year")
        sp.add_argument("--domain", required=True)
        sp.add_argument("--domain-mode", choices=["existing", "new"], default="existing")
        sp.add_argument("--database", choices=["none", "mysql", "postgresql"])
        sp.add_argument("--mailbox", help="Teil vor dem @, z. B. info (leer = keines)")
        sp.add_argument("--git-url")
        sp.add_argument("--git-branch", default="main")
        sp.add_argument("--setup", action="store_true", help="Zusatz «Wir bringen es online»")
        sp.add_argument("--name")
        sp.add_argument("--email")
        sp.add_argument("--company")

    order_args(sub.add_parser("link", help="Bestell-Link erzeugen (ohne Internet)"))
    order_args(sub.add_parser("order", help="Bestellung über die Bestell-API vorbereiten"))
    st = sub.add_parser("status", help="Stand der vorbereiteten Bestellung")
    st.add_argument("--wait", action="store_true")
    st.add_argument("--timeout", type=int, default=30, help="Minuten (mit --wait)")
    sub.add_parser("services", help="Eigene Hostings")
    j = sub.add_parser("job", help="Stand eines Auftrags")
    j.add_argument("id", type=int)
    dp = sub.add_parser("deploy", help="Neu ausrollen")
    dp.add_argument("service_id", type=int)

    a = p.parse_args()
    {"link": cmd_link, "order": cmd_order, "status": cmd_status, "services": cmd_services, "job": cmd_job, "deploy": cmd_deploy}[a.cmd](a)


if __name__ == "__main__":
    main()
