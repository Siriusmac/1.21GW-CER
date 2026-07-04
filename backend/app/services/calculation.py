from collections import defaultdict
from datetime import UTC, datetime
import math
from zoneinfo import ZoneInfo

from app.schemas.common import CalculationSummary, EnergyDirection, EnergyReadingIn, MemberBenefit, TimeSeriesPoint
from app.schemas.cer import CommunitySchema

ROME = ZoneInfo("Europe/Rome")
MAX_ENERGY_KWH = 1_000_000


def _round(value: float) -> float:
    return round(value, 4)


def _normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=ROME)
    return value.astimezone(ROME)


def _validate_reading(reading: EnergyReadingIn) -> None:
    if reading.timestamp.tzinfo is None:
        raise ValueError("reading timestamp must include timezone information")
    if not math.isfinite(reading.energy_kwh) or reading.energy_kwh < 0 or reading.energy_kwh > MAX_ENERGY_KWH:
        raise ValueError(f"energy_kwh must be finite, non-negative and <= {MAX_ENERGY_KWH}")


def calculate_summary(
    community: CommunitySchema,
    readings: list[EnergyReadingIn],
    incentive_eur_kwh: float,
    start: datetime | None = None,
    end: datetime | None = None,
) -> CalculationSummary:
    start_rome = _normalize_datetime(start) if start else None
    end_rome = _normalize_datetime(end) if end else None

    pod_to_member = {pod.id: member for member in community.members for pod in member.pods}
    by_timestamp_pod: dict[datetime, dict[str, dict[EnergyDirection, float]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(float))
    )
    consumption_by_member: dict[str, float] = defaultdict(float)

    for reading in readings:
        _validate_reading(reading)
        timestamp = _normalize_datetime(reading.timestamp)
        if (start_rome is not None and timestamp < start_rome) or (end_rome is not None and timestamp > end_rome):
            continue
        interval_key = timestamp.astimezone(UTC)
        by_timestamp_pod[interval_key][reading.pod_id][reading.direction] += reading.energy_kwh

    by_timestamp: dict[datetime, dict[str, float]] = defaultdict(lambda: defaultdict(float))

    for timestamp_utc, pods in by_timestamp_pod.items():
        for pod_id, directions in pods.items():
            production = directions.get(EnergyDirection.production, 0.0)
            grid_injection = directions.get(EnergyDirection.grid_injection, 0.0)
            consumption = directions.get(EnergyDirection.consumption, 0.0)
            grid_withdrawal = directions.get(EnergyDirection.grid_withdrawal, 0.0)

            supply = grid_injection if grid_injection > 0 else production
            demand = consumption if consumption > 0 else grid_withdrawal

            by_timestamp[timestamp_utc]["production"] += supply
            by_timestamp[timestamp_utc]["consumption"] += demand
            member = pod_to_member.get(pod_id)
            if member and demand:
                consumption_by_member[member.id] += demand

    series: list[TimeSeriesPoint] = []
    total_production = 0.0
    total_consumption = 0.0
    total_shared = 0.0

    for timestamp_utc in sorted(by_timestamp):
        production = by_timestamp[timestamp_utc]["production"]
        consumption = by_timestamp[timestamp_utc]["consumption"]
        shared = min(production, consumption)
        total_production += production
        total_consumption += consumption
        total_shared += shared
        series.append(
            TimeSeriesPoint(
                timestamp=timestamp_utc.astimezone(ROME),
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
