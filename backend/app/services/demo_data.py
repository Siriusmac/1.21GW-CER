from datetime import datetime
from zoneinfo import ZoneInfo

from app.schemas.cer import CommunitySchema, MemberSchema, PlantSchema, PodSchema
from app.schemas.common import EnergyDirection, EnergyReadingIn

ROME = ZoneInfo("Europe/Rome")


DEMO_COMMUNITY = CommunitySchema(
    id="cer-demo",
    name="CER Demo Cabina Primaria Roma Nord",
    primary_substation="CP-ROMA-NORD-01",
    benefit_rule="proportional_consumption",
    members=[
        MemberSchema(
            id="m-001",
            name="Condominio Via Solare",
            role="consumer",
            pods=[PodSchema(id="POD-CONS-001", code="IT001E00000001", direction_type="consumption")],
            plants=[],
        ),
        MemberSchema(
            id="m-002",
            name="Azienda Agricola Luce",
            role="prosumer",
            pods=[
                PodSchema(id="POD-CONS-002", code="IT001E00000002", direction_type="consumption"),
                PodSchema(id="POD-PROD-001", code="IT001E00000003", direction_type="production"),
            ],
            plants=[PlantSchema(id="plant-001", name="FV Tetto Magazzino", capacity_kw=85.0, pod_id="POD-PROD-001")],
        ),
        MemberSchema(
            id="m-003",
            name="Scuola Primaria Energia",
            role="producer",
            pods=[PodSchema(id="POD-PROD-002", code="IT001E00000004", direction_type="production")],
            plants=[PlantSchema(id="plant-002", name="FV Scuola", capacity_kw=45.0, pod_id="POD-PROD-002")],
        ),
    ],
)


DEMO_READINGS = [
    EnergyReadingIn(timestamp=datetime(2026, 1, 1, 9, 0, tzinfo=ROME), pod_id="POD-CONS-001", energy_kwh=18.2, direction=EnergyDirection.consumption),
    EnergyReadingIn(timestamp=datetime(2026, 1, 1, 9, 0, tzinfo=ROME), pod_id="POD-CONS-002", energy_kwh=9.1, direction=EnergyDirection.consumption),
    EnergyReadingIn(timestamp=datetime(2026, 1, 1, 9, 0, tzinfo=ROME), pod_id="POD-PROD-001", energy_kwh=21.4, direction=EnergyDirection.production),
    EnergyReadingIn(timestamp=datetime(2026, 1, 1, 9, 0, tzinfo=ROME), pod_id="POD-PROD-002", energy_kwh=7.5, direction=EnergyDirection.production),
    EnergyReadingIn(timestamp=datetime(2026, 1, 1, 10, 0, tzinfo=ROME), pod_id="POD-CONS-001", energy_kwh=16.8, direction=EnergyDirection.consumption),
    EnergyReadingIn(timestamp=datetime(2026, 1, 1, 10, 0, tzinfo=ROME), pod_id="POD-CONS-002", energy_kwh=11.2, direction=EnergyDirection.consumption),
    EnergyReadingIn(timestamp=datetime(2026, 1, 1, 10, 0, tzinfo=ROME), pod_id="POD-PROD-001", energy_kwh=25.6, direction=EnergyDirection.production),
    EnergyReadingIn(timestamp=datetime(2026, 1, 1, 10, 0, tzinfo=ROME), pod_id="POD-PROD-002", energy_kwh=8.0, direction=EnergyDirection.production),
    EnergyReadingIn(timestamp=datetime(2026, 1, 1, 11, 0, tzinfo=ROME), pod_id="POD-CONS-001", energy_kwh=14.1, direction=EnergyDirection.consumption),
    EnergyReadingIn(timestamp=datetime(2026, 1, 1, 11, 0, tzinfo=ROME), pod_id="POD-CONS-002", energy_kwh=12.6, direction=EnergyDirection.consumption),
    EnergyReadingIn(timestamp=datetime(2026, 1, 1, 11, 0, tzinfo=ROME), pod_id="POD-PROD-001", energy_kwh=28.3, direction=EnergyDirection.production),
    EnergyReadingIn(timestamp=datetime(2026, 1, 1, 11, 0, tzinfo=ROME), pod_id="POD-PROD-002", energy_kwh=9.4, direction=EnergyDirection.production),
]
