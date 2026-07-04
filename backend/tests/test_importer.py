from app.services.importer import parse_energy_csv
from app.services.importer import normalize_timestamp


def test_parse_energy_csv_reports_invalid_rows() -> None:
    content = b"""timestamp,pod_id,energy_kwh,direction
2026-01-01T10:00:00+01:00,POD-1,1.5,consumption
2026-01-01T10:10:00+01:00,POD-1,2.0,consumption
bad-date,POD-2,1.0,production
"""

    result = parse_energy_csv(content, "Europe/Rome")

    assert result.imported_count == 1
    assert result.invalid_count == 2
    assert result.readings[0].timestamp.tzinfo is not None


def test_parse_energy_csv_accepts_quarter_hour_and_hourly_rows() -> None:
    content = b"""timestamp,pod_id,energy_kwh,direction
2026-01-01T10:00:00+01:00,POD-1,1.5,consumption
2026-01-01T10:15:00+01:00,POD-1,2.0,production
"""

    result = parse_energy_csv(content, "Europe/Rome")

    assert result.imported_count == 2
    assert result.invalid_count == 0


def test_dst_spring_forward_non_existent_local_time_is_rejected() -> None:
    content = b"""timestamp,pod_id,energy_kwh,direction
2026-03-29T02:15:00,POD-1,1.5,consumption
"""

    result = parse_energy_csv(content, "Europe/Rome")

    assert result.imported_count == 0
    assert result.invalid_count == 1
    assert "non-existent" in result.errors[0].message


def test_dst_fall_back_ambiguous_local_time_requires_explicit_offset() -> None:
    content = b"""timestamp,pod_id,energy_kwh,direction
2026-10-25T02:15:00,POD-1,1.5,consumption
"""

    result = parse_energy_csv(content, "Europe/Rome")

    assert result.imported_count == 0
    assert result.invalid_count == 1
    assert "ambiguous" in result.errors[0].message


def test_dst_fall_back_with_explicit_offsets_keeps_distinct_instants() -> None:
    summer = normalize_timestamp("2026-10-25T02:15:00+02:00", "Europe/Rome")
    winter = normalize_timestamp("2026-10-25T02:15:00+01:00", "Europe/Rome")

    assert summer.timestamp() != winter.timestamp()
    assert summer.utcoffset() != winter.utcoffset()


def test_csv_rejects_anomalous_and_negative_values() -> None:
    content = b"""timestamp,pod_id,energy_kwh,direction
2026-01-01T10:00:00+01:00,POD-1,-1,consumption
2026-01-01T10:15:00+01:00,POD-1,1000001,production
"""

    result = parse_energy_csv(content, "Europe/Rome")

    assert result.imported_count == 0
    assert result.invalid_count == 2
