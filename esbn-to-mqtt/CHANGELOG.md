# Changelog

## 0.4.9-colfin1 (colfin22 fork)

- Fix the timezone migration crashing on legacy state: my own state file had
  interval keys with unicode superscript digits from a past encoding glitch
  (e.g. `18:3¹` instead of `18:31`), which broke `datetime.fromisoformat`
  and made every poll fail after the 0.4.7 upgrade. The migration now
  normalizes those digits before parsing instead of aborting.

## 0.4.7-colfin1 (colfin22 fork)

- Fix HDF download 404: ESB Networks now requires an `x-ReturnUrl` header on
  the `DownloadHdfPeriodic` request; without it every poll failed even with
  a valid authenticated session.
- Merge in upstream 0.4.4: HDF timestamps are read as Irish local time
  instead of being misread as UTC (the meter's 30-minute intervals were off
  by up to an hour depending on the time of year), with a one-time state
  migration and backup on first run. Also fixes autumn-DST duplicate-hour
  handling in the HDF parser.

## 0.4.4-colfin1 (colfin22 fork)

- Survive ESBN portal timeouts instead of crashing: five raw `httpx` calls
  (session check, landing page, credential submit, CAPTCHA template/scripts)
  now route through the wrapping `_get`/`_post` helpers, and the main poll
  loop catches `httpx.HTTPError` as a safety net. A portal `ReadTimeout` on
  04-07-2026 previously killed the add-on and froze the sensors for 2 days;
  it now logs the failure and retries on the normal backoff.

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
