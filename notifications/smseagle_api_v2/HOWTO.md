# SMSEagle Notification Plugin - Installation & Setup

## 📦 Was hast du bekommen?

Ein **vollständiges Check_MK Notification Plugin** für SMSEagle mit:

✅ **Notification Plugin** - Sendet Alerts via SMS/TTS/Wave
✅ **WATO GUI Integration** - Konfiguration über Web-Interface
✅ **Failover Support** - Automatischer Fallback zum Backup-Server
✅ **Flexible Recipients** - Phone, Contacts, Groups oder Kombination
✅ **Custom Templates** - Eigene Nachrichtenformate
✅ **Production Ready** - Error-Handling, Logging, SSL Support

## 🚀 Installation

### Voraussetzungen

- Check_MK Version 2.0 oder höher
- SMSEagle Device mit API v2
- API Access Token (siehe unten)

### Schritt 1: Notification Plugin installieren

```bash
# Als site-user
OMD_SITE="deine_site"  # Anpassen!

# Plugin kopieren
sudo cp smseagle /omd/sites/$OMD_SITE/local/share/check_mk/notifications/
sudo chmod +x /omd/sites/$OMD_SITE/local/share/check_mk/notifications/smseagle
sudo chown $OMD_SITE:$OMD_SITE /omd/sites/$OMD_SITE/local/share/check_mk/notifications/smseagle
```

### Schritt 2: WATO Integration installieren

```bash
# WATO Plugin kopieren
sudo cp smseagle_notifications.py /omd/sites/$OMD_SITE/local/share/check_mk/web/plugins/wato/
sudo chown $OMD_SITE:$OMD_SITE /omd/sites/$OMD_SITE/local/share/check_mk/web/plugins/wato/smseagle_notifications.py
```

### Schritt 3: Apache neu laden

```bash
omd reload apache
```

### Schritt 4: Browser Cache leeren

Im Browser: `Ctrl + Shift + R` (Hard Refresh)

## 🔑 SMSEagle Access Token erstellen

### In SMSEagle Web-Interface:

1. **Login** → http://your-smseagle-ip
2. **Settings** → **API** → **Access Tokens**
3. **Add new token**:
   - Name: `checkmk-monitoring`
   - Permissions: `Send SMS`, `Send Calls`
4. **Speichern** und Token kopieren!

## 📱 Notification Rule erstellen (WATO GUI)

### Setup → Notifications → Add rule

#### 1. **Notification Method**: SMSEagle

#### 2. **Primary Server Configuration**:
```
Primary SMSEagle URL: http://192.168.1.100
Primary Access Token: your-token-here
```

#### 3. **Secondary Server (optional, für Failover)**:
```
Secondary SMSEagle URL: http://192.168.1.200
Secondary Access Token: backup-token-here
```

#### 4. **Message Type** (Dropdown):
- ○ **SMS Text Message** (Standard)
- ○ **Voice Call (Text-to-Speech)** - Ruft an und liest Text vor
- ○ **Voice Call (WAV File)** - Spielt hochgeladene WAV-Datei ab
  - Wave File ID: `1` (WAV-Datei in SMSEagle hochladen)

#### 5. **Modem Number**: `1` (oder 2-4, je nach Device)

#### 6. **SSL Certificate Verification**: 
- ● Enable (recommended)
- ○ Disable (insecure) - nur bei Self-Signed Certs

#### 7. **Custom Message Template** (optional):
```
Alert: $HOSTNAME$ $SERVICEDESC$ is $SERVICESTATE$
Output: $SERVICEOUTPUT$
Time: $SHORTDATETIME$
```

#### 8. **Conditions** (Beispiele):

**Option A: Alle Kontakte mit Pager-Feld**
```
Contact selection: All contacts
Filter: Only contacts with pager field set
```

**Option B: Spezifische Kontakte**
```
Contact selection: The following contacts...
  ☑ admin
  ☑ oncall-engineer
```

**Option C: Nach Host/Service**
```
Match host/service: 
  Folder: /Production/Critical/
Match notification type:
  ☑ Problem notifications
  ☑ Recovery notifications
```

## 👤 User Pager Field konfigurieren

### Setup → Users → Edit user → Contact Settings

**Pager / SMS Number Feld:**

### Format-Optionen:

#### 1. **Direkte Telefonnummer**:
```
+491234567890
```

#### 2. **SMSEagle Contact IDs**:
```
contacts:12,15
```
(Sendet an Contact ID 12 und 15 in SMSEagle)

#### 3. **SMSEagle Group IDs**:
```
groups:1,2
```
(Sendet an alle Mitglieder von Group 1 und 2)

#### 4. **Kombination** (Semikolon-getrennt):
```
+491234567890;groups:1
```
(Sendet an Telefon UND Group)

```
+491234567890;contacts:12;groups:1,2
```
(Telefon + Contact 12 + Groups 1,2)

## 📝 Message Template Variablen

Verfügbare Platzhalter für Custom Templates:

### Host-Variablen:
- `$HOSTNAME$` - Hostname
- `$HOSTALIAS$` - Host Alias
- `$HOSTADDRESS$` - IP-Adresse
- `$HOSTSTATE$` - UP, DOWN, UNREACHABLE
- `$HOSTSHORTSTATE$` - U, D
- `$HOSTOUTPUT$` - Check Output

### Service-Variablen:
- `$SERVICEDESC$` - Service Name
- `$SERVICESTATE$` - OK, WARNING, CRITICAL, UNKNOWN
- `$SERVICESHORTSTATE$` - O, W, C, U
- `$SERVICEOUTPUT$` - Check Output

### Weitere:
- `$NOTIFICATIONTYPE$` - PROBLEM, RECOVERY, ACKNOWLEDGEMENT
- `$SHORTDATETIME$` - Datum/Zeit
- `$CONTACTNAME$` - Empfänger Name

### Template-Beispiele:

#### Kurz & Prägnant (für SMS):
```
[$SERVICESHORTSTATE$] $HOSTNAME$: $SERVICEOUTPUT$
```

#### Ausführlich (für TTS):
```
Monitoring Alert.
Host: $HOSTNAME$.
Service: $SERVICEDESC$.
State: $SERVICESTATE$.
Output: $SERVICEOUTPUT$.
Time: $SHORTDATETIME$.
```

#### Mit Kontext:
```
🚨 Alert: $NOTIFICATIONTYPE$
Host: $HOSTNAME$ ($HOSTADDRESS$)
Service: $SERVICEDESC$
Status: $SERVICESTATE$
$SERVICEOUTPUT$
```

## 🧪 Testen

### 1. Test-Notification über GUI

**Setup → Notifications → Test notifications**

```
Contact: admin
Host: test-host
Service: CPU Load
State: WARNING
Output: CPU Load is 85%
```

**Send test notification** → Check Log

### 2. Manueller CLI Test

```bash
# Als site-user
OMD[site]$ cd ~/local/share/check_mk/notifications/

# Test-Variablen setzen
export NOTIFY_CONTACTPAGER="+491234567890"
export NOTIFY_HOSTNAME="test-host"
export NOTIFY_WHAT="SERVICE"
export NOTIFY_SERVICEDESC="CPU Load"
export NOTIFY_SERVICESHORTSTATE="W"
export NOTIFY_SERVICEOUTPUT="Load average: 15.2, 14.8, 13.5"
export NOTIFY_PARAMETER_PRIMARY_URL="http://192.168.1.100"
export NOTIFY_PARAMETER_PRIMARY_TOKEN="your-token-here"
export NOTIFY_PARAMETER_MESSAGE_TYPE="sms"
export NOTIFY_PARAMETER_MODEM_NO="1"

# Plugin ausführen
./smseagle
```

### 3. Log prüfen

```bash
tail -f ~/var/log/smseagle_notifications.log
```

**Erwartete Ausgabe:**
```
2025-01-08 14:30:15 - INFO - SMSEagle Notification Plugin called
2025-01-08 14:30:15 - INFO - Host: test-host
2025-01-08 14:30:15 - INFO - Service: CPU Load
2025-01-08 14:30:15 - INFO - State: W
2025-01-08 14:30:15 - INFO - Message type: sms
2025-01-08 14:30:15 - INFO - Sending request to http://192.168.1.100/api/v2/messages/sms
2025-01-08 14:30:16 - INFO - API Response: {'status': 'queued', 'id': '12345'}
2025-01-08 14:30:16 - INFO - Message queued successfully. ID: 12345
2025-01-08 14:30:16 - INFO - Notification sent successfully
```

## 🎯 Erweiterte Konfiguration

### Mehrere Notification Rules

**Rule 1: Critical Alerts → Voice Call**
```
Notification Method: SMSEagle
Message Type: Voice Call (TTS)
Conditions:
  - Service states: CRITICAL only
  - Folders: /Production/
```

**Rule 2: Warnings → SMS**
```
Notification Method: SMSEagle
Message Type: SMS Text Message
Conditions:
  - Service states: WARNING only
```

**Rule 3: Recovery → SMS mit Custom Template**
```
Notification Method: SMSEagle
Message Type: SMS
Custom Template: ✅ $HOSTNAME$ $SERVICEDESC$ recovered
Conditions:
  - Notification type: Recovery
```

### Eskalation mit Failover

**Rule Priority:**

1. **Priority 1**: SMS an Oncall (Primary SMSEagle)
2. **Priority 2**: Voice Call nach 5 min (Secondary SMSEagle)
3. **Priority 3**: SMS an Manager nach 15 min

### Zeitbasierte Rules

```
Rule: Business Hours → SMS
Conditions:
  - Time period: workhours (Mon-Fri 08:00-18:00)
  - Message Type: SMS

Rule: After Hours → Voice Call
Conditions:
  - Time period: nonworkhours
  - Message Type: Voice Call (TTS)
```

## 🔧 Troubleshooting

### Notification wird nicht gesendet

#### Check 1: User hat Pager Field?
```
Setup → Users → admin → Pager field set?
```

#### Check 2: Notification Rule Conditions?
```
Setup → Notifications → Check conditions match
```

#### Check 3: Log prüfen
```bash
tail -f ~/var/log/smseagle_notifications.log
tail -f ~/var/log/notify.log
```

### API Connection Errors

#### Test API manuell:
```bash
curl -X POST http://192.168.1.100/api/v2/messages/sms \
  -H "Content-Type: application/json" \
  -H "access-token: YOUR-TOKEN" \
  -d '{
    "to": ["+491234567890"],
    "text": "Test from curl",
    "modem_no": 1
  }'
```

**Erwartete Response:**
```json
{
  "status": "queued",
  "number": "+491234567890",
  "id": "12345"
}
```

### Failover wird nicht ausgelöst

Check Log:
```
Primary server failed. Trying secondary server...
```

Wenn nicht → Secondary URL/Token korrekt gesetzt?

### SSL Certificate Errors

Wenn Self-Signed Cert:
```
SSL Certificate Verification: Disable
```

Oder besser: Installiere richtiges Cert auf SMSEagle

## 📊 Message Type Vergleich

| Type | Use Case | Pros | Cons |
|------|----------|------|------|
| **SMS** | Standard Alerts | ✅ Schnell<br>✅ Überall empfangbar<br>✅ Günstig | ⚠️ Zeichenlimit (160)<br>⚠️ Kann übersehen werden |
| **TTS Call** | Kritische Alerts | ✅ Schwer zu ignorieren<br>✅ Lange Messages möglich | ⚠️ Teuer<br>⚠️ Kann nerven |
| **Wave Call** | Spezielle Sounds | ✅ Wiedererkennbar<br>✅ Verschiedene Prioritäten | ⚠️ WAV Upload nötig<br>⚠️ Teuer |

## 💡 Best Practices

### 1. Failover konfigurieren
Immer Secondary Server einrichten für High Availability

### 2. Templates kurz halten
SMS hat 160 Zeichen Limit - Template testen!

### 3. Voice Calls sparsam nutzen
Nur für CRITICAL/DOWN States

### 4. Groups nutzen
Statt einzelne Nummern → SMSEagle Groups verwalten

### 5. Logging aktivieren
Hilft beim Debugging:
```bash
tail -f ~/var/log/smseagle_notifications.log
```

### 6. Test Notifications
Regelmäßig testen ob alles funktioniert

### 7. Rate Limiting beachten
SMSEagle hat limits - nicht zu viele Notifications

## 📁 Dateipfade

```
/omd/sites/SITE/
├── local/
│   └── share/check_mk/
│       ├── notifications/
│       │   └── smseagle                    # Notification Plugin
│       └── web/plugins/wato/
│           └── smseagle_notifications.py   # WATO Integration
└── var/log/
    └── smseagle_notifications.log          # Log File
```

## ✅ Checkliste

- [ ] Notification Plugin installiert
- [ ] WATO Integration installiert
- [ ] Apache neu geladen
- [ ] SMSEagle Access Token erstellt
- [ ] Notification Rule in WATO erstellt
- [ ] User Pager Fields konfiguriert
- [ ] Test Notification gesendet
- [ ] Log geprüft - alles OK
- [ ] Failover getestet (optional)
- [ ] Custom Templates erstellt (optional)

## 🎉 Fertig!

Dein Check_MK sendet jetzt Notifications via SMSEagle!

**Features die du jetzt hast:**
- ✅ SMS, TTS & Wave Support
- ✅ Automatischer Failover
- ✅ Flexible Recipients (Phone/Contacts/Groups)
- ✅ Custom Message Templates
- ✅ Komplette WATO GUI Integration
- ✅ Production-Ready mit Logging

**Brauchst du noch:**
- 📊 Notification Statistics Dashboard?
- 🔔 Eskalation Rules?
- 📱 Mobile App Integration?
