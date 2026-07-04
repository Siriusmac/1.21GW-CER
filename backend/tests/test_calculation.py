from datetime import datetime
from zoneinfo import ZoneInfo

from app.schemas.cer import CommunitySchema, MemberSchema, PodSchema
from app.schemas.common import EnergyDirection, EnergyReadingIn
from app.services.calculation import calculate_summary


def test_shared_energy_is_minimum_between_production_and_consumption() -> None:
    zone = ZoneInfo("Europe/Rome")
    community = CommunitySchema(
        id="cer-test",
        name="CER Test",
        primary_substation="CP-TEST",
        benefit_rule="proportional_consumption",
        members=[
            MemberSchema(id="m1", name="Consumer", role="consumer", pods=[PodSchema(id="pod-c", code="C", direction_type="consumption")], plants=[]),
            MemberSchema(id="m2", name="Producer", role="producer", pods=[PodSchema(id="pod-p", code="P", direction_type="production")], plants=[]),
        ],
    )
    readings = [
        EnergyReadingIn(timestamp=datetime(2026, 1, 1, 10, tzinfo=zone), pod_id="pod-c", energy_kwh=10, direction=EnergyDirection.consumption),
        EnergyReadingIn(timestamp=datetime(2026, 1, 1, 10, tzinfo=zone), pod_id="pod-p", energy_kwh=7, direction=EnergyDirection.production),
    ]

    summary = calculate_summary(community, readings, incentive_eur_kwh=0.1)

    assert summary.label == "stima tecnica non validata"
    assert summary.production_kwh == 7
    assert summary.consumption_kwh == 10
    assert summary.shared_energy_kwh == 7
    assert summary.estimated_value_eur == 0.7
    assert summary.members[0].estimated_benefit_eur == 0.7


def test_fixed_percent_benefit_rule() -> None:
    zone = ZoneInfo("Europe/Rome")
    community = CommunitySchema(
        id="cer-test",
        name="CER Test",
        primary_substation="CP-TEST",
        benefit_rule="fixed_percent",
        members=[
            MemberSchema(id="m1", name="A", role="consumer", benefit_share_percent=60, pods=[PodSchema(id="pod-a", code="A", direction_type="consumption")], plants=[]),
            MemberSchema(id="m2", name="B", role="consumer", benefit_share_percent=40, pods=[PodSchema(id="pod-b", code="B", direction_type="consumption")], plants=[]),
        ],
    )
    readings = [
        EnergyReadingIn(timestamp=datetime(2026, 1, 1, 10, tzinfo=zone), pod_id="pod-a", energy_kwh=10, direction=EnergyDirection.consumption),
        EnergyReadingIn(timestamp=datetime(2026, 1, 1, 10, tzinfo=zone), pod_id="pod-b", energy_kwh=10, direction=EnergyDirection.consumption),
        EnergyReadingIn(timestamp=datetime(2026, 1, 1, 10, tzinfo=zone), pod_id="pod-x", energy_kwh=10, direction=EnergyDirection.production),
    ]

    summary = calculate_summary(community, readings, incentive_eur_kwh=0.2)

    assert summary.estimated_value_eur == 2
    assert summary.members[0].estimated_benefit_eur == 1.2
    assert summary.members[1].estimated_benefit_eur == 0.8


def make_community() -> CommunitySchema:
    return CommunitySchema(
        id="cer-test",
        name="CER Test",
        primary_substation="CP-TEST",
        benefit_rule="proportional_consumption",
        members=[
            MemberSchema(
                id="m1",
                name="Consumer A",
                role="consumer",
                pods=[PodSchema(id="pod-c1", code="C1", direction_type="consumption")],
                plants=[],
            ),
            MemberSchema(
                id="m2",
                name="Consumer B",
                role="consumer",
                pods=[PodSchema(id="pod-c2", code="C2", direction_type="consumption")],
                plants=[],
            ),
            MemberSchema(
                id="m3",
                name="Producer",
                role="producer",
                pods=[PodSchema(id="pod-p1", code="P1", direction_type="production")],
                plants=[],
            ),
        ],
    )


def reading(hour: int, pod_id: str, energy_kwh: float, direction: EnergyDirection) -> EnergyReadingIn:
    return EnergyReadingIn(
        timestamp=datetime(2026, 1, 1, hour, tzinfo=ZoneInfo("Europe/Rome")),
        pod_id=pod_id,
        energy_kwh=energy_kwh,
        direction=direction,
    )


def test_production_greater_than_consumption_caps_shared_energy_to_consumption() -> None:
    summary = calculate_summary(
        make_community(),
        [
            reading(10, "pod-c1", 6, EnergyDirection.consumption),
            reading(10, "pod-p1", 10, EnergyDirection.production),
        ],
        incentive_eur_kwh=0.1,
    )

    assert summary.production_kwh == 10
    assert summary.consumption_kwh == 6
    assert summary.shared_energy_kwh == 6
    assert summary.sharing_percent == 60


def test_consumption_greater_than_production_caps_shared_energy_to_production() -> None:
    summary = calculate_summary(
        make_community(),
        [
            reading(10, "pod-c1", 12, EnergyDirection.consumption),
            reading(10, "pod-p1", 5, EnergyDirection.production),
        ],
        incentive_eur_kwh=0.1,
    )

    assert summary.production_kwh == 5
    assert summary.consumption_kwh == 12
    assert summary.shared_energy_kwh == 5
    assert summary.sharing_percent == 100


def test_missing_interval_is_not_filled_or_carried_forward() -> None:
    summary = calculate_summary(
        make_community(),
        [
            reading(9, "pod-c1", 3, EnergyDirection.consumption),
            reading(9, "pod-p1", 3, EnergyDirection.production),
            reading(11, "pod-c1", 4, EnergyDirection.consumption),
            reading(11, "pod-p1", 2, EnergyDirection.production),
        ],
        incentive_eur_kwh=0.1,
    )

    assert [point.timestamp.hour for point in summary.series] == [9, 11]
    assert summary.shared_energy_kwh == 5


def test_multiple_pods_same_timestamp_are_aggregated_by_interval() -> None:
    summary = calculate_summary(
        make_community(),
        [
            reading(10, "pod-c1", 4, EnergyDirection.consumption),
            reading(10, "pod-c2", 6, EnergyDirection.consumption),
            reading(10, "pod-p1", 8, EnergyDirection.production),
        ],
        incentive_eur_kwh=0.1,
    )

    assert len(summary.series) == 1
    assert summary.consumption_kwh == 10
    assert summary.production_kwh == 8
    assert summary.shared_energy_kwh == 8
    assert summary.members[0].estimated_benefit_eur == 0.32
    assert summary.members[1].estimated_benefit_eur == 0.48


def test_grid_injection_and_withdrawal_do_not_double_count_alternative_measurements() -> None:
    summary = calculate_summary(
        make_community(),
        [
            reading(10, "pod-c1", 10, EnergyDirection.consumption),
            reading(10, "pod-c1", 7, EnergyDirection.grid_withdrawal),
            reading(10, "pod-p1", 12, EnergyDirection.production),
            reading(10, "pod-p1", 5, EnergyDirection.grid_injection),
        ],
        incentive_eur_kwh=0.1,
    )

    assert summary.production_kwh == 5
    assert summary.consumption_kwh == 10
    assert summary.shared_energy_kwh == 5


def test_negative_or_anomalous_values_are_rejected() -> None:
    community = make_community()

    try:
        EnergyReadingIn(
            timestamp=datetime(2026, 1, 1, 10, tzinfo=ZoneInfo("Europe/Rome")),
            pod_id="pod-c1",
            energy_kwh=-1,
            direction=EnergyDirection.consumption,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("negative values must be rejected by schema validation")

    huge = EnergyReadingIn(
        timestamp=datetime(2026, 1, 1, 10, tzinfo=ZoneInfo("Europe/Rome")),
        pod_id="pod-c1",
        energy_kwh=1_000_001,
        direction=EnergyDirection.consumption,
    )

    try:
        calculate_summary(community, [huge], incentive_eur_kwh=0.1)
    except ValueError as exc:
        assert "energy_kwh" in str(exc)
    else:
        raise AssertionError("anomalous values must be rejected by calculation validation")


def test_duplicate_timestamps_same_direction_are_summed_once_per_direction() -> None:
    summary = calculate_summary(
        make_community(),
        [
            reading(10, "pod-c1", 2, EnergyDirection.consumption),
            reading(10, "pod-c1", 3, EnergyDirection.consumption),
            reading(10, "pod-p1", 4, EnergyDirection.production),
            reading(10, "pod-p1", 1, EnergyDirection.production),
        ],
        incentive_eur_kwh=0.1,
    )

    assert len(summary.series) == 1
    assert summary.consumption_kwh == 5
    assert summary.production_kwh == 5
    assert summary.shared_energy_kwh == 5


def test_timestamps_are_normalized_to_europe_rome_before_aggregation() -> None:
    utc = ZoneInfo("UTC")
    rome = ZoneInfo("Europe/Rome")
    summary = calculate_summary(
        make_community(),
        [
            EnergyReadingIn(timestamp=datetime(2026, 1, 1, 9, tzinfo=utc), pod_id="pod-c1", energy_kwh=6, direction=EnergyDirection.consumption),
            EnergyReadingIn(timestamp=datetime(2026, 1, 1, 10, tzinfo=rome), pod_id="pod-p1", energy_kwh=6, direction=EnergyDirection.production),
        ],
        incentive_eur_kwh=0.1,
    )

    assert len(summary.series) == 1
    assert summary.series[0].timestamp.hour == 10
    assert summary.shared_energy_kwh == 6


def test_dst_fall_back_intervals_are_distinct_when_offsets_differ() -> None:
    summary = calculate_summary(
        make_community(),
        [
            EnergyReadingIn(timestamp=datetime.fromisoformat("2026-10-25T02:15:00+02:00"), pod_id="pod-c1", energy_kwh=4, direction=EnergyDirection.consumption),
            EnergyReadingIn(timestamp=datetime.fromisoformat("2026-10-25T02:15:00+02:00"), pod_id="pod-p1", energy_kwh=4, direction=EnergyDirection.production),
            EnergyReadingIn(timestamp=datetime.fromisoformat("2026-10-25T02:15:00+01:00"), pod_id="pod-c1", energy_kwh=6, direction=EnergyDirection.consumption),
            EnergyReadingIn(timestamp=datetime.fromisoformat("2026-10-25T02:15:00+01:00"), pod_id="pod-p1", energy_kwh=6, direction=EnergyDirection.production),
        ],
        incentive_eur_kwh=0.1,
    )

    assert len(summary.series) == 2
    assert [point.timestamp.utcoffset().total_seconds() for point in summary.series] == [7200, 3600]
    assert summary.shared_energy_kwh == 10
