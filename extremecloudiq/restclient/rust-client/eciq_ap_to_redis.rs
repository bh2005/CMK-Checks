#!/usr/bin/env rustscript
// cargo-deps: reqwest = { version = "0.12", features = ["json", "gzip"] }
// cargo-deps: tokio = { version = "1.40", features = ["full"] }
// cargo-deps: serde = { version = "1.0", features = ["derive"] }
// cargo-deps: serde_json = "1.0"
// cargo-deps: redis = { version = "0.27", features = ["tokio-comp"] }
// cargo-deps: clap = { version = "4.5", features = ["derive"] }
// cargo-deps: dotenvy = "0.15"
// cargo-deps: tracing = "0.1"
// cargo-deps: tracing-subscriber = { version = "0.3", features = ["env-filter"] }
// cargo-deps: thiserror = "1.0"
// cargo-deps: anyhow = "1.0"

use anyhow::{Context, Result};
use clap::Parser;
use dotenvy::dotenv;
use reqwest::{Client, header};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::env;
use std::fs;
use std::time::Duration;
use tokio::time::sleep;
use tracing::{info, warn, error, debug, Level};

/// ExtremeCloudIQ → Redis Sync Tool (Rust Edition)
#[derive(Parser, Debug)]
#[command(author, version, about = "Holt Access Points + SSIDs aus ExtremeCloudIQ und speichert sie in Redis")]
struct Args {
    /// XIQ API Base URL
    #[arg(long, default_value = "https://api.extremecloudiq.com")]
    server: String,

    /// API Token Datei (wird automatisch gespeichert/geladen)
    #[arg(long, default_value = "xiq_token.txt")]
    token_file: String,

    /// Redis URL (z.B. redis://localhost:6379/3)
    #[arg(long, default_value = "redis://localhost:6379/3")]
    redis_url: String,

    /// Page size (max 100 bei XIQ)
    #[arg(long, default_value_t = 100)]
    page_size: u32,

    /// Force Login (ignoriert gespeicherten Token)
    #[arg(long)]
    force_login: bool,
}

#[derive(Debug, Serialize, Deserialize)]
struct LoginResponse {
    access_token: String,
}

#[derive(Debug, Deserialize)]
struct DevicePage {
    data: Vec<Device>,
    total_count: Option<u32>,
    page: u32,
    limit: u32,
}

#[derive(Debug, Deserialize, Clone)]
struct Device {
    id: u64,
    hostname: Option<String>,
    device_function: String,
    serial_number: Option<String>,
    product_type: Option<String>,
    connected: bool,
    location_id: Option<u64>,
    // ... weitere Felder nach Bedarf
}

#[derive(Debug, Deserialize)]
struct RadioInfoResponse {
    data: Vec<RadioDeviceInfo>,
}

#[derive(Debug, Deserialize)]
struct RadioDeviceInfo {
    device_id: u64,
    radios: Vec<Radio>,
}

#[derive(Debug, Deserialize)]
struct Radio {
    wlans: Vec<Wlan>,
}

#[derive(Debug, Deserialize, Clone)]
struct Wlan {
    ssid: String,
    ssid_status: Option<String>,
    ssid_security_type: Option<String>,
    bssid: Option<String>,
    network_policy_name: Option<String>,
}

type SsidsByDevice = HashMap<u64, Vec<Wlan>>;

#[tokio::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_max_level(Level::INFO)
        .with_env_filter("eciq_ap_to_redis=debug")
        .init();

    dotenv().ok();
    let args = Args::parse();

    let client = Client::builder()
        .timeout(Duration::from_secs(30))
        .gzip(true)
        .build()?;

    let token = if args.force_login || !token_exists(&args.token_file) {
        let token = login_and_save(&client, &args.server, &args.token_file).await?;
        info!("Neuer Token erhalten und gespeichert.");
        token
    } else {
        let token = fs::read_to_string(&args.token_file)?.trim().to_string();
        info!("Token aus Datei geladen.");
        token
    };

    let aps = fetch_all_access_points(&client, &args.server, &token, args.page_size).await?;
    info!("{} Access Points gefunden.", aps.len());

    let ssids = fetch_ssids_for_devices(&client, &args.server, &token, &aps).await?;
    info!("SSIDs für {} Geräte geladen.", ssids.len());

    store_in_redis(&args.redis_url, &aps, &ssids).await?;
    info!("Fertig – alle Daten in Redis gespeichert.");

    Ok(())
}

fn token_exists(path: &str) -> bool {
    std::path::Path::new(path).exists()
}

async fn login_and_save(client: &Client, server: &str, token_file: &str) -> Result<String> {
    let username = env::var("XIQ_USERNAME").context("XIQ_USERNAME nicht gesetzt")?;
    let password = env::var("XIQ_PASSWORD").context("XIQ_PASSWORD nicht gesetzt")?;

    let res = client
        .post(format!("{server}/login"))
        .json(&serde_json::json!({ "username": username, "password": password }))
        .send()
        .await?
        .error_for_status()?;

    let login: LoginResponse = res.json().await?;
    fs::write(token_file, &login.access_token)?;
    Ok(login.access_token)
}

async fn request_with_retry(client: &Client, req: reqwest::RequestBuilder) -> Result<reqwest::Response> {
    let mut attempts = 0;
    loop {
        let res = req.try_clone().unwrap().send().await?;

        if res.status() == 429 {
            let retry_after = res.headers()
                .get("Retry-After")
                .and_then(|v| v.to_str().ok())
                .and_then(|s| s.parse::<u64>().ok())
                .unwrap_or(60);

            warn!("Rate Limit! Warte {retry_after} Sekunden...");
            sleep(Duration::from_secs(retry_after)).await;
            attempts += 1;
            if attempts > 5 {
                return Err(anyhow::anyhow!("Rate Limit trotz Retry"));
            }
            continue;
        }

        return Ok(res.error_for_status()?);
    }
}

async fn fetch_all_access_points(
    client: &Client,
    server: &str,
    token: &str,
    page_size: u32,
) -> Result<Vec<Device>> {
    let mut page = 1;
    let mut all_aps = Vec::new();
    let auth_header = format!("Bearer {token}");

    loop {
        info!("Seite {page} wird geladen (limit={page_size})...");

        let req = client
            .get(format!("{server}/devices"))
            .header(header::AUTHORIZATION, &auth_header)
            .query(&[
                ("page", page.to_string()),
                ("limit", page_size.to_string()),
                ("views", "FULL".to_string()),
            ]);

        let res = request_with_retry(client, req).await?;
        let page_data: DevicePage = res.json().await?;

        let aps: Vec<Device> = page_data
            .data
            .into_iter()
            .filter(|d| d.device_function == "AP")
            .collect();

        all_aps.extend(aps);

        if page_data.data.len() < page_size as usize {
            break;
        }
        page += 1;
        sleep(Duration::from_millis(800)).await; // Höfliches Pacing
    }

    Ok(all_aps)
}

async fn fetch_ssids_for_devices(
    client: &Client,
    server: &str,
    token: &str,
    devices: &[Device],
) -> Result<SsidsByDevice> {
    let mut ssids_map = HashMap::new();
    let auth_header = format!("Bearer {token}");
    let ids: Vec<u64> = devices.iter().map(|d| d.id).collect();

    for chunk in ids.chunks(10) {  // XIQ erlaubt max 10 IDs pro Request
        let ids_str = chunk.iter()
            .map(|id| id.to_string())
            .collect::<Vec<_>>()
            .join(",");

        let req = client
            .get(format!("{server}/devices/radio-information"))
            .header(header::AUTHORIZATION, &auth_header)
            .header(header::ACCEPT, "application/json")
            .query(&[
                ("deviceIds", ids_str),
                ("includeDisabledRadio", "false"),
                ("limit", "100"),
            ]);

        let res = request_with_retry(client, req).await?;
        let info: RadioInfoResponse = res.json().await?;

        for device_info in info.data {
            let unique_ssids = device_info.radios
                .into_iter()
                .flat_map(|r| r.wlans)
                .fold(HashMap::new(), |mut acc, wlan| {
                    acc.entry(wlan.ssid.clone()).or_insert(wlan.clone());
                    acc
                })
                .into_values()
                .collect();

            ssids_map.insert(device_info.device_id, unique_ssids);
        }

        sleep(Duration::from_millis(500)).await;
    }

    Ok(ssids_map)
}

async fn store_in_redis(
    redis_url: &str,
    aps: &[Device],
    ssids_map: &SsidsByDevice,
) -> Result<()> {
    let client = redis::Client::open(redis_url)?;
    let mut con = client.get_async_connection().await?;

    for ap in aps {
        let key = format!("ap:{}", ap.id);

        // Basisdaten als JSON
        let ap_json = serde_json::to_string(ap)?;
        redis::cmd("SET").arg(&key).arg(&ap_json).query_async(&mut con).await?;

        // SSIDs als separate Liste
        if let Some(ssids) = ssids_map.get(&ap.id) {
            let ssid_strings: Vec<String> = ssids.iter()
                .map(|w| w.ssid.clone())
                .collect();
            redis::cmd("DEL").arg(format!("{key}:ssids")).query_async(&mut con).await?;
            if !ssid_strings.is_empty() {
                redis::cmd("RPUSH")
                    .arg(format!("{key}:ssids"))
                    .arg(&ssid_strings)
                    .query_async(&mut con).await?;
            }
        }

        // TTL: 2 Stunden
        redis::cmd("EXPIRE").arg(&key).arg(7200).query_async(&mut con).await?;
        debug!("Gespeichert: {key}");
    }

    info!("{} Access Points in Redis gespeichert.", aps.len());
    Ok(())
}