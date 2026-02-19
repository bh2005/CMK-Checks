# SD-WAN Monitoring Konzept für Checkmk
# ======================================
# Umfassendes Monitoring-Konzept für Software-Defined WAN
# ======================================

## 📋 Executive Summary

SD-WAN (Software-Defined Wide Area Network) erfordert ein mehrdimensionales 
Monitoring-Konzept, das über klassisches WAN-Monitoring hinausgeht:

**Kernherausforderungen:**
- Mehrere parallele WAN-Links (MPLS, Internet, LTE, 5G)
- Dynamisches Path-Selection basierend auf Performance
- Application-Aware Routing
- Failover und Load Balancing
- Zentrale Orchestrierung vs. Edge-Autonomie

**Monitoring-Ziele:**
1. ✅ Verfügbarkeit jedes einzelnen WAN-Links
2. ✅ Performance-Metriken (Latency, Jitter, Packet Loss)
3. ✅ Aktiver Pfad und Failover-Events
4. ✅ Application Performance per Link
5. ✅ Tunnel-Status (IPsec, GRE, VXLAN)
6. ✅ Controller-Connectivity
7. ✅ Link-Kosten und Budget-Tracking

---

## 🏗️ Architektur-Übersicht

### Typische SD-WAN Topologie

```
                    [SD-WAN Controller]
                            |
                    (Management Plane)
                            |
        +-------------------+-------------------+
        |                   |                   |
   [Branch 1]          [Branch 2]          [Branch 3]
        |                   |                   |
    +---+---+           +---+---+           +---+---+
    |       |           |       |           |       |
  MPLS   Internet     MPLS   LTE         Internet 5G
  (Path 1) (Path 2)  (Path 1) (Path 2)  (Path 1) (Path 2)
```

### Monitoring-Ebenen

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: Physical Links (MPLS, DSL, LTE, 5G)          │
├─────────────────────────────────────────────────────────┤
│ Layer 2: Overlay Tunnels (IPsec, GRE, VXLAN)          │
├─────────────────────────────────────────────────────────┤
│ Layer 3: Path Selection & Load Balancing               │
├─────────────────────────────────────────────────────────┤
│ Layer 4: Application Performance (SLA-Monitoring)      │
├─────────────────────────────────────────────────────────┤
│ Layer 5: Controller & Orchestration                    │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Monitoring-Dimensionen

### 1. **Link-Level Monitoring**

Jeder physische WAN-Link benötigt eigene Überwachung:

#### Zu überwachende Metriken:

| Metrik | Bedeutung | Schwellwert (Beispiel) |
|--------|-----------|------------------------|
| **Bandwidth Utilization** | Auslastung | WARN: 70%, CRIT: 85% |
| **Latency (RTT)** | Round-Trip-Time | WARN: 100ms, CRIT: 200ms |
| **Jitter** | Latenz-Schwankungen | WARN: 20ms, CRIT: 50ms |
| **Packet Loss** | Paketverlust | WARN: 1%, CRIT: 3% |
| **Interface Errors** | CRC, Collisions | WARN: 10/min, CRIT: 50/min |
| **Link State** | Up/Down Status | DOWN = CRIT |
| **MOS Score** | Mean Opinion Score (VoIP) | WARN: <3.5, CRIT: <3.0 |

#### Checkmk Services:

```
✓ Interface eth0 (MPLS)
  - Bandwidth: 45% (45 Mbit/s von 100 Mbit/s)
  - Latency: 25ms
  - Packet Loss: 0.1%
  
✓ Interface eth1 (Internet)
  - Bandwidth: 78% (78 Mbit/s von 100 Mbit/s)
  - Latency: 15ms
  - Packet Loss: 0.3%
  
⚠ Interface wwan0 (LTE Backup)
  - Link State: Down (Standby)
  - Last Failover: 2 days ago
```

---

### 2. **Tunnel-Monitoring**

SD-WAN nutzt Overlay-Tunnels über Underlay-Links:

#### IPsec/GRE/VXLAN Tunnel Status:

| Parameter | Monitoring | Alarmierung |
|-----------|-----------|-------------|
| **Tunnel State** | Up/Down/Degraded | DOWN = CRIT |
| **Encryption Status** | Active/Inactive | INACTIVE = WARN |
| **SA Lifetime** | Remaining time | <10min = WARN |
| **Tunnel Traffic** | Bytes/Packets | Baseline-Abweichung |
| **Tunnel Latency** | End-to-End RTT | >150ms = WARN |
| **Path MTU** | Fragmentation | <1400 = WARN |

#### Checkmk Services:

```
✓ SD-WAN Tunnel: Branch01 → HQ via MPLS
  - State: UP
  - Encryption: AES-256-GCM (active)
  - SA Lifetime: 2h 15min remaining
  - Tunnel Traffic: 25 Mbit/s
  - End-to-End Latency: 28ms

⚠ SD-WAN Tunnel: Branch01 → HQ via Internet
  - State: UP (Backup)
  - Priority: Secondary
  - Last Used: 3 days ago
  - Standby Traffic: 0 Mbit/s
```

---

### 3. **Path Selection Monitoring**

Kritisch: Welcher Pfad wird aktuell für welche Application genutzt?

#### Application-Aware Routing:

| Application | Priorität | Bevorzugter Pfad | Failover-Pfad |
|-------------|-----------|------------------|---------------|
| VoIP (SIP) | High | MPLS (low latency) | Internet |
| Video (Teams) | High | MPLS | Internet |
| File Transfer | Low | Internet (günstig) | MPLS |
| Backup | Lowest | Internet (nachts) | - |

#### Zu überwachen:

- **Active Path per Application**
- **Path Changes (Failover-Events)**
- **Policy Compliance** (läuft Traffic auf dem richtigen Pfad?)
- **Load Distribution** (bei Load Balancing)

#### Checkmk Services:

```
✓ SD-WAN Path Selection
  - Active Primary Path: MPLS (85% traffic)
  - Active Secondary Path: Internet (15% traffic)
  - Failover Events: 0 in last 24h
  - Policy Violations: 0

✓ Application Routing: VoIP
  - Current Path: MPLS
  - SLA Compliance: OK (Latency: 25ms, Jitter: 5ms, Loss: 0%)
  - Alternative Paths Available: 1 (Internet)

⚠ Application Routing: File Transfer
  - Current Path: MPLS (should be Internet!)
  - Reason: Internet link degraded
  - Policy Violation: Active since 15min
```

---

### 4. **SLA-Monitoring**

Service Level Agreements pro Application und Link:

#### SLA-Definition Beispiel:

```yaml
VoIP_SLA:
  latency:
    target: <50ms
    warn: 80ms
    crit: 100ms
  jitter:
    target: <10ms
    warn: 20ms
    crit: 30ms
  packet_loss:
    target: <0.5%
    warn: 1%
    crit: 2%
  availability:
    target: 99.9%
    warn: 99.5%
    crit: 99%

Video_SLA:
  bandwidth:
    target: >5 Mbit/s
    warn: 3 Mbit/s
    crit: 2 Mbit/s
  latency:
    target: <100ms
    warn: 150ms
    crit: 200ms
```

#### Checkmk Services:

```
✓ SLA Compliance: VoIP
  - Availability: 99.95% (Target: 99.9%)
  - Avg Latency: 28ms (Target: <50ms)
  - Avg Jitter: 8ms (Target: <10ms)
  - Packet Loss: 0.2% (Target: <0.5%)
  - SLA Status: COMPLIANT

⚠ SLA Compliance: Video Conferencing
  - Availability: 99.2% (Target: 99.5%)
  - Avg Latency: 45ms (Target: <100ms)
  - Bandwidth: 4.2 Mbit/s (Target: >5 Mbit/s)
  - SLA Status: DEGRADED (Bandwidth below target)
```

---

### 5. **Controller-Monitoring**

SD-WAN Controller als Single Point of Failure:

#### Controller Metrics:

| Metrik | Beschreibung | Alarmierung |
|--------|--------------|-------------|
| **Controller Reachability** | Erreichbarkeit vom Edge | CRIT: Down |
| **API Latency** | Response Time | WARN: >1s |
| **Edge Registration** | Anzahl aktiver Edges | Baseline |
| **Policy Push Success** | Erfolgreiche Updates | <100% = WARN |
| **Certificate Validity** | Verbleibende Laufzeit | <30d = WARN |

#### Checkmk Services:

```
✓ SD-WAN Controller (controller.sdwan.local)
  - Status: Reachable
  - API Latency: 45ms
  - Registered Edges: 127/127 (100%)
  - Last Policy Update: 2h ago (Success: 100%)
  - Certificate Expiry: 89 days

✓ Controller HA Status
  - Primary: Active
  - Secondary: Standby (healthy)
  - Last Failover: Never
  - Sync Status: In-Sync
```

---

### 6. **Failover & High Availability**

Failover-Events und -Historie:

#### Zu tracken:

- **Failover-Ereignisse** (Wann? Warum? Wie lange?)
- **Mean Time Between Failures (MTBF)**
- **Mean Time To Repair (MTTR)**
- **Failback-Erfolg** (zurück zum Primary Path)

#### Checkmk Services:

```
✓ SD-WAN Failover History (Branch01)
  - Last Failover: 2 days ago
  - Reason: MPLS Link Down (15min outage)
  - Failback: Successful after 20min
  - Total Failovers (30d): 3
  - MTBF: 10 days
  - MTTR: 18 minutes (avg)

⚠ SD-WAN Failover History (Branch05)
  - Last Failover: 4 hours ago
  - Reason: High Packet Loss on Primary (>5%)
  - Failback: FAILED (Primary still degraded)
  - Current Path: Internet (Secondary)
  - Failover Count (24h): 5 (UNUSUAL!)
```

---

### 7. **Link-Kosten & Budget**

Volumen-basierte Links (LTE/5G) benötigen Budget-Tracking:

#### Kosten-Tracking:

| Link | Typ | Inklusiv-Volumen | Aktueller Verbrauch | Kosten/GB | Forecast |
|------|-----|------------------|---------------------|-----------|----------|
| LTE-1 | Backup | 10 GB/Monat | 8.2 GB | 0€ | OK |
| LTE-1 | Overage | Unlimited | - | 5€/GB | - |
| 5G-1 | Primary | 100 GB/Monat | 78 GB | 0€ | 95 GB EOM |

#### Checkmk Services:

```
✓ Link Budget: LTE Backup (Branch01)
  - Monthly Quota: 10 GB
  - Used: 8.2 GB (82%)
  - Remaining: 1.8 GB
  - Days Left: 5
  - Forecast: Within budget
  - Overage Cost: 0€

⚠ Link Budget: 5G Primary (Branch03)
  - Monthly Quota: 100 GB
  - Used: 92 GB (92%)
  - Remaining: 8 GB
  - Days Left: 3
  - Forecast: OVERAGE EXPECTED (105 GB)
  - Estimated Overage Cost: 25€ (5 GB × 5€)
```

---

## 🛠️ Implementierung in Checkmk

### Monitoring-Architektur

```
┌─────────────────────────────────────────────────────────┐
│ Checkmk Server                                          │
│  ├─ Special Agents (SD-WAN APIs)                       │
│  ├─ Active Checks (Synthetic Monitoring)               │
│  └─ Agent Plugins (Edge Devices)                       │
└─────────────────────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
    [Controller]   [Edge 1]       [Edge 2]
         │              │              │
         └──────────────┴──────────────┘
              (SD-WAN Fabric)
```

### Datenquellen

#### 1. **SNMP (Standard Interface Monitoring)**

```python
# Standard IF-MIB für Interfaces
check_plugin_interface = CheckPlugin(
    name="interfaces",
    # Bandwidth, Errors, Discards
)

# Erweitert mit SD-WAN spezifischen OIDs
# Beispiel: Cisco SD-WAN (Viptela)
snmp_section_cisco_sdwan_links = SimpleSNMPSection(
    name="cisco_sdwan_links",
    detect=exists(".1.3.6.1.4.1.41916.1.1"),  # Cisco SD-WAN Enterprise OID
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.41916.3.2.1",
        oids=[
            "2",  # Link Name
            "3",  # Link State
            "4",  # Link Type (MPLS/Internet/LTE)
            "5",  # Latency
            "6",  # Jitter
            "7",  # Packet Loss
            "8",  # Bandwidth
        ],
    ),
)
```

#### 2. **REST API (Controller)**

```python
# Special Agent für SD-WAN Controller
# Beispiel: Fortinet SD-WAN, Cisco Viptela, VMware VeloCloud

special_agent_sdwan_controller = SpecialAgent(
    name="sdwan_controller",
    argument_function=agent_sdwan_arguments,
)

def agent_sdwan_arguments(params, hostname, ipaddress):
    return [
        "--controller", params["controller_url"],
        "--api-key", params["api_key"],
        "--tenant", params.get("tenant_id", ""),
    ]
```

**API-Endpoints:**
- `/api/v1/edges` - Edge Device Status
- `/api/v1/links` - Link Status & Metrics
- `/api/v1/tunnels` - Tunnel Status
- `/api/v1/paths` - Active Paths
- `/api/v1/applications` - Application Routing
- `/api/v1/events` - Failover Events

#### 3. **Active Checks (Synthetic Monitoring)**

```python
# Synthetische End-to-End Tests
active_check_sdwan_path = ActiveCheck(
    name="check_sdwan_path_quality",
    argument_function=...,
)

# Testet:
# - Latency (ICMP/UDP)
# - Packet Loss (Flood-Test)
# - Jitter (Continuous Pings)
# - Bandwidth (iPerf3)
# - Application Simulation (HTTP/SIP/RTP)
```

#### 4. **Agent Plugins (Edge Devices)**

```bash
#!/bin/bash
# /usr/lib/check_mk_agent/plugins/sdwan_edge_status

# Lokale Checks auf Edge-Device
echo "<<<sdwan_edge_local>>>"

# Active Interfaces
ip -j link show | jq -r '.[] | select(.operstate=="UP") | .ifname'

# Tunnel Status
ip -j tunnel show

# Routing Table (für Path Selection)
ip route show table all | grep "metric"

# iptables rules (für Application Routing)
iptables -t mangle -L -n -v
```

---

## 📈 Dashboard-Konzept

### Level 1: Executive Dashboard

```
┌─────────────────────────────────────────────────────────┐
│ SD-WAN Health Overview                                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🟢 Overall Status: HEALTHY                            │
│                                                         │
│  ┌──────────────┬──────────────┬──────────────┐       │
│  │ Total Links  │ Active Links │ Backup Links │       │
│  │     127      │     125      │      2       │       │
│  └──────────────┴──────────────┴──────────────┘       │
│                                                         │
│  ┌──────────────┬──────────────┬──────────────┐       │
│  │ SLA Comply.  │ Tunnel UP    │ Failovers/24h│       │
│  │    98.5%     │    124/127   │      3       │       │
│  └──────────────┴──────────────┴──────────────┘       │
│                                                         │
│  Recent Events:                                         │
│  ⚠ Branch-05: High Packet Loss on MPLS (10min ago)    │
│  ℹ Branch-12: LTE Backup activated (2h ago)           │
│  ✓ Branch-03: Policy update successful (4h ago)       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Level 2: Site-Specific Dashboard

```
┌─────────────────────────────────────────────────────────┐
│ Branch-01 SD-WAN Status                                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Links:                                                 │
│  ┌────────────────────────────────────────────┐       │
│  │ 🟢 MPLS (Primary)     │ 45%  │ 28ms │ 0.1% │       │
│  │ 🟢 Internet (Active)  │ 78%  │ 15ms │ 0.3% │       │
│  │ 🟡 LTE (Standby)      │  0%  │  -   │  -   │       │
│  └────────────────────────────────────────────┘       │
│                                                         │
│  Tunnels:                                               │
│  ✓ HQ via MPLS (Primary)    - 25 Mbit/s               │
│  ✓ HQ via Internet (Backup) -  0 Mbit/s               │
│  ✓ Branch-02 via MPLS       -  5 Mbit/s               │
│                                                         │
│  Application Performance:                               │
│  ┌────────────────────────────────────────────┐       │
│  │ App        │ Path     │ Latency │ SLA      │       │
│  ├────────────────────────────────────────────┤       │
│  │ VoIP       │ MPLS     │ 25ms    │ ✓ OK     │       │
│  │ Video      │ MPLS     │ 28ms    │ ✓ OK     │       │
│  │ Web        │ Internet │ 15ms    │ ✓ OK     │       │
│  │ Backup     │ Internet │ 18ms    │ ✓ OK     │       │
│  └────────────────────────────────────────────┘       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Level 3: Link-Detail Dashboard

```
┌─────────────────────────────────────────────────────────┐
│ Link Detail: MPLS (Branch-01)                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Real-time Metrics:                                     │
│  ┌─────────────────────────────────────────┐          │
│  │ [Bandwidth Graph - Last 24h]            │          │
│  │  Current: 45 Mbit/s                     │          │
│  │  Peak: 89 Mbit/s (14:30)               │          │
│  │  Average: 52 Mbit/s                     │          │
│  └─────────────────────────────────────────┘          │
│                                                         │
│  ┌─────────────────────────────────────────┐          │
│  │ [Latency Graph - Last 24h]              │          │
│  │  Current: 28ms                           │          │
│  │  Max: 45ms                               │          │
│  │  Average: 30ms                           │          │
│  └─────────────────────────────────────────┘          │
│                                                         │
│  SLA Compliance (Last 30 days):                         │
│  Availability: 99.95%                                   │
│  Latency SLA: 99.8% compliant                          │
│  Packet Loss SLA: 100% compliant                       │
│                                                         │
│  Tunnel Traffic Split:                                  │
│  HQ:         85% (21 Mbit/s)                           │
│  Branch-02:  10% ( 3 Mbit/s)                           │
│  Branch-03:   5% ( 1 Mbit/s)                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🚨 Alerting-Strategie

### Alert-Hierarchie

```
Priority 1 (CRITICAL - Sofort):
├─ Kompletter Site-Ausfall (alle Links down)
├─ Controller unreachable
├─ Keine aktiven Tunnel zu HQ
└─ SLA-Verletzung (kritische Application)

Priority 2 (WARNING - 15min):
├─ Einzelner Link down (Backup verfügbar)
├─ Failover auf Backup-Link
├─ Hohe Latenz (>Threshold)
├─ Budget-Warnung (>90% verbraucht)
└─ Tunnel flapping (>3 Änderungen/h)

Priority 3 (INFO - kein Alert):
├─ Geplanter Link-Wechsel
├─ Policy-Update erfolgreich
└─ Regelmäßige Reports
```

### Alert-Gruppierung

```yaml
Alert Groups:
  - name: "SD-WAN Critical Sites"
    contacts: [noc-team, sd-wan-team]
    conditions:
      - all_links_down
      - controller_unreachable
      - no_active_tunnels
    
  - name: "SD-WAN Performance Degradation"
    contacts: [sd-wan-team]
    conditions:
      - high_latency
      - packet_loss_threshold
      - sla_violation
    
  - name: "SD-WAN Capacity"
    contacts: [capacity-team]
    conditions:
      - link_utilization_high
      - budget_warning
      - bandwidth_forecast
```

### Context-Aware Alerting

```python
# Beispiel: Unterdrücke "Link Down" Alert wenn Backup aktiv ist
if link_primary.state == "DOWN" and link_backup.state == "UP":
    alert.severity = "WARNING"  # statt CRITICAL
    alert.message = "Primary link down, running on backup (no service impact)"
```

---

## 📊 Reporting

### Automatische Reports

#### 1. **Daily Health Report**
- Verfügbarkeit pro Site (99.x%)
- Failover-Ereignisse
- Top 5 Sites nach Latenz
- SLA Compliance Summary

#### 2. **Weekly Performance Report**
- Bandwidth-Trends
- Link-Utilization Heatmap
- Application Performance pro Site
- Tunnel-Stability Metrics

#### 3. **Monthly Executive Report**
- Overall SD-WAN Health Score
- SLA Compliance vs. Target
- Cost Analysis (Backup-Link-Nutzung)
- Top Issues & Recommendations

#### 4. **Budget Report (LTE/5G)**
- Verbrauch pro Site
- Overage-Kosten
- Forecast nächster Monat
- Optimierungsvorschläge

---

## 🔧 Wartung & Lifecycle

### Proactive Monitoring

```
Predictive Alerts:
├─ Bandbreiten-Forecast: "Link wird in 7 Tagen zu 100% ausgelastet"
├─ Budget-Forecast: "LTE-Backup wird Limit in 3 Tagen überschreiten"
├─ Certificate Expiry: "Controller-Zertifikat läuft in 30 Tagen ab"
└─ Hardware EOL: "Edge-Device EOL in 6 Monaten"
```

### Capacity Planning

```sql
-- Beispiel: Bandwidth Growth Analysis
SELECT 
    site,
    AVG(bandwidth_utilization) as avg_util,
    MAX(bandwidth_utilization) as peak_util,
    (peak_util - avg_util) as burst_capacity
FROM link_metrics
WHERE timestamp > NOW() - INTERVAL '90 days'
GROUP BY site
HAVING peak_util > 80
ORDER BY peak_util DESC;
```

---

## 🎯 Best Practices

### 1. **Baseline Establishment**
- Sammle 30 Tage Daten vor Alerting-Aktivierung
- Definiere "Normal" pro Site
- Berücksichtige Tages-/Wochenzyklen

### 2. **Thresholds**
```
Latency Thresholds (Beispiel):
- VoIP: WARN 50ms, CRIT 100ms
- Video: WARN 100ms, CRIT 150ms
- Data: WARN 150ms, CRIT 200ms

Packet Loss:
- VoIP: WARN 0.5%, CRIT 1%
- Video: WARN 1%, CRIT 2%
- Data: WARN 2%, CRIT 5%
```

### 3. **Synthetic Monitoring**
- Kontinuierliche End-to-End Tests
- Application-Simulation (VoIP, Video)
- Proactive vs. Reactive

### 4. **Documentation**
- Runbooks für Failover-Szenarien
- Escalation Matrix
- Contact List (Vendor, ISP)

---

## 📦 Deliverables

### Phase 1: Foundation (Woche 1-2)
- ✅ Interface Monitoring (SNMP)
- ✅ Basic Link Metrics (Bandwidth, Errors)
- ✅ Controller Reachability

### Phase 2: Core (Woche 3-4)
- ✅ Tunnel Status Monitoring
- ✅ Latency/Jitter/Packet Loss
- ✅ Failover Event Detection

### Phase 3: Advanced (Woche 5-8)
- ✅ Application-Aware Monitoring
- ✅ SLA Tracking
- ✅ Path Selection Monitoring
- ✅ Budget Tracking

### Phase 4: Optimization (Woche 9-12)
- ✅ Predictive Alerting
- ✅ Capacity Planning
- ✅ Executive Reporting
- ✅ API Integration (Automation)

---

## 🔗 Integration-Punkte

### Ticketing (ITSM)
```
Auto-Ticket Creation:
├─ Link Down → Priority 1 Incident
├─ SLA Violation → Priority 2 Incident
└─ Budget Overage → Change Request
```

### ChatOps (Slack/Teams)
```
Notifications:
├─ Critical: Immediate ping @on-call
├─ Warning: Channel notification
└─ Info: Silent update
```

### Automation (Ansible/Terraform)
```
Auto-Remediation:
├─ Tunnel flapping → Restart tunnel
├─ High utilization → Activate backup
└─ Controller unreachable → Switch to secondary
```

---

## ✅ Success Metrics

**KPIs für erfolgreiches SD-WAN Monitoring:**

| Metrik | Ziel | Messung |
|--------|------|---------|
| **MTTD** (Mean Time To Detect) | <5 min | Ausfallszeit bis Alert |
| **MTTR** (Mean Time To Repair) | <30 min | Ausfallszeit gesamt |
| **False Positive Rate** | <5% | Fehlalarme / Alerts |
| **SLA Compliance** | >99.5% | Uptime pro Link |
| **Alert Coverage** | 100% | Echte Ausfälle mit Alert |

---

## 📚 Weiterführende Ressourcen

- Checkmk SD-WAN Plugin Repository
- Vendor-Spezifische API-Dokumentation
- SD-WAN Best Practices (IETF, MEF)
- Performance Monitoring Standards (ITU-T Y.1540)

---

**Dokument-Version:** 1.0  
**Letzte Aktualisierung:** 2026-02-19  
**Autor:** SD-WAN Monitoring Konzept-Team