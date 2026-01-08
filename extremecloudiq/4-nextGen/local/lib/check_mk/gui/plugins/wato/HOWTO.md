# WATO GUI Integration - Installation & Nutzung

## 📦 Was bringt dir die WATO Integration?

✨ **Keine CLI-Commands mehr nötig** - alles über die Web-GUI
✨ **Schöne Formulare** für alle Einstellungen
✨ **Parameter-Rules** mit Dropdowns und Validierung
✨ **Unterschiedliche Thresholds** per Host/Folder/Label
✨ **Test-Button** in der GUI (Enterprise Edition)

## 🚀 Installation

### Schritt 1: WATO Plugin kopieren

```bash
# Als site-user
OMD_SITE="deine_site"  # Anpassen!

# WATO Plugin installieren
sudo cp extreme_wato_integration.py /omd/sites/$OMD_SITE/local/lib/check_mk/gui/plugins/wato/
sudo chown $OMD_SITE:$OMD_SITE /omd/sites/$OMD_SITE/local/lib/check_mk/gui/plugins/wato/extreme_wato_integration.py
```

### Schritt 2: Apache neu laden

```bash
omd reload apache

# Oder bei älteren Versionen:
omd restart apache
```

### Schritt 3: Check_MK GUI neu laden

- Im Browser: `Ctrl + Shift + R` (Hard Refresh)
- Oder: Ausloggen und wieder einloggen

## 🎯 Verwendung in WATO

### 1. Special Agent konfigurieren

**Setup → Agents → VM, Cloud, Container → ExtremeCloud IQ Access Points**

Klicke auf **"Add rule"** und konfiguriere:

#### Option A: Mit API Token (empfohlen) 🔐

```
Authentication Method:
  ○ Username and Password
  ● API Token
    Token: ********************************
    
API Timeout: 30 seconds
Debug Mode: Disabled

Conditions:
  Explicit hosts: extreme-cloud-iq
```

#### Option B: Mit Username/Password

```
Authentication Method:
  ● Username and Password
    Username: admin@company.com
    Password: ********
  ○ API Token
    
API Timeout: 30 seconds
Debug Mode: Disabled
```

### 2. Host erstellen mit GUI

**Setup → Hosts → Add host**

```
Hostname: extreme-cloud-iq
IP Address Family: No IP
Monitored data: 
  ☑ Check_MK Agent (don't select this)
  ☑ Use special agent: ExtremeCloud IQ Access Points

Save & go to service configuration
```

### 3. Client Count Thresholds anpassen

**Setup → Services → Service monitoring rules → ExtremeCloud IQ AP Client Count**

**Add rule:**

```
Warning at: 50 clients
Critical at: 80 clients

Conditions:
  Host labels: 
    - site:campus (für Campus APs)
```

**Beispiel für High-Density APs:**

```
Warning at: 100 clients
Critical at: 150 clients

Conditions:
  Host labels:
    - ap_type:high_density
```

### 4. Performance Thresholds (CPU/Memory)

**Setup → Services → Service monitoring rules → ExtremeCloud IQ AP Performance**

**Add rule:**

```
CPU Warning Level: 80.0%
CPU Critical Level: 90.0%
Memory Warning Level: 80.0%
Memory Critical Level: 90.0%

Conditions:
  Folders: /Networking/Access Points/
```

## 📊 WATO GUI Features im Detail

### Datasource Program Rule

Die GUI bietet dir:

| Feld | Beschreibung | Beispiel |
|------|-------------|----------|
| **Authentication Method** | Dropdown: Username/Password oder API Token | API Token empfohlen |
| **Username** | Text Input mit Validierung | `admin@company.com` |
| **Password** | Password-Feld (versteckt) | `********` |
| **API Token** | Password-Feld (versteckt, 60 chars) | `eyJ0eXAiOiJKV1Q...` |
| **API Timeout** | Integer Slider (5-120 sec) | `30` |
| **Debug Mode** | Dropdown: Enabled/Disabled | `Disabled` |

### Check Parameter Rules

#### 1. Client Count Rule

```
ExtremeCloud IQ AP Client Count
├── Warning at: Integer (min: 1)
└── Critical at: Integer (min: 1)

Conditions können sein:
- Explicit hosts
- Host labels (site:campus, ap_type:high_density)
- Folders (/Networking/APs/Building-A/)
```

#### 2. Performance Rule

```
ExtremeCloud IQ AP Performance
├── CPU Warning Level: Float (0-100%)
├── CPU Critical Level: Float (0-100%)
├── Memory Warning Level: Float (0-100%)
└── Memory Critical Level: Float (0-100%)
```

## 🏷️ Host Labels für flexible Rules

### Labels anlegen

**Setup → Hosts → Labels**

Erstelle Labels für deine APs (werden automatisch via Piggyback angelegt):

```yaml
site: campus
ap_type: high_density
building: building_a
floor: 2
```

### Rules basierend auf Labels

**Beispiel 1: Campus APs mit höheren Limits**

```
Rule: ExtremeCloud IQ AP Client Count
Warning: 100
Critical: 150
Condition: Host label "site" = "campus"
```

**Beispiel 2: Outdoor APs mit niedrigeren CPU-Limits**

```
Rule: ExtremeCloud IQ AP Performance
CPU Warning: 70%
CPU Critical: 85%
Condition: Host label "ap_type" = "outdoor"
```

## 📁 Folder-Struktur Best Practice

```
Main
└── Networking
    └── Extreme Cloud IQ
        ├── extreme-cloud-iq (Main Host)
        └── Access Points/
            ├── Building-A/
            │   ├── AP-A-Floor1
            │   ├── AP-A-Floor2
            │   └── AP-A-Floor3
            ├── Building-B/
            │   └── ...
            └── Outdoor/
                ├── AP-Parking
                └── AP-Garden
```

**Vorteile:**
- Rules per Folder anwendbar
- Übersichtliche Struktur
- Bulk-Operations möglich

## 🎨 GUI Screenshots (was du siehst)

### Special Agent Rule

```
┌─ ExtremeCloud IQ Access Points ──────────────────┐
│                                                   │
│ Authentication Method                             │
│ ○ Username and Password                          │
│   Username: [admin@company.com              ]    │
│   Password: [********                       ]    │
│                                                   │
│ ● API Token                                      │
│   Token: [********************************  ]    │
│                                                   │
│ API Timeout: [30] seconds                        │
│                                                   │
│ Debug Mode: [Disabled ▼]                         │
│                                                   │
│ ┌─ Conditions ────────────────────────────────┐  │
│ │ Explicit hosts: [extreme-cloud-iq]         │  │
│ └──────────────────────────────────────────────┘  │
│                                                   │
│              [Save]  [Cancel]                     │
└───────────────────────────────────────────────────┘
```

### Client Count Rule

```
┌─ ExtremeCloud IQ AP Client Count ────────────────┐
│                                                   │
│ Warning at:  [50  ] clients                      │
│ Critical at: [80  ] clients                      │
│                                                   │
│ ┌─ Conditions ────────────────────────────────┐  │
│ │ Host labels:                                │  │
│ │   ☑ site = campus                          │  │
│ │   ☐ ap_type = high_density                 │  │
│ └──────────────────────────────────────────────┘  │
│                                                   │
│              [Save]  [Cancel]                     │
└───────────────────────────────────────────────────┘
```

## 🔧 Troubleshooting

### GUI zeigt Rule nicht an?

```bash
# Check ob Datei korrekt installiert ist
ls -la ~/local/lib/check_mk/gui/plugins/wato/extreme_wato_integration.py

# Check Python Syntax
python3 -m py_compile ~/local/lib/check_mk/gui/plugins/wato/extreme_wato_integration.py

# Apache neu laden
omd reload apache

# Browser Cache leeren (Ctrl+Shift+R)
```

### Import Errors im GUI?

Check das Error-Log:

```bash
tail -f ~/var/log/web.log
tail -f ~/var/log/apache/error_log
```

Häufige Fehler:
- Fehlende Imports (Check_MK Version?)
- Syntax-Fehler (Python 3!)
- Permissions (chown!)

### Rule erscheint nicht in Service monitoring rules?

Die Rules erscheinen unter:
- **Setup → Services → Service monitoring rules**
- Filter nach "Extreme" oder "Cloud"

Wenn nicht:
1. Check ob Check Plugins installiert sind
2. Service Discovery auf einem Host durchführen
3. cmk --reload config

## 📚 Erweiterte Features (Optional)

### Host Tags definieren

Erstelle `local/lib/check_mk/gui/plugins/wato/extreme_tags.py`:

```python
from cmk.gui.plugins.wato import (
    register_hosttag_group,
    HostTagGroupSpec,
)

register_hosttag_group(
    HostTagGroupSpec(
        id="extreme_ap_location",
        title="Extreme AP Location Type",
        tags=[
            ("indoor", "Indoor", []),
            ("outdoor", "Outdoor", []),
            ("warehouse", "Warehouse", []),
        ],
    )
)
```

Dann: `omd reload apache`

### Bulk-Operations

1. Alle APs in einem Folder markieren
2. **Bulk operations → Edit attributes**
3. Labels oder Tags zuweisen
4. Rules basierend auf diesen Attributen erstellen

## ✅ Checkliste

- [ ] WATO Plugin installiert (`extreme_wato_integration.py`)
- [ ] Apache neu geladen
- [ ] Special Agent Rule in GUI erstellt
- [ ] Main Host angelegt mit Special Agent
- [ ] Service Discovery durchgeführt
- [ ] Piggyback Hosts erscheinen automatisch
- [ ] Parameter Rules angepasst
- [ ] Host Labels definiert (optional)
- [ ] Folder-Struktur angelegt

## 🎯 Nächste Schritte

Jetzt kannst du alles über die GUI machen:

1. ✅ **Special Agent konfigurieren** - kein CLI mehr nötig
2. ✅ **Thresholds anpassen** - schöne Formulare
3. ✅ **Rules per Folder/Label** - flexibel & übersichtlich
4. ✅ **Bulk-Operations** - viele APs auf einmal konfigurieren

**Brauchst du noch:**
- 📊 Dashboards für Extreme APs?
- 📧 Notification Rules?
- 🎨 Custom Views?
