```markdown
---
sidebar_position: 1
sidebar_label: Rust Client – HOWTO
title: ExtremeCloudIQ → Redis Sync (Rust)
slug: /rust-client
---

# ExtremeCloudIQ → Redis Sync Tool (Rust Edition)

**eciq_ap_to_redis** – Der schnellste, sicherste und modernste Weg, alle Access Points + aktuelle SSIDs aus ExtremeCloudIQ in Redis zu cachen.

Perfekt für Checkmk, Dashboards oder eigene Monitoring-Tools.

## Warum Rust?

| Vorteil                  | Rust-Version              | Python-Version |
|--------------------------|---------------------------|----------------|
| Laufzeitgeschwindigkeit  | 5–20× schneller           | langsam        |
| RAM-Verbrauch            | ~15 MB                    | ~120 MB        |
| Binary-Größe             | 5–7 MB (statisch)         | + Python + venv |
| Keine Abhängigkeiten     | Ja                        | Nein           |
| Type-Safety              | Compile-Time              | Runtime-Fehler |

## Features

- Automatisches Login + Token-Caching
- Robustes Rate-Limit-Handling (429 → Retry-After)
- Vollständige Pagination (10.000+ APs kein Problem)
- Unique SSIDs pro AP (inkl. Status, Policy, BSSID)
- Redis-Speicherung als Hash + separate SSID-Liste
- 100 % async (Tokio)
- .env + CLI mit `clap`
- Structured Logging mit `tracing`

## Installation

### 1. Als statisches Binary (empfohlen)

```bash
git clone https://github.com/deinuser/CMK-Checks.git
cd CMK-Checks/extremecloudiq/rustclient
cargo build --release
sudo cp target/release/eciq_ap_to_redis /usr/local/bin/
```

→ Läuft überall, auch ohne Rust!

### 2. Docker

```dockerfile
FROM rust:1.82-alpine AS builder
WORKDIR /app
COPY . .
RUN cargo build --release

FROM alpine:latest
COPY --from=builder /app/target/release/eciq_ap_to_redis /usr/local/bin/
CMD ["eciq_ap_to_redis"]
```

```bash
docker build -t eciq-ap-to-redis .
docker run --env-file .env eciq-ap-to-redis
```

## Konfiguration (.env)

```env
XIQ_USERNAME=monitoring@deinefirma.com
XIQ_PASSWORD=SuperSecret123!

# Optional andere Region
# XIQ_BASE_URL=https://api.eu.extremecloudiq.com

# Redis (DB 3 = APs, DB 1 = Locations, etc.)
REDIS_URL=redis://redis.intern:6379/3
```

## Verwendung

```bash
# Einfach starten
eciq_ap_to_redis

# Mit Parametern
eciq_ap_to_redis \
  --server https://api.extremecloudiq.com \
  --token-file /var/lib/xiq/token.txt \
  --redis-url redis://localhost:6379/3 \
  --page-size 100

# Token neu holen (z. B. nach Passwortänderung)
eciq_ap_to_redis --force-login
```

### CLI-Optionen

```text
--server       XIQ API URL (default: https://api.extremecloudiq.com)
--token-file   Speicherort des Tokens (default: xiq_token.txt)
--redis-url    Redis-URL (default: redis://localhost:6379/3)
--page-size    Geräte pro Seite (max 100)
--force-login  Ignoriert alten Token und loggt neu ein
```

## Redis-Struktur nach dem Lauf

```redis
# Alle AP-Daten als JSON im Hash
HGETALL ap:123456789012345

# SSIDs als sortierte Liste (unique)
LRANGE ap:123456789012345:ssids 0 -1
# → ["Corporate", "Guest", "IoT-Network"]
```

TTL: **2 Stunden** → ideal für Checkmk-Caching.

## Cronjob (empfohlen)

```cron
*/30 * * * * /usr/local/bin/eciq_ap_to_redis --redis-url redis://localhost:6379/3 >> /var/log/eciq_sync.log 2>&1
```

## Fehlerbehebung

| Problem                    | Lösung                                  |
|----------------------------|-----------------------------------------|
| `401 Unauthorized`         | `--force-login` oder Passwort prüfen    |
| `429 Too Many Requests`    | Automatisches Retry (log zeigt Wartezeit) |
| Redis-Verbindung fehlt     | `REDIS_URL` prüfen                      |
| Keine APs gefunden         | XIQ-Berechtigungen (Read auf Devices)   |

## Entwicklung

```bash
# Hot-Reload
cargo watch -x run

# Tests & Linting
cargo test
cargo clippy --all-features
cargo fmt --all
```

## Lizenz

MIT – wie der Rest des Repos.

---

**Fertig!** Dein XIQ-Monitoring ist jetzt blitzschnell, stabil und zukunftssicher.

Fragen → Issue aufmachen oder PN!
