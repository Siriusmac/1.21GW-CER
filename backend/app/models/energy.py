from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EnergyReading(Base):
    __tablename__ = "energy_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    pod_id: Mapped[str] = mapped_column(ForeignKey("pods.id"), index=True)
    energy_kwh: Mapped[float] = mapped_column(Float)
    direction: Mapped[str] = mapped_column(String(30), index=True)
    source: Mapped[str] = mapped_column(String(80), default="csv")
    validated: Mapped[bool] = mapped_column(Boolean, default=False)
