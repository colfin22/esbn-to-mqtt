# Changelog

## 0.4.3-colfin1 (colfin22 fork)

- Add `export_hdf_dir` option: when set, the raw downloaded HDF CSV is written to `<dir>/esbn_hdf_latest.csv` on every successful poll. Lets external tooling (e.g. an InfluxDB importer) consume the full half-hourly series, which is not published over MQTT.
- Add `share:rw` to the add-on filesystem map so the default `/share/esbn` export path is writable.
- Build locally from the Dockerfile (removed upstream prebuilt `image:` reference).

## 0.4.3

- Fix Home Assistant discovery metadata for monetary cost totals and latest interval kWh sensors.
- Add CODEOWNERS so protected branches can require owner review.

## 0.4.2

- Add HDF export stuck diagnostics when ESBN row counts fall while the latest interval does not advance.
- Log a warning after repeated stuck HDF export observations.

## 0.4.1

- Adjust accumulated import, export, and tariff cost totals when ESBN revises already-seen interval values.
- Log successful poll diagnostics including parsed rows, latest interval, data lag, and new values processed.

## 0.1.0

- Initial experimental Home Assistant app release.
