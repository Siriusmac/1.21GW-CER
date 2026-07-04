import csv
import io
import math
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from app.schemas.common import EnergyDirection, EnergyReadingIn, ImportErrorRow, ImportResult

REQUIRED_COLUMNS = {"timestamp", "pod_id", "energy_kwh", "direction"}
MAX_ENERGY_KWH = 1_000_000


def normalize_timestamp(value: str, timezone_name: str) -> datetime:
    parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    zone = ZoneInfo(timezone_name)
    if parsed.tzinfo is not None:
        return parsed.astimezone(zone)

    fold_0 = parsed.replace(tzinfo=zone, fold=0)
    fold_1 = parsed.replace(tzinfo=zone, fold=1)
    roundtrip_0 = fold_0.astimezone(UTC).astimezone(zone).replace(tzinfo=None)
    roundtrip_1 = fold_1.astimezone(UTC).astimezone(zone).replace(tzinfo=None)
    matches_0 = roundtrip_0 == parsed
    matches_1 = roundtrip_1 == parsed

    if not matches_0 and not matches_1:
        raise ValueError("timestamp is in a non-existent local time during DST transition")
    if matches_0 and matches_1 and fold_0.utcoffset() != fold_1.utcoffset():
        raise ValueError("timestamp is ambiguous during DST transition; include an explicit UTC offset")
    return fold_0 if matches_0 else fold_1


def _validate_granularity(timestamp: datetime, allowed_minutes: tuple[int, ...] = (0, 15, 30, 45)) -> None:
    if timestamp.minute not in allowed_minutes or timestamp.second != 0 or timestamp.microsecond != 0:
        raise ValueError("timestamp must be hourly or quarter-hourly")


def parse_energy_csv(content: bytes, timezone_name: str) -> ImportResult:
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    errors: list[ImportErrorRow] = []
    readings: list[EnergyReadingIn] = []

    if not reader.fieldnames or not REQUIRED_COLUMNS.issubset(set(reader.fieldnames)):
        missing = ", ".join(sorted(REQUIRED_COLUMNS - set(reader.fieldnames or [])))
        return ImportResult(imported_count=0, invalid_count=1, errors=[ImportErrorRow(row_number=1, message=f"missing columns: {missing}")], readings=[])

    for index, row in enumerate(reader, start=2):
        try:
            timestamp = normalize_timestamp(row["timestamp"], timezone_name)
            _validate_granularity(timestamp)
            energy_kwh = float(row["energy_kwh"])
            if not math.isfinite(energy_kwh) or energy_kwh < 0 or energy_kwh > MAX_ENERGY_KWH:
                raise ValueError(f"energy_kwh must be finite, non-negative and <= {MAX_ENERGY_KWH}")
            pod_id = row["pod_id"].strip()
            if not pod_id:
                raise ValueError("pod_id is required")
            readings.append(
                EnergyReadingIn(
                    timestamp=timestamp,
                    pod_id=pod_id,
                    energy_kwh=energy_kwh,
                    direction=EnergyDirection(row["direction"].strip()),
                )
            )
        except Exception as exc:
            errors.append(ImportErrorRow(row_number=index, message=str(exc)))

    return ImportResult(
        imported_count=len(readings),
        invalid_count=len(errors),
        errors=errors,
        readings=readings,
    )
