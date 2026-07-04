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
