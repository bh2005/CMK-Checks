# ExtremeCloud IQ Special Agent - Installation & Setup

## 📦 Was hast du bekommen?

1. **Special Agent** (`agent_extreme_cloud_iq`) - Fragt die API ab
2. **Check Plugins** - 4 Services pro AP:
   - `Extreme AP Status` - Verbindungsstatus
   - `Extreme AP Clients` - Client-Anzahl mit Levels
   - `Extreme AP Details` - CPU, RAM, Uptime
   - `Extreme Infrastructure Summary` - Gesamtübersicht

## 🚀 Installation

### Schritt 1: Special Agent installieren

```bash
# Als site-user
OMD_SITE="deine_site"  # Anpassen!

# Agent kopieren
sudo cp agent_extreme_cloud_iq /omd/sites/$OMD_SITE/local/share/check_mk/agents/special/
sudo chmod +x /omd/sites/$OMD_SITE/local/share/check_mk/agents/special/agent_extreme_cloud_iq
sudo chown $OMD_SITE:$OMD_SITE /omd/sites/$OMD_SITE/local/share/check_mk/agents/special/agent_extreme_cloud_iq
```

### Schritt 2: Check Plugins installieren

```bash
# Check Plugins kopieren (Check_MK 2.x)
sudo cp extreme_check_plugins.py /omd/sites/$OMD_SITE/local/lib/check_mk/base/plugins/agent_based/
sudo chown $OMD_SITE:$OMD_SITE /omd/sites/$OMD_SITE/local/lib/check_mk/base/plugins/agent_based/extreme_check_plugins.py
```

### Schritt 3: Special Agent Rule erstellen

**Setup → Agents → Other integrations → ExtremeCloud IQ (manual rule creation)**

Erstelle eine neue Datasource Program Rule:

```python
# In WATO: Setup → Agents → VM, Cloud, Container → Individual program call
{
    'id': 'extreme_cloud_iq',
    'command_line': 'agent_extreme_cloud_iq --username $USER$ --password $PASSWORD$',
    'use_only_cache': False,
}
```

**Oder als Custom Rule (Setup → Agent Rules → Datasource Programs):**

```
Command line: 
special_agents:extreme_cloud_iq

Configuration (in WATO GUI):
- Username: your-api-user@company.com
- Password: ********
- (Optional) API Token: wenn du statt User/Pass einen Token nutzt
```

### Schritt 4: Host in Check_MK erstellen

1. **Main Host erstellen**: `extreme-cloud-iq`
   - IP: Keine (Special Agent)
   - Agent Type: No API integrations, no Check_MK agent
   - Datasource: ExtremeCloud IQ

2. **Service Discovery ausführen**
   - Findet: `Extreme Infrastructure Summary`

3. **APs werden automatisch als Piggyback-Hosts erstellt!**
   - Jedes AP wird als eigener Host angelegt
   - Mit 3 Services: Status, Clients, Details

## 🔑 API Credentials erstellen

### In ExtremeCloud IQ:

1. **Login** → https://extremecloudiq.com
2. **Global Settings** → **API Token Management**
3. **Generate API Token**
   - Client ID: `checkmk-monitoring`
   - Description: Check_MK Monitoring
   - **Kopiere den Token!** (wird nur einmal angezeigt)

### Verwendung:

**Option A: Username/Password**
```bash
--username admin@company.com --password YourPassword
```

**Option B: API Token (empfohlen)**
```bash
--api-token YOUR_GENERATED_TOKEN_HERE
```

## 🧪 Testen

### Manueller Test:

```bash
# Als site-user
OMD[deine_site]$ export EXTREME_USERNAME="admin@company.com"
OMD[deine_site]$ export EXTREME_PASSWORD="password"

# Agent ausführen
OMD[deine_site]$ ~/local/share/check_mk/agents/special/agent_extreme_cloud_iq --debug

# Oder mit API Token:
OMD[deine_site]$ ~/local/share/check_mk/agents/special/agent_extreme_cloud_iq --api-token YOUR_TOKEN --debug
```

**Erwartete Ausgabe:**
```
<<<<AP-Hostname-1>>>>
<<<extreme_ap_status>>>
AP-01|ABC123|aa:bb:cc:dd:ee:ff|10.0.1.50|AP4000|1|CONNECTED|10.0.2.1|Building-A
<<<extreme_ap_clients>>>
15|8|7
<<<extreme_ap_details>>>
25.5|45.2|864000|normal|15.4
<<<<>>>>
<<<<AP-Hostname-2>>>>
...
<<<extreme_summary>>>
access_points=25|total_clients=150
```

## 📊 Services & Metriken

### Pro Access Point:

| Service | Metriken | Levels |
|---------|----------|--------|
| **Extreme AP Status** | - | CRIT wenn disconnected |
| **Extreme AP Clients** | `clients_total`, `clients_2_4ghz`, `clients_5ghz` | WARN: 50, CRIT: 80 clients |
| **Extreme AP Details** | `cpu_utilization`, `memory_utilization`, `uptime`, `poe_power` | CPU/RAM: WARN 80%, CRIT 90% |

### Main Host:

| Service | Metriken | Info |
|---------|----------|------|
| **Extreme Infrastructure Summary** | `access_points`, `total_clients` | Gesamtübersicht |

## ⚙️ Threshold anpassen

### In WATO:

**Setup → Service monitoring rules**

1. **Extreme AP Clients Rule**:
   - Pfad: `Applications, Processes & Services → Network applications → Extreme AP Clients`
   - Anpassen: `clients_warn`, `clients_crit`

2. **Extreme AP Details Rule**:
   - Pfad: `Applications, Processes & Services → Hardware → Extreme AP Details`
   - Anpassen: `cpu_warn`, `cpu_crit`, `memory_warn`, `memory_crit`

### Beispiel Rule (YAML):

```yaml
- id: extreme_ap_clients_high_density
  description: Higher thresholds for high-density APs
  conditions:
    host_labels:
      site: campus
  value:
    clients_warn: 100
    clients_crit: 150
```

## 🔧 Troubleshooting

### Keine APs gefunden?

```bash
# Test mit Debug
~/local/share/check_mk/agents/special/agent_extreme_cloud_iq --username USER --password PASS --debug

# Checke API direkt:
curl -X POST https://api.extremecloudiq.com/login \
  -H "Content-Type: application/json" \
  -d '{"username":"USER","password":"PASS"}'
```

### Authentication failed?

- Prüfe Username/Password
- Versuche es mit API Token statt Username/Password
- Checke ob User die richtigen Permissions hat (mindestens "Monitor" Role)

### Piggyback Hosts werden nicht erstellt?

1. Check ob Agent erfolgreich läuft: `cmk --debug -vvn extreme-cloud-iq`
2. Prüfe Piggyback-Daten: `ls -la ~/tmp/check_mk/piggyback/`
3. Service Discovery auf Main Host ausführen

### Rate Limiting?

Die API hat ein Limit von **7500 requests / hour**. Bei vielen APs:
- Setze längere Check-Intervalle (z.B. 5 Minuten statt 1)
- In WATO: Normal check interval auf 5 minutes setzen

## 📁 Dateipfade (Check_MK 2.x)

```
/omd/sites/SITE/
├── local/
│   ├── share/check_mk/agents/special/
│   │   └── agent_extreme_cloud_iq          # Special Agent
│   └── lib/check_mk/base/plugins/agent_based/
│       └── extreme_check_plugins.py        # Check Plugins
```

## 🎯 Best Practices

1. **API Token verwenden** statt Username/Password (sicherer)
2. **Dedizierter Monitoring-User** in ExtremeCloud IQ erstellen
3. **Read-Only Permissions** für den User setzen
4. **Check-Intervalle erhöhen** bei vielen APs (Rate Limiting)
5. **Host-Labels** nutzen für AP-Gruppierung (z.B. nach Standort)

## 📝 Nächste Schritte

- [ ] Special Agent installiert
- [ ] Check Plugins installiert
- [ ] API Credentials erstellt
- [ ] Main Host angelegt
- [ ] Services discovered
- [ ] Thresholds angepasst
- [ ] Dashboards erstellt (optional)

## 💡 Weitere Features

Du kannst den Agent erweitern um:
- **Radio Stats** (Signal, Noise, Channel)
- **Rogue APs** Detection
- **Client History** & Roaming
- **SSID Monitoring**
- **Alarm/Events** aus der API

Sag Bescheid wenn du etwas davon brauchst! 🚀