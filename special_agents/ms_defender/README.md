# Microsoft Defender for Endpoint → Check_MK Integration
## Kompatibel mit Check_MK 2.3 und 2.4 (neue Plugin-API)

---

## Verzeichnisstruktur

```
~/local/lib/python3/cmk_addons/plugins/defender_endpoint/
├── libexec/
│   └── agent_defender_endpoint          ← Special Agent Script (kein .py!)
├── rulesets/
│   └── special_agent.py                 ← GUI-Formular (WATO/Setup)
├── server_side_calls/
│   └── special_agent.py                 ← CLI-Argument-Mapping
└── agent_based/
    └── defender_endpoint_alerts.py      ← Check-Plugin (Services)
```

---

## Schritt 1 – Azure App-Registrierung

### 1a – App anlegen
1. https://portal.azure.com → **Microsoft Entra ID** → **App-Registrierungen** → **Neue Registrierung**
2. Name: z.B. `checkmk-defender-agent`, Kontotyp: Einzelmandant
3. → **Registrieren**

### 1b – API-Berechtigung hinzufügen
1. App → **API-Berechtigungen** → **Berechtigung hinzufügen**
2. → **APIs meiner Organisation** → `WindowsDefenderATP`
3. → **Anwendungsberechtigungen** → `Alert.Read.All` aktivieren
4. → **Berechtigungen hinzufügen**
5. → **Administratorzustimmung erteilen** ⚠️ (erforderlich!)

### 1c – Client Secret erstellen
1. App → **Zertifikate & Geheimnisse** → **Neuer geheimer Clientschlüssel**
2. Beschreibung & Ablauf wählen → **Hinzufügen**
3. **Wert sofort kopieren** – er wird danach nicht mehr vollständig angezeigt!

### 1d – IDs notieren
- **Tenant ID**: Übersichtsseite → "Verzeichnis-ID (Mandant)"
- **Client ID**: Übersichtsseite → "Anwendungs-ID (Client)"
- **Client Secret**: aus Schritt 1c

---

## Schritt 2 – Installation auf dem Check_MK-Server

SSH als Site-User einloggen:
```bash
su - <sitename>
```

### 2a – Verzeichnisse anlegen
```bash
mkdir -p ~/local/lib/python3/cmk_addons/plugins/defender_endpoint/libexec
mkdir -p ~/local/lib/python3/cmk_addons/plugins/defender_endpoint/rulesets
mkdir -p ~/local/lib/python3/cmk_addons/plugins/defender_endpoint/server_side_calls
mkdir -p ~/local/lib/python3/cmk_addons/plugins/defender_endpoint/agent_based
```

### 2b – Dateien kopieren
```bash
# Special Agent (KEIN .py, muss ausführbar sein!)
cp agent_defender_endpoint \
   ~/local/lib/python3/cmk_addons/plugins/defender_endpoint/libexec/
chmod 755 ~/local/lib/python3/cmk_addons/plugins/defender_endpoint/libexec/agent_defender_endpoint

# Ruleset (GUI-Formular)
cp rulesets/special_agent.py \
   ~/local/lib/python3/cmk_addons/plugins/defender_endpoint/rulesets/

# Server-Side-Calls (CLI-Mapping)
cp server_side_calls/special_agent.py \
   ~/local/lib/python3/cmk_addons/plugins/defender_endpoint/server_side_calls/

# Check-Plugin
cp agent_based/defender_endpoint_alerts.py \
   ~/local/lib/python3/cmk_addons/plugins/defender_endpoint/agent_based/
```

### 2c – Python-Abhängigkeiten prüfen
```bash
python3 -c "import requests; print('OK')"
# Falls Fehler:
pip3 install requests
```

### 2d – Apache neu starten (damit das Ruleset sichtbar wird)
```bash
omd restart apache
```

---

## Schritt 3 – Host in Check_MK anlegen

Da kein lokaler Agent benötigt wird, legen wir einen virtuellen Host an:

1. **Setup → Hosts → Host hinzufügen**
2. Hostname: z.B. `defender-endpoint`
3. IP-Adresse: `127.0.0.1`
4. → **Speichern & zur Service-Konfiguration**

---

## Schritt 4 – Special Agent konfigurieren (WATO)

1. **Setup → Agents → Other integrations**
2. Dort erscheint nach dem Apache-Neustart: **Microsoft Defender for Endpoint**
3. → **Regel hinzufügen**
4. Tenant ID, Client ID und Client Secret eintragen
5. Regel auf den Host `defender-endpoint` begrenzen
6. → **Speichern**

---

## Schritt 5 – Service Discovery

```bash
# Auf der Kommandozeile:
cmk -vI defender-endpoint

# Oder in der GUI:
# Setup → Hosts → defender-endpoint → Services → Service-Erkennung
```

Erwartete Services:
- `Defender Alerts Summary` – Gesamtübersicht
- `Defender Host <Hostname>` – Pro betroffenen Endpunkt

Danach: **Änderungen aktivieren**

---

## Schritt 6 – Agent manuell testen

```bash
~/local/lib/python3/cmk_addons/plugins/defender_endpoint/libexec/agent_defender_endpoint \
  --tenant-id   "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" \
  --client-id   "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" \
  --client-secret "dein-secret-hier"
```

Erwartete Ausgabe:
```
<<<defender_endpoint_alerts:sep(124)>>>
SUMMARY|2|5|3|0|10
ALERT|abc123|High|New|DESKTOP-ABC|Malware detected|Malware|2h 15m|T1059|Trojan.GenericKD
ALERT|def456|Medium|InProgress|SERVER-XYZ|Suspicious behavior|SuspiciousActivity|45m||
```

---

## Schwellwerte anpassen (optional)

In Check_MK → **Setup → Services → Service monitoring rules** → suche `defender_endpoint_alerts`:

| Parameter | Standard | Bedeutung |
|---|---|---|
| `warn_high`   | 1 | Ab diesem Wert → WARN bei High-Alerts |
| `crit_high`   | 1 | Ab diesem Wert → CRIT bei High-Alerts |
| `warn_medium` | 1 | Ab diesem Wert → WARN bei Medium-Alerts |
| `crit_medium` | 5 | Ab diesem Wert → CRIT bei Medium-Alerts |

---

## Troubleshooting

| Problem | Ursache | Lösung |
|---|---|---|
| Agent nicht unter "Other integrations" | Apache nicht neu gestartet | `omd restart apache` |
| `403 Forbidden` beim Alert-Abruf | Berechtigung fehlt / kein Admin-Consent | Azure Portal → API-Berechtigungen → Adminzustimmung erteilen |
| `FEHLER Token-Abruf` | Falsche IDs oder Secret | Tenant ID, Client ID, Secret prüfen |
| Keine Services nach Discovery | Agent produziert keinen Output | Agent manuell testen (Schritt 6) |
| `requests` fehlt | Modul nicht installiert | `pip3 install requests` |
| Agent wird nicht gefunden | Falsche Dateirechte | `chmod 755 agent_defender_endpoint` |

---

## Status-Mapping

| Defender Severity | Check_MK Status |
|---|---|
| High | 🔴 CRIT |
| Medium | 🟡 WARN |
| Low | 🟢 OK |
| Informational | 🟢 OK |