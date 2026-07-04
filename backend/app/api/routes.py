from datetime import datetime

from fastapi import APIRouter, File, Query, UploadFile

from app.core.config import settings
from app.schemas.common import CalculationSummary, ImportResult
from app.schemas.cer import CommunitySchema
from app.services.calculation import calculate_summary
from app.services.demo_data import DEMO_COMMUNITY, DEMO_READINGS
from app.services.importer import parse_energy_csv

router = APIRouter(prefix="/api/v1")


@router.get("/config/economics")
def economics_config() -> dict[str, float | int | str]:
    return {
        "label": "stima tecnica non validata",
        "timezone": settings.timezone,
        "granularity_minutes": settings.default_granularity_minutes,
        "incentive_eur_kwh": settings.incentive_eur_kwh,
    }


@router.get("/cer", response_model=CommunitySchema)
def get_community() -> CommunitySchema:
    return DEMO_COMMUNITY


@router.post("/import/csv", response_model=ImportResult)
async def import_csv(file: UploadFile = File(...)) -> ImportResult:
    content = await file.read()
    return parse_energy_csv(content, settings.timezone)


@router.get("/dashboard/admin", response_model=CalculationSummary)
def admin_dashboard(
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
) -> CalculationSummary:
    return calculate_summary(DEMO_COMMUNITY, DEMO_READINGS, settings.incentive_eur_kwh, start=start, end=end)


@router.get("/dashboard/member/{member_id}", response_model=CalculationSummary)
def member_dashboard(member_id: str) -> CalculationSummary:
    summary = calculate_summary(DEMO_COMMUNITY, DEMO_READINGS, settings.incentive_eur_kwh)
    summary.members = [member for member in summary.members if member.member_id == member_id]
    return summary


@router.get("/reports/monthly", response_model=CalculationSummary)
def monthly_report(
    year: int = Query(default=2026, ge=2000, le=2100),
    month: int = Query(default=1, ge=1, le=12),
) -> CalculationSummary:
    start = datetime.fromisoformat(f"{year:04d}-{month:02d}-01T00:00:00+01:00")
    end_month = month + 1
    end_year = year
    if end_month == 13:
        end_month = 1
        end_year += 1
    end = datetime.fromisoformat(f"{end_year:04d}-{end_month:02d}-01T00:00:00+01:00")
    return calculate_summary(DEMO_COMMUNITY, DEMO_READINGS, settings.incentive_eur_kwh, start=start, end=end)
