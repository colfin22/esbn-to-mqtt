from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from .models import MeterMetrics, MeterReading, TariffConfig
from .tariff import calculate_import_cost, current_tariff_snapshot

LOCAL_TZ = ZoneInfo("Europe/Dublin")


def _round_kwh(value: float) -> float:
    return round(value, 6)


def _latest_value(readings: list[MeterReading], field: str) -> float | None:
    for reading in sorted(readings, key=lambda item: item.timestamp, reverse=True):
        value = getattr(reading, field)
        if isinstance(value, float):
            return value
    return None


def _sum_for_local_day(readings: list[MeterReading], field: str, now: datetime) -> float | None:
    local_date = now.astimezone(LOCAL_TZ).date()
    values = [
        getattr(reading, field)
        for reading in readings
        if reading.timestamp.astimezone(LOCAL_TZ).date() == local_date
    ]
    numeric_values = [value for value in values if isinstance(value, float)]
    if not numeric_values:
        return None
    return _round_kwh(sum(numeric_values))


def _sum_for_local_month(readings: list[MeterReading], field: str, now: datetime) -> float | None:
    local_now = now.astimezone(LOCAL_TZ)
    values = [
        getattr(reading, field)
        for reading in readings
        if (
            reading.timestamp.astimezone(LOCAL_TZ).year == local_now.year
            and reading.timestamp.astimezone(LOCAL_TZ).month == local_now.month
        )
    ]
    numeric_values = [value for value in values if isinstance(value, float)]
    if not numeric_values:
        return None
    return _round_kwh(sum(numeric_values))


def build_meter_metrics(
    readings: list[MeterReading],
    *,
    processed_before: frozenset[str],
    processed_after: frozenset[str],
    auth_path: str,
    captcha_used: bool,
    tariff: TariffConfig | None = None,
    now: datetime | None = None,
) -> MeterMetrics:
    timestamp = now or datetime.now(UTC)
    latest_interval = max((reading.timestamp for reading in readings), default=None)
    data_lag_hours = None
    if latest_interval is not None:
        data_lag_hours = round(
            (timestamp.astimezone(UTC) - latest_interval.astimezone(UTC)).total_seconds() / 3600,
            3,
        )

    today_import = _sum_for_local_day(readings, "import_kwh", timestamp) or 0.0
    month_import = _sum_for_local_month(readings, "import_kwh", timestamp) or 0.0

    # A meter that exports (solar) but has no readings for TODAY yet has exported zero so
    # far — it is not "no data". The distinction matters: left as None the key is dropped
    # from the state payload (build_state_message skips None) while the discovery config
    # still advertises the sensor, so Home Assistant renders {{ value_json.today_export_kwh }}
    # against a payload with no such key — the sensor sticks at "unknown" and HA logs a
    # template warning on every publish. And it always happens, because the ESBN HDF lags
    # ~24h, so "today" never has readings.
    # An import-only meter still reports None (and gets no export sensors at all).
    exports_energy = any(reading.export_kwh is not None for reading in readings)
    today_export = _sum_for_local_day(readings, "export_kwh", timestamp)
    month_export = _sum_for_local_month(readings, "export_kwh", timestamp)
    if exports_energy:
        today_export = today_export if today_export is not None else 0.0
        month_export = month_export if month_export is not None else 0.0
    today_import_cost = None
    month_import_cost = None
    current_tariff = None
    current_tariff_rate = None
    tariff_currency = None
    if tariff is not None and tariff.enabled:
        today_readings = [
            reading
            for reading in readings
            if reading.timestamp.astimezone(LOCAL_TZ).date()
            == timestamp.astimezone(LOCAL_TZ).date()
        ]
        local_now = timestamp.astimezone(LOCAL_TZ)
        month_readings = [
            reading
            for reading in readings
            if (
                reading.timestamp.astimezone(LOCAL_TZ).year == local_now.year
                and reading.timestamp.astimezone(LOCAL_TZ).month == local_now.month
            )
        ]
        today_import_cost = calculate_import_cost(today_readings, tariff)
        month_import_cost = calculate_import_cost(month_readings, tariff)
        snapshot = current_tariff_snapshot(tariff, now=timestamp)
        current_tariff = snapshot.name
        current_tariff_rate = snapshot.rate
        tariff_currency = snapshot.currency

    return MeterMetrics(
        latest_import_interval_kwh=_latest_value(readings, "import_kwh"),
        latest_export_interval_kwh=_latest_value(readings, "export_kwh"),
        today_import_kwh=today_import,
        today_export_kwh=today_export,
        current_month_import_kwh=month_import,
        current_month_export_kwh=month_export,
        latest_esbn_interval_start=latest_interval,
        data_lag_hours=data_lag_hours,
        hdf_rows_parsed=len(readings),
        new_interval_values_processed=len(processed_after - processed_before),
        captcha_used=captcha_used,
        auth_path=auth_path,
        today_import_cost=today_import_cost,
        current_month_import_cost=month_import_cost,
        current_tariff=current_tariff,
        current_tariff_rate=current_tariff_rate,
        tariff_currency=tariff_currency,
    )
