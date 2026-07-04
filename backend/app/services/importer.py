import csv
import io
from datetime import datetime
from zoneinfo import ZoneInfo

from app.schemas.common import EnergyDirection, EnergyReadingIn, ImportErrorRow, ImportResult

REQUIRED_COLUMNS = {"timestamp", "pod_id", "energy_kwh", "direction"}


def normalize_timestamp(value: str, timezone_name: str) -> datetime:
    parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    zone = ZoneInfo(timezone_name)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=zone)
    return parsed.astimezone(zone)


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
            if energy_kwh < 0:
                raise ValueError("energy_kwh must be non-negative")
            readings.append(
                EnergyReadingIn(
                    timestamp=timestamp,
                    pod_id=row["pod_id"].strip(),
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
