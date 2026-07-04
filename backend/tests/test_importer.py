from app.services.importer import parse_energy_csv


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
