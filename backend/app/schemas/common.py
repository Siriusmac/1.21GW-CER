from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class EnergyDirection(StrEnum):
    consumption = "consumption"
    production = "production"
    grid_withdrawal = "grid_withdrawal"
    grid_injection = "grid_injection"


class MemberRole(StrEnum):
    consumer = "consumer"
    producer = "producer"
    prosumer = "prosumer"


class EnergyReadingIn(BaseModel):
    timestamp: datetime
    pod_id: str
    energy_kwh: float = Field(ge=0)
    direction: EnergyDirection


class ImportErrorRow(BaseModel):
    row_number: int
    message: str


class ImportResult(BaseModel):
    imported_count: int
    invalid_count: int
    errors: list[ImportErrorRow]
    readings: list[EnergyReadingIn]


class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    production_kwh: float
    consumption_kwh: float
    shared_energy_kwh: float
    sharing_percent: float
    estimated_value_eur: float


class MemberBenefit(BaseModel):
    member_id: str
    member_name: str
    consumption_kwh: float
    shared_energy_kwh: float
    estimated_benefit_eur: float


class CalculationSummary(BaseModel):
    label: str = "stima tecnica non validata"
    production_kwh: float
    consumption_kwh: float
    shared_energy_kwh: float
    virtual_self_consumption_kwh: float
    sharing_percent: float
    incentive_eur_kwh: float
    estimated_value_eur: float
    series: list[TimeSeriesPoint]
    members: list[MemberBenefit]
