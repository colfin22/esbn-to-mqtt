# esbn-to-mqtt (colfin22 fork)

> Fork of [omgapuppy/esbn-to-mqtt](https://github.com/omgapuppy/esbn-to-mqtt). Adds the `export_hdf_dir` option (default `/share/esbn`), which writes the raw HDF CSV to `<dir>/esbn_hdf_latest.csv` on every poll for external tooling. All other behaviour is unchanged from upstream.

Publish ESB Networks smart meter readings to Home Assistant over MQTT.

This app signs in to ESB Networks, downloads the 30-minute kWh HDF export, keeps a monotonic local accumulator, and publishes retained MQTT discovery sensors for the Home Assistant Energy dashboard.

## What You Get

- `ESBN Import Total` for grid consumption
- `ESBN Export Total` when export data exists
- `ESBN Last Update` as a diagnostic sensor
- Recent interval, daily, monthly, lag, auth, CAPTCHA, and HDF parse diagnostics
- Optional smart-tariff import cost sensors for day, night, and peak pricing
- Configurable polling, defaulting to every 6 hours
- Optional 2Captcha solving when ESBN presents a reCAPTCHA challenge
- Optional raw HDF CSV export to disk via `export_hdf_dir` (fork addition)
- Redacted logs for credentials and MPRNs

## Setup

Open the **Documentation** tab for configuration details, Energy dashboard setup, data freshness notes, and troubleshooting.

The first-pass setup assumes the Home Assistant Mosquitto broker is already installed and available at `core-mosquitto`.

## Status

This is an unofficial app and is not affiliated with ESB Networks. The ESBN portal flow may change, and CAPTCHA or challenge pages can interrupt automated polling.
