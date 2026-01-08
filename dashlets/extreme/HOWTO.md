# Extreme AP Custom Dashlet - Installation & Setup

## 📦 Was ist das?

Ein **natives Check_MK Dashlet** das direkt in deine Check_MK GUI integriert wird und:

✅ **Live-Daten** aus Check_MK Livestatus lädt
✅ **Interaktive Karten** für jeden AP zeigt
✅ **Real-time Statistics** anzeigt
✅ **Auto-Refresh** unterstützt (konfigurierbar)
✅ **Filter nach Sites** (Building-A, Building-B, Outdoor)
✅ **Responsive Design** - passt sich der Größe an

## 🚀 Installation

### Schritt 1: Dashlet Plugin installieren

```bash
# Als site-user
OMD_SITE="deine_site"  # Anpassen!

# Dashlet kopieren
sudo cp extreme_ap_dashboard.py /omd/sites/$OMD_SITE/local/share/check_mk/web/plugins/dashboard/
sudo chown $OMD_SITE:$OMD_SITE /omd/sites/$OMD_SITE/local/share/check_mk/web/plugins/dashboard/extreme_ap_dashboard.py
```

### Schritt 2: Apache neu laden

```bash
omd reload apache
```

### Schritt 3: Browser Cache leeren

Im Browser: `Ctrl + Shift + R` (Hard Refresh)

### Schritt 4: Check_MK GUI neu laden

- Ausloggen und wieder einloggen
- Oder: Einfach Seite neu laden

## 📊 Dashlet zu Dashboard hinzufügen

### Option 1: Neues Dashboard erstellen

**Customize → Visualization → Dashboards → Add dashboard**

```
Title: Extreme Access Points
Topic: Networking
Public: Yes (oder No für privat)
```

**Add dashlet:**
1. Klicke auf **"Add"** (+ Symbol)
2. Wähle **"Extreme Access Points Overview"**
3. Konfiguriere das Dashlet (siehe unten)
4. **Save & go to dashboard**

### Option 2: Zu bestehendem Dashboard hinzufügen

1. Öffne dein Dashboard
2. Klicke **"Edit dashboard"** (Zahnrad-Symbol oben rechts)
3. **"Add dashlet"** → **"Extreme Access Points Overview"**
4. Konfiguriere & Save

## ⚙️ Dashlet Konfiguration

### Im Dashlet Settings Dialog:

#### **Filter by Site**
```
Dropdown-Optionen:
○ All Sites (zeigt alle APs)
○ Building A (nur Building-A APs)
○ Building B (nur Building-B APs)
○ Outdoor (nur Outdoor APs)
```

#### **Maximum APs to display**
```
Slider: 5 - 100
Default: 20

Begrenzt die Anzahl der APs im Detail-View.
Nützlich bei vielen APs für Performance.
```

#### **Size** (Grid Units)
```
Width: 60 (empfohlen für 2-3 Spalten APs)
Height: 40 (passt sich automatisch an Inhalt an)
```

#### **Refresh Interval**
```
60 seconds (default)
30 seconds (für schnellere Updates)
120 seconds (bei vielen APs)
```

## 🎨 Dashboard Beispiel-Layouts

### Layout 1: Single Focus Dashboard

```
┌─────────────────────────────────────────────────┐
│                                                 │
│     Extreme Access Points Overview (60x40)     │
│                                                 │
│  [Stats Cards: Total | Online | Clients | Issues]
│                                                 │
│  [AP Grid - zeigt alle APs mit Details]        │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Layout 2: Multi-View Dashboard

```
┌──────────────────────┬──────────────────────────┐
│                      │                          │
│  Extreme APs         │  Host Statistics         │
│  (30x20)             │  (30x20)                 │
│  Filter: Building-A  │                          │
│                      │                          │
├──────────────────────┼──────────────────────────┤
│                      │                          │
│  Service Problems    │  Event Console           │
│  (30x20)             │  (30x20)                 │
│                      │                          │
└──────────────────────┴──────────────────────────┘
```

### Layout 3: Stacked Per-Site View

```
┌─────────────────────────────────────────────────┐
│  Extreme APs - Building A (60x15)               │
│  [Stats + APs für Building-A]                   │
├─────────────────────────────────────────────────┤
│  Extreme APs - Building B (60x15)               │
│  [Stats + APs für Building-B]                   │
├─────────────────────────────────────────────────┤
│  Extreme APs - Outdoor (60x10)                  │
│  [Stats + APs für Outdoor]                      │
└─────────────────────────────────────────────────┘
```

## 🎯 Dashlet Features im Detail

### Statistics Cards (oben)

| Card | Zeigt | Farbe |
|------|-------|-------|
| **Total APs** | Gesamtzahl + Online Count | Lila Gradient |
| **Connected** | Anzahl online APs | Grün Gradient |
| **Total Clients** | Summe aller Clients + Durchschnitt | Gelb/Pink Gradient |
| **Issues** | Offline + High Load APs | Rot/Gelb Gradient |

### AP Cards (Grid)

**Jede Karte zeigt:**
- 🟢 **Header** (farbcodiert: Grün=Online, Rot=Offline)
  - Hostname
  - Site/Location
- 📋 **Info Grid**:
  - Model (z.B. AP4000U)
  - IP-Adresse
  - Status Badge (Online/Offline)
  - Software Version
- 👥 **Client Box** (blauer Hintergrund):
  - Große Zahl: Total Clients
  - Split: 2.4GHz / 5GHz Clients
- 📊 **Performance Metrics**:
  - CPU: Progress Bar + Prozent (Grün/Gelb/Rot)
  - Memory: Progress Bar + Prozent (Grün/Gelb/Rot)

### Farbcodierung

**Status:**
- 🟢 Grün = Connected, Everything OK
- 🟡 Gelb = Warning (CPU/Memory 60-80%)
- 🔴 Rot = Critical (CPU/Memory >80% oder Offline)

**Progress Bars:**
- 0-60%: Grün
- 60-80%: Gelb/Orange
- 80-100%: Rot

## 🔄 Live-Daten Update

Das Dashlet lädt Daten via **Livestatus Query** direkt von Check_MK:

```python
# Query ausgeführt:
GET services
Columns: host_name, service_description, state, plugin_output
Filter: service_description ~~ Extreme AP
```

**Data Flow:**
1. Dashlet fragt Livestatus ab
2. Parst Service Outputs (von deinen Check Plugins)
3. Berechnet Statistics
4. Rendert HTML mit CSS
5. Auto-Refresh nach X Sekunden

## 📐 Größenanpassung

### Empfohlene Größen:

**Klein (Übersicht):**
```
Width: 30 grid units
Height: 20 grid units
Max APs: 6-8
```

**Mittel (Standard):**
```
Width: 60 grid units
Height: 40 grid units
Max APs: 20
```

**Groß (Vollansicht):**
```
Width: 90 grid units
Height: 60 grid units
Max APs: 50
```

**Fullscreen:**
```
Width: 120 grid units
Height: 80 grid units
Max APs: 100
```

## 🧪 Testen

### Check 1: Plugin installiert?

```bash
ls -la ~/local/share/check_mk/web/plugins/dashboard/extreme_ap_dashboard.py
```

### Check 2: Dashlet in GUI sichtbar?

1. **Customize → Visualization → Dashboards**
2. **Dashboard öffnen → Edit**
3. **Add dashlet** - Suche nach "Extreme"
4. Sollte erscheinen: **"Extreme Access Points Overview"**

### Check 3: Daten werden geladen?

1. Dashlet hinzufügen
2. Sollte Statistics Cards zeigen
3. Sollte AP Cards zeigen
4. Wenn leer: Check ob APs als Piggyback Hosts existieren

### Check 4: Browser Console

```
F12 → Console Tab
Sollte keine Fehler zeigen
```

## 🔧 Troubleshooting

### Dashlet erscheint nicht in Liste

**Lösung:**
```bash
# Python Syntax checken
python3 -m py_compile ~/local/share/check_mk/web/plugins/dashboard/extreme_ap_dashboard.py

# Apache neu laden
omd reload apache

# Browser Cache leeren (Ctrl+Shift+R)
```

### "No data" oder leeres Dashlet

**Check 1: Haben APs Services?**
```bash
# Als site-user
cmk --list-hosts | grep AP-

# Services für einen AP checken
cmk -D AP-Building-A-Floor1
```

**Check 2: Sind Services discovered?**
```
Setup → Hosts → [AP Host] → Services → Discovery
```

**Check 3: Livestatus Query manuell testen**
```bash
echo "GET services
Columns: host_name service_description state plugin_output
Filter: service_description ~~ Extreme AP" | lq
```

### CSS wird nicht angezeigt

**Browser Cache Problem:**
- `Ctrl + Shift + R` (Hard Refresh)
- Oder: Browser DevTools → Network → "Disable cache" aktivieren

### Performance bei vielen APs

**Optimierungen:**

1. **Max APs reduzieren:**
   ```
   Dashlet Settings → Maximum APs: 10-15
   ```

2. **Refresh Interval erhöhen:**
   ```
   Refresh Interval: 120 seconds
   ```

3. **Filter nach Site:**
   ```
   Statt "All Sites" → "Building-A" nur
   Erstelle mehrere Dashlets pro Site
   ```

## 📊 Erweiterte Anpassungen

### Custom CSS (optional)

Wenn du das Design anpassen willst, editiere in `extreme_ap_dashboard.py`:

**Beispiel: Andere Farben für Stats Cards**
```python
# Zeile ~120 im Code:
.extreme-stat-card {
    background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
}
```

### Zusätzliche Metriken anzeigen

Im Code kannst du weitere Daten aus den Services parsen:

```python
# Bei "Details" Service:
if "Details" in service_desc:
    parts = output.split("|")
    aps_data[host_name].update({
        "cpu": float(parts[0]),
        "memory": float(parts[1]),
        "uptime": int(parts[2]),
        "power_mode": parts[3],  # NEU
        "poe_power": float(parts[4]),  # NEU
    })
```

Dann im Render-Code nutzen:
```python
power = ap.get("power_mode", "N/A")
html.span(f"Power: {power}")
```

## 📱 Mobile View

Das Dashlet ist **responsive**:
- Auf Desktop: Grid mit 2-3 Spalten
- Auf Tablet: Grid mit 1-2 Spalten
- Auf Mobile: Single Column

Grid passt sich automatisch an: `grid-template-columns: repeat(auto-fill, minmax(300px, 1fr))`

## 🎯 Best Practices

### 1. Mehrere Dashlets für große Installationen
Statt 100 APs in einem Dashlet:
- **Dashlet 1**: Building-A (Filter: Building-A)
- **Dashlet 2**: Building-B (Filter: Building-B)
- **Dashlet 3**: Outdoor (Filter: Outdoor)

### 2. Dashboard für NOC/Operations
```
- Large Display / TV
- Fullscreen Dashboard
- Auto-Refresh: 30 seconds
- Max APs: 50
- Width: 120, Height: 80
```

### 3. Manager Overview Dashboard
```
- Nur Statistics Cards prominent
- Max APs: 10 (nur kritische)
- Refresh: 60 seconds
- Kombiniert mit anderen Business-Metriken
```

### 4. Troubleshooting Dashboard
```
- Filter: nur "high_load" oder "disconnected"
- Max APs: 20
- Refresh: 30 seconds
- Kombiniert mit Log-Views
```

## 📚 Integration mit anderen Dashlets

**Kombiniere mit:**

1. **Host Statistics** - Zeigt Gesamtzahl Hosts
2. **Service Problems** - Zeigt alle Service-Probleme
3. **Event Console** - Zeigt aktuelle Events
4. **Custom Graphs** - CPU/Memory Trends über Zeit
5. **Top Lists** - Top 10 APs nach Client-Count

## ✅ Checkliste

- [ ] Dashlet Plugin installiert
- [ ] Apache neu geladen
- [ ] Browser Cache geleert
- [ ] Dashlet in GUI sichtbar
- [ ] Dashboard erstellt
- [ ] Dashlet hinzugefügt & konfiguriert
- [ ] Daten werden angezeigt
- [ ] Refresh funktioniert
- [ ] Größe angepasst
- [ ] Filter getestet

## 🎉 Fertig!

Du hast jetzt ein **natives Check_MK Dashlet** für deine Extreme APs!

**Features:**
- ✅ Live-Daten aus Livestatus
- ✅ Auto-Refresh
- ✅ Interaktive Cards
- ✅ Responsive Design
- ✅ Site-Filter
- ✅ Performance-Metriken
- ✅ Production-Ready

**Möchtest du noch:**
- 📈 Historische Graphs (CPU/Memory Trends)?
- 🔔 Click-through zu Host-Details?
- 📊 Export-Funktion (PDF/Excel)?
- 🎨 Dark Mode?
