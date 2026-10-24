# Deployment-Runbook: Taskboard auf Render

## Zweck und Geltungsbereich

Dieses Dokument beschreibt, wie das Taskboard aus dem GitHub-Repository geklont, lokal gestartet, auf Render bereitgestellt und nach dem Deployment überprüft wird.

**Repository:** https://github.com/DST81/devops_beispielApp  
**Produktionsplattform:** Render  
**Anwendung:** Python-/Flask-Webanwendung mit Gunicorn  
**Lokaler Endpunkt:** http://127.0.0.1:8000  
**Health Check:** `/health`  
**Standard-Branch:** `main`

Die Anleitung verwendet den Render-Dashboard-Weg. Sie setzt voraus, dass die zuständige Person Schreibzugriff auf das GitHub-Repository sowie Zugriff auf das Render-Konto hat.

---

## Teil A – Voraussetzungen

### A.1 Benötigte Konten und Berechtigungen

Vor Beginn müssen folgende Voraussetzungen erfüllt sein:

| Voraussetzung | Zweck | Prüfung |
|---|---|---|
| GitHub-Konto | Repository abrufen und Quellcode lesen | Anmeldung unter https://github.com |
| Zugriff auf `DST81/devops_beispielApp` | Repository klonen | Repository im Browser öffnen |
| Render-Konto | Webservice erstellen und verwalten | Anmeldung unter https://dashboard.render.com |
| GitHub-Verbindung in Render | Repository für Deployments verbinden | Render-Dashboard → Account Settings bzw. Git Provider |
| Berechtigung zum Erstellen von Services | Webservice anlegen und deployen | Im Render-Konto verfügbare Service-Erstellung prüfen |

Für produktive Änderungen müssen zusätzlich die im Team vereinbarten Freigabe- und Review-Regeln eingehalten werden.

### A.2 Lokal benötigte Werkzeuge

Benötigt werden Git, Python, pip und ein Terminal. Für den lokalen Start wird ausserdem `make` benötigt. Für den optionalen Docker-Test wird Docker mit Docker Compose benötigt.

Versionen prüfen:

```bash
git --version       # erwartet: git 2.x
python3 --version   # erwartet: Python 3.12.x
curl --version      # erwartet: curl 7.x/8.x
python3 -m pip --version    # erwartet: pip 24.x
make --version      
docker --version
docker compose version
```

Python 3.12 wird empfohlen, da das Container-Image auf Python 3.12 basiert.

Falls ein Befehl nicht gefunden wird, muss das entsprechende Werkzeug zunächst installiert werden. Docker ist für den Python-basierten lokalen Start nicht zwingend erforderlich.

### A.3 Zugriffs- und Sicherheitsregeln

- Änderungen werden über Git und den vorgesehenen Branch veröffentlicht.
- Zugangsdaten, Passwörter und Datenbank-URLs mit Zugangsdaten dürfen nicht in Git eingecheckt werden.
- Geheimnisse werden ausschliesslich über die Environment-Einstellungen von Render beziehungsweise lokale, nicht versionierte `.env`-Dateien bereitgestellt.
- Vor einem Deployment muss bekannt sein, welcher Commit veröffentlicht werden soll.

---

## Teil B – Lokale Installation

### B.1 Repository klonen

Ein Terminal öffnen und die folgenden Befehle ausführen:

```bash
git clone https://github.com/DST81/devops_beispielApp.git
cd devops_beispielApp
git status
```

Die letzte Ausgabe sollte den aktuellen Branch anzeigen und einen sauberen Arbeitsbaum melden, sofern keine lokalen Änderungen vorliegen.

**Wichtig:** Die Dateien liegen im Root-Verzeichnis des geklonten Repositories. Es darf nicht zusätzlich in einen nicht vorhandenen Unterordner `beispiel-app` gewechselt werden.

Die benötigten Dateien kontrollieren:

```bash
ls
```

Unter anderem werden `Dockerfile`, `requirements.txt`, `requirements-dev.txt`, `wsgi.py`, `app/` und `Makefile` erwartet.

### B.2 Virtuelle Python-Umgebung erstellen

```bash
python3 -m venv .venv
```

Aktivierung unter Linux/macOS:

```bash
source .venv/bin/activate
```

Aktivierung unter Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Danach pip aktualisieren und die Entwicklungsabhängigkeiten installieren:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Die Entwicklungsabhängigkeiten umfassen die Laufzeitabhängigkeiten sowie Werkzeuge für Tests und Codeprüfung.

### B.3 Anwendung starten

Mit aktivierter virtueller Umgebung:

```bash
make run
```

Der Entwicklungsserver startet auf Port `8000`. Das Terminal bleibt während des Betriebs geöffnet.

Erwartet wird eine Meldung des Flask-Entwicklungsservers, dass er unter `http://127.0.0.1:8000` erreichbar ist.

Die Startmeldung kann je nach Betriebssystem und Flask-Version unterschiedlich aussehen.

### B.4 Anwendung prüfen

In einem zweiten Terminal:

```bash
curl -i http://127.0.0.1:8000/health
```

Erwartet werden HTTP `200 OK` und eine JSON-Antwort nach diesem Muster:

```json
{
  "status": "ok",
  "version": "0.0.0-dev"
}
```

Die konkrete Version kann abweichen, wenn `APP_VERSION` gesetzt wurde.

Anschliessend die Weboberfläche aufrufen:

http://127.0.0.1:8000

Es sollte die Taskboard-Oberfläche erscheinen.

Optional kann die Readiness geprüft werden:

```bash
curl -i http://127.0.0.1:8000/ready
```

Ohne `DATABASE_URL` verwendet die Anwendung den In-Memory-Speicher. Bei erfolgreicher Initialisierung wird HTTP `200` mit `{"status":"ready"}` erwartet.

### B.5 Lokale Tests ausführen

Den Entwicklungsserver gegebenenfalls mit `Ctrl+C` beenden und aus dem Repository-Verzeichnis ausführen:

```bash
make test   #erwartet: 24 passed in x.xx s
```

Die Testsuite wird mit pytest gestartet. Der Befehl muss ohne fehlgeschlagene Tests enden.

Für die Codeprüfung:

```bash
make lint  #erwartet:
```

Dieser Befehl führt Ruff-Prüfungen und eine Formatprüfung aus.

---

## Teil C – Konfigurationsvariablen

Die Anwendung bezieht ihre Konfiguration aus Umgebungsvariablen. Werte werden nicht in den Quellcode eingebaut.

| Name | Standardwert | Geheim (ja/nein) | Wirkung |
|---|---|---|---|
| `DATABASE_URL` | Nicht gesetzt | Ja, wenn Zugangsdaten enthalten sind | Nicht gesetzt: In-Memory-Speicher. Gesetzt: Verbindung zur PostgreSQL-Datenbank. |
| `APP_VERSION` | `0.0.0-dev` im Anwendungscode | Nein | Versionskennung, die unter anderem in `/health` und `/metrics` angezeigt wird. |
| `LOG_LEVEL` | `INFO` | Nein | Legt fest, ab welcher Protokollstufe Meldungen ausgegeben werden. |
| `PORT` | Container-Port `8000`; im Render-Blueprint explizit auf `8000` gesetzt | Nein | Port, auf dem der Service erreichbar sein soll. Muss mit dem Port des Gunicorn-Prozesses übereinstimmen. |
| `GUNICORN_WORKERS` | `1` | Nein | Anzahl der Gunicorn-Worker-Prozesse. Bei In-Memory-Speicherung muss der Wert `1` bleiben. |

### Umgang mit geheimen Werten

`DATABASE_URL` kann Benutzername und Passwort enthalten und muss daher vertraulich behandelt werden.

Beispiel für eine Datenbank-URL:

```text
postgresql://BENUTZER:PASSWORT@HOST:5432/DATENBANK
```

Das Beispiel enthält Platzhalter und darf nicht unverändert als echte Verbindung verwendet werden.

**Geheimnisse gehören nicht ins Repository.**

- Lokal: in eine nicht versionierte `.env`-Datei, sofern diese vom lokalen Setup benötigt wird.
- Auf Render: Dashboard → Webservice → Environment.
- Niemals Zugangsdaten in Git-Commits, Screenshots, öffentlich sichtbare Logs oder Dokumentation schreiben.
- Bei versehentlicher Veröffentlichung ein betroffenes Passwort sofort rotieren und den Vorfall dem Service-Owner melden.

Die Datei `.env.example` ist eine Vorlage. Sie enthält keine produktiven Zugangsdaten.

---

## Teil D – Deployment auf Render

### D.1 Deployment-Variante

Diese Anleitung verwendet ausschliesslich das Render-Dashboard und verbindet den bestehenden GitHub-Branch `main` direkt mit einem Docker-Webservice.

### D.2 Repository und Webservice verbinden

1. Bei https://dashboard.render.com anmelden.
2. Falls noch nicht geschehen, das GitHub-Konto mit Render verbinden.
3. **New +** auswählen.
4. **Web Service** auswählen.
5. Das Repository `DST81/devops_beispielApp` auswählen.
6. Falls das Repository nicht angezeigt wird, die GitHub-Berechtigungen für Render prüfen.
7. Den Branch `main` auswählen.

### D.3 Service konfigurieren

Folgende Einstellungen verwenden:

| Einstellung | Wert |
|---|---|
| Name | `taskboard` |
| Runtime / Environment | Docker |
| Branch | `main` |
| Root Directory | Leer lassen |
| Dockerfile Path | `./Dockerfile` |
| Docker Build Context | `.` |
| Instance Type | Free für Labor und Demonstration, sofern verfügbar |
| Health Check Path | `/health` |

Die Pfade beziehen sich auf das Root-Verzeichnis des verbundenen Repositories.


Der Docker-Build-Kontext `.` ermöglicht dem Dockerfile den Zugriff auf `app/`, `wsgi.py` und `requirements.txt`.

### D.4 Environment-Variablen eintragen

Im Bereich **Environment** folgende Werte anlegen:

| Key | Value |
|---|---|
| `PORT` | `8000` |
| `GUNICORN_WORKERS` | `1` |
| `APP_VERSION` | `1.0.0` |
| `LOG_LEVEL` | `INFO` |

`DATABASE_URL` bleibt für die hier beschriebene Demonstrationskonfiguration ungesetzt. Die Anwendung verwendet dadurch einen In-Memory-Speicher.

Falls eine PostgreSQL-Datenbank verwendet werden soll, muss zuerst eine Datenbank eingerichtet und die korrekte interne Verbindungs-URL als geheime Umgebungsvariable hinterlegt werden.

**Warum nur ein Worker?** Jeder Gunicorn-Worker ist ein eigener Prozess. Ohne Datenbank hat jeder Prozess seinen eigenen In-Memory-Speicher. Bei mehreren Workern können Aufgaben deshalb je nach Anfrage scheinbar verschwinden oder mit `404` nicht gefunden werden.

`PORT=8000` muss zur Konfiguration passen: Das Docker-Image startet Gunicorn auf Port `8000`. Wird dieser Port geändert, müssen Anwendung und Plattformkonfiguration konsistent angepasst werden.

### D.5 Ersten Deploy ausführen

1. Die Einstellungen nochmals kontrollieren.
2. Den Service erstellen und den ersten Deploy starten.
3. Den Build- und Deploy-Logs folgen.
4. Warten, bis Render den Deploy als erfolgreich meldet.
5. Die von Render bereitgestellte öffentliche URL öffnen.

Die öffentliche Adresse hat üblicherweise die Form:

```text
https://<service-name>.onrender.com
```

Der tatsächliche Hostname wird von Render vergeben und muss aus dem Dashboard übernommen werden.

Bei Free-Instanzen kann der erste Aufruf nach einer längeren Ruhephase verzögert sein. Dies ist nicht automatisch ein Ausfall.

### D.6 Wiederkehrendes Deployment

Dieser Ablauf gilt, wenn der Render-Service bereits eingerichtet ist und eine neue Version veröffentlicht werden soll.

1. Im Repository die gewünschten Änderungen fertigstellen und lokal testen:

   ```bash
   make test
   make lint
   ```

2. Änderungen committen und auf den Branch `main` pushen:

   ```bash
   git status
   git add .
   git commit -m "Beschreibung der Änderung"
   git push origin main
   ```

   `git add .` nur verwenden, wenn vorher kontrolliert wurde, dass keine Geheimnisse, lokalen Dateien oder unerwünschten Änderungen enthalten sind.

3. Im Render-Dashboard den Service `taskboard` öffnen und den neuen Deploy unter **Events** beziehungsweise **Deploys** verfolgen.

4. Warten, bis Render den Deploy erfolgreich abgeschlossen hat. Bei einem fehlgeschlagenen Deploy die Logs prüfen und nicht ungeprüft weitere Änderungen veröffentlichen.

5. Nach dem Deploy die Prüfungen aus Teil E durchführen: `/health`, Weboberfläche, Smoke-Test und Logs.

6. Commit-SHA, Deploy-Ergebnis und Testergebnisse dokumentieren.

**Erfolgskriterium:** Die neue Version ist aktiv, `/health` liefert HTTP 200, der Smoke-Test endet mit `SMOKE TEST PASSED` und die Logs zeigen keine betriebsverhindernden Fehler.

---

## Teil E – Verifikation nach dem Deploy

Ein erfolgreicher Build allein beweist noch nicht, dass die Anwendung korrekt erreichbar ist. Die folgenden Prüfungen müssen durchgeführt und dokumentiert werden.

### E.1 Health Check

Die tatsächliche Render-URL aus dem Dashboard übernehmen:

```bash
export BASE_URL="https://taskboard-12vg.onrender.com"
curl -i "$BASE_URL/health"
```

Erwartet:

- HTTP-Status `200 OK`
- JSON mit `"status":"ok"`
- Feld `"version"` mit der konfigurierten Versionskennung, zum Beispiel `"1.0.0"`

Beispiel:

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

Die Reihenfolge der JSON-Felder kann abweichen.

### E.2 Weboberfläche

Die URL ohne Pfad im Browser öffnen:

```text
https://<tatsaechliche-service-url>/
```

Erwartet wird die Taskboard-Oberfläche und kein Render-Fehlerbildschirm.

### E.3 API-Smoke-Test

Der folgende Test prüft, ob eine Aufgabe angelegt, abgerufen und wieder gelöscht werden kann. Er benötigt Python 3, aber keine zusätzlichen Python-Pakete.

```bash
python3 - "$BASE_URL" <<'PY'
import json
import sys
import urllib.error
import urllib.request

base = sys.argv[1].rstrip("/")

def request(path, method="GET", payload=None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(
        base + path, data=data, headers=headers, method=method
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        body = response.read()
        return response.status, json.loads(body) if body else None

status, health = request("/health")
assert status == 200 and health["status"] == "ok", health
print("PASS health:", health)

status, task = request(
    "/api/tasks", "POST", {"title": "deployment-smoke-test"}
)
assert status == 201, (status, task)
task_id = task["id"]
print("PASS create:", task)

status, fetched = request(f"/api/tasks/{task_id}")
assert status == 200 and fetched["title"] == "deployment-smoke-test", fetched
print("PASS read:", fetched)

status, _ = request(f"/api/tasks/{task_id}", "DELETE")
assert status == 204, status
print("PASS delete: HTTP 204")

print("SMOKE TEST PASSED")
PY
```

Erwartete Abschlussmeldung:

```text
PASS health: ...
PASS create: ...
PASS read: ...
PASS delete: HTTP 204
SMOKE TEST PASSED
```

Die konkreten IDs und Versionswerte sind dynamisch. Entscheidend sind die erfolgreichen Assertions und die Abschlussmeldung `SMOKE TEST PASSED`.

Falls die Anwendung während des Tests neu startet oder der Aufruf fehlschlägt, Logs prüfen und den Test nach Behebung der Ursache wiederholen.

### E.4 Logs kontrollieren

1. Im Render-Dashboard den Webservice `taskboard` öffnen.
2. **Logs** auswählen.
3. Den Zeitpunkt des letzten Deployments suchen.
4. Prüfen, ob Gunicorn gestartet ist und HTTP-Anfragen protokolliert werden.
5. Nach Tracebacks, Importfehlern, fehlenden Dateien und wiederholten Neustarts suchen.

Erwartet werden ein erfolgreicher Start des Webservers und keine unbehandelten Fehler, die den Betrieb verhindern.

Die Logs dürfen keine Passwörter oder vollständigen Datenbank-URLs mit Zugangsdaten enthalten.

### E.5 Ergebnis dokumentieren

Für die Abnahme festhalten:

- Commit-SHA des deployten Codes
- Render-Service-URL
- Zeitpunkt des Deployments
- Ergebnis von `/health`
- Ergebnis des Smoke-Tests
- Ergebnis der Logkontrolle

Ein Deployment gilt erst als verifiziert, wenn Health Check, Oberfläche, Smoke-Test und Logs geprüft wurden.

---

## Teil F – Rollback

### F.1 Wann ist ein Rollback erforderlich?

Ein Rollback ist angebracht, wenn ein neuer Deploy die Anwendung beeinträchtigt, beispielsweise durch einen fehlgeschlagenen Start, fehlerhafte API-Antworten oder einen wiederholt fehlschlagenden Health Check.

Vor dem Rollback den fehlerhaften Deploy und die zugehörigen Logs dokumentieren.

### F.2 Auf eine frühere Version zurückkehren

1. Render-Dashboard öffnen.
2. Den Service `taskboard` auswählen.
3. **Deploys** beziehungsweise **Events** öffnen; die genaue Bezeichnung kann sich in der Render-Oberfläche ändern.
4. Den letzten nachweislich funktionierenden Deploy anhand von Zeitstempel und Commit-SHA identifizieren.
5. Über die verfügbare Rollback-Funktion auf diesen Deploy zurückkehren.
6. Die Bestätigung abwarten und kontrollieren, dass die frühere Version wieder aktiv ist.

Falls die Rollback-Funktion für den betreffenden Deploy nicht verfügbar ist, den bekannten funktionierenden Commit auf einem geeigneten Branch wiederherstellen beziehungsweise erneut deployen. Änderungen nur nach den geltenden Repository-Freigaberegeln vornehmen.

Nicht blind den neuesten Deploy erneut starten: Das würde den fehlerhaften Code möglicherweise wieder ausrollen.

### F.3 Rollback verifizieren

Nach dem Rollback dieselben Prüfungen wie in Teil E durchführen:

```bash
curl -i "$BASE_URL/health"
```

Erwartet werden HTTP `200 OK`, `"status":"ok"` und die Versionskennung der zurückgerollten Anwendung.

Anschliessend:

- Weboberfläche öffnen
- Smoke-Test ausführen
- Render-Logs auf Startfehler prüfen
- Commit-SHA und aktive Version dokumentieren

### F.4 Grenzen des Rollbacks

Ein Rollback der Anwendung setzt nicht automatisch Datenbankinhalte auf einen früheren Zustand zurück.

Insbesondere:

- Änderungen an persistenten Daten bleiben möglicherweise bestehen.
- Datenbankmigrationen können mit älteren Anwendungsversionen inkompatibel sein.
- In-Memory-Daten können bei einem Neustart oder neuen Deploy verloren gehen.
- Ein Rollback ersetzt keine Datenbanksicherung.

Bei produktiven Datenbankänderungen muss vorab ein separates Backup- und Wiederherstellungsverfahren existieren. Bei Datenverlust oder inkompatiblen Migrationen den Service-Owner und Datenbankverantwortlichen hinzuziehen.

---

## Teil G – Troubleshooting

### Fehler 1: Render findet das Root Directory nicht

**Symptom**

Der Deploy bricht mit einer Meldung ähnlich dieser ab:

```text
lstat /opt/render/project/src/beispiel-app:
no such file or directory
```

**Ursache**

In der Render-Konfiguration wurde ein Root Directory `beispiel-app` angegeben, das am erwarteten Ort nicht existiert.

**Lösung**

- Root Directory im Dashboard leeren.
- Dockerfile Path auf `./Dockerfile` setzen.
- Docker Build Context auf `.` setzen.
- Prüfen, dass `Dockerfile`, `requirements.txt`, `wsgi.py` und `app/` im Repository-Root liegen.
- Erneut deployen.

### Fehler 2: Render meldet einen fehlgeschlagenen Health Check

**Symptom**

Der Container wird gebaut, der Deploy wird aber nicht als erfolgreich aktiviert.

**Ursache**

Der Health Check ist falsch konfiguriert oder die Anwendung antwortet auf dem erwarteten Pfad nicht erfolgreich. Ein typischer Konfigurationsfehler ist die Verwendung von `/ready` anstelle von `/health`.

`/health` prüft, ob der Prozess läuft. `/ready` prüft zusätzlich die Verfügbarkeit der Abhängigkeiten und kann deshalb beispielsweise bei einem Datenbankproblem `503` liefern.

**Lösung**

- Health Check Path auf `/health` setzen.
- Prüfen, ob Gunicorn erfolgreich startet.
- Portkonfiguration kontrollieren.
- Den Endpunkt direkt über die öffentliche Service-URL testen.

### Fehler 3: Anwendung ist nach längerer Inaktivität scheinbar ausgefallen

**Symptom**

Der erste Aufruf dauert ungewöhnlich lange oder läuft in einen Timeout. Spätere Aufrufe funktionieren wieder.

**Ursache**

Eine Free-Instanz kann nach einer Ruhephase heruntergefahren werden und muss bei einer neuen Anfrage erst wieder starten.

**Lösung**

- Einen erneuten Aufruf durchführen und ausreichend auf den Start warten.
- Render-Logs auf den Neustart prüfen.
- `/health` erneut aufrufen.
- Bei dauerhaftem Ausfall nicht von einem Cold Start ausgehen, sondern Startfehler und Logs untersuchen.

### Fehler 4: Aufgaben werden gelegentlich mit HTTP 404 nicht gefunden

**Symptom**

Eine Aufgabe wird erfolgreich erstellt, scheint bei einer späteren Anfrage aber nicht zu existieren.

**Ursache**

Wenn `DATABASE_URL` nicht gesetzt ist, wird ein In-Memory-Speicher verwendet. Bei mehreren Gunicorn-Workern besitzt jeder Prozess einen eigenen Speicher. Anfragen können dadurch unterschiedliche Aufgabenbestände sehen.

**Lösung**

- `GUNICORN_WORKERS=1` setzen, solange der In-Memory-Speicher verwendet wird.
- Für gemeinsam genutzten und persistenten Zustand PostgreSQL konfigurieren und `DATABASE_URL` sicher hinterlegen.
- Nach der Änderung den Smoke-Test erneut ausführen.

### Fehler 5: Anwendung startet nicht wegen eines falschen Ports

**Symptom**

Der Container läuft scheinbar, aber Render kann die Anwendung nicht erreichen oder meldet einen fehlgeschlagenen Health Check.

**Ursache**

Der von Gunicorn verwendete Port und der für den Service konfigurierte Port stimmen nicht überein.

**Lösung**

- Prüfen, dass `PORT=8000` gesetzt ist.
- Kontrollieren, dass Gunicorn an `0.0.0.0:8000` bindet.
- Dockerfile und Render-Environment auf widersprüchliche Portangaben untersuchen.
- Neu deployen und `/health` testen.

### Fehler 6: Geheimnis erscheint in einem Log oder Commit

**Symptom**

Eine Datenbank-URL oder ein Passwort ist in Logs, einem Screenshot oder einem Git-Commit sichtbar.

**Ursache**

Ein vertraulicher Wert wurde protokolliert oder versehentlich versioniert.

**Lösung**

- Betroffene Zugangsdaten sofort als kompromittiert behandeln.
- Passwort beziehungsweise Zugangsdaten beim jeweiligen Anbieter rotieren.
- Logs und Repository auf weitere Offenlegung prüfen.
- `.env` aus dem Repository entfernen und sicherstellen, dass sie in `.gitignore` steht.
- Den Vorfall an den Service-Owner melden.

Das Löschen eines Git-Commits allein macht ein bereits veröffentlichtes Geheimnis nicht wieder sicher.

---

## Teil H – Kontakt und Eskalation

### Zuständigkeiten

| Rolle | Zuständigkeit | Kontakt |
|---|---|---|
| Service-Owner | Gesamtverantwortung, Deployment-Freigabe und Rollback-Entscheidung | `<Name oder Team>` |
| Betriebsverantwortliche Person | Render-Service, Logs, Health Checks und Erstdiagnose | `<Name oder Team>` |
| Repository-Verantwortliche Person | Quellcode, Dockerfile, Branches und GitHub-Berechtigungen | `<Name oder Team>` |
| Datenbankverantwortliche Person | PostgreSQL, Zugangsdaten, Backups und Wiederherstellung | `<Name oder Team>` |
| Eskalationsstelle | Übernahme bei ungelösten oder schwerwiegenden Störungen | `<Name oder Team>` |

### Kommunikationsweg

1. Fehlerbild, Zeitpunkt, Service-URL und Commit-SHA dokumentieren.
2. Relevante Logs und Ergebnisse der Health- und Smoke-Tests sichern.
3. Den Betriebsverantwortlichen über `<Team-Chat / Ticketsystem / E-Mail>` informieren.
4. Wenn nach **30 Minuten** keine Lösung gefunden wurde, an `<Eskalationsstelle>` eskalieren.
5. Bei Sicherheitsvorfällen, vermutetem Datenverlust oder offen gelegten Geheimnissen sofort eskalieren und nicht erst 30 Minuten warten.

Keine Passwörter, Tokens oder vollständigen Datenbank-URLs in Tickets oder Team-Chats veröffentlichen.


