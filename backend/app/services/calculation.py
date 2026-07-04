from collections import defaultdict
from datetime import datetime

from app.schemas.common import CalculationSummary, EnergyDirection, EnergyReadingIn, MemberBenefit, TimeSeriesPoint
from app.schemas.cer import CommunitySchema


def _round(value: float) -> float:
    return round(value, 4)


def calculate_summary(
    community: CommunitySchema,
    readings: list[EnergyReadingIn],
    incentive_eur_kwh: float,
    start: datetime | None = None,
    end: datetime | None = None,
) -> CalculationSummary:
    filtered = [
        reading
        for reading in readings
        if (start is None or reading.timestamp >= start) and (end is None or reading.timestamp <= end)
    ]

    pod_to_member = {pod.id: member for member in community.members for pod in member.pods}
    by_timestamp: dict[datetime, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    consumption_by_member: dict[str, float] = defaultdict(float)

    for reading in filtered:
        direction = reading.direction
        if direction in (EnergyDirection.production, EnergyDirection.grid_injection):
            by_timestamp[reading.timestamp]["production"] += reading.energy_kwh
        if direction in (EnergyDirection.consumption, EnergyDirection.grid_withdrawal):
            by_timestamp[reading.timestamp]["consumption"] += reading.energy_kwh
            member = pod_to_member.get(reading.pod_id)
            if member:
                consumption_by_member[member.id] += reading.energy_kwh

    series: list[TimeSeriesPoint] = []
    total_production = 0.0
    total_consumption = 0.0
    total_shared = 0.0

    for timestamp in sorted(by_timestamp):
        production = by_timestamp[timestamp]["production"]
        consumption = by_timestamp[timestamp]["consumption"]
        shared = min(production, consumption)
        total_production += production
        total_consumption += consumption
        total_shared += shared
        series.append(
            TimeSeriesPoint(
                timestamp=timestamp,
                production_kwh=_round(production),
                consumption_kwh=_round(consumption),
                shared_energy_kwh=_round(shared),
                sharing_percent=_round((shared / production * 100) if production else 0),
                estimated_value_eur=_round(shared * incentive_eur_kwh),
            )
        )

    total_value = total_shared * incentive_eur_kwh
    total_member_consumption = sum(consumption_by_member.values())
    member_benefits: list[MemberBenefit] = []

    for member in community.members:
        consumption = consumption_by_member.get(member.id, 0.0)
        if community.benefit_rule == "fixed_percent" and member.benefit_share_percent is not None:
            share_ratio = member.benefit_share_percent / 100
        else:
            share_ratio = consumption / total_member_consumption if total_member_consumption else 0
        member_benefits.append(
            MemberBenefit(
                member_id=member.id,
                member_name=member.name,
                consumption_kwh=_round(consumption),
                shared_energy_kwh=_round(total_shared * share_ratio),
                estimated_benefit_eur=_round(total_value * share_ratio),
            )
        )

    return CalculationSummary(
        production_kwh=_round(total_production),
        consumption_kwh=_round(total_consumption),
        shared_energy_kwh=_round(total_shared),
        virtual_self_consumption_kwh=_round(total_shared),
        sharing_percent=_round((total_shared / total_production * 100) if total_production else 0),
        incentive_eur_kwh=incentive_eur_kwh,
        estimated_value_eur=_round(total_value),
        series=series,
        members=member_benefits,
    )
