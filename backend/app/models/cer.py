from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Community(Base):
    __tablename__ = "communities"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    primary_substation: Mapped[str] = mapped_column(String(120))
    benefit_rule: Mapped[str] = mapped_column(String(80), default="proportional_consumption")

    members: Mapped[list["Member"]] = relationship(back_populates="community")


class Member(Base):
    __tablename__ = "members"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    community_id: Mapped[str] = mapped_column(ForeignKey("communities.id"))
    name: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(20))
    benefit_share_percent: Mapped[float | None] = mapped_column(Float, nullable=True)

    community: Mapped[Community] = relationship(back_populates="members")
    pods: Mapped[list["Pod"]] = relationship(back_populates="member")
    plants: Mapped[list["Plant"]] = relationship(back_populates="member")


class Pod(Base):
    __tablename__ = "pods"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    member_id: Mapped[str] = mapped_column(ForeignKey("members.id"))
    code: Mapped[str] = mapped_column(String(80), unique=True)
    direction_type: Mapped[str] = mapped_column(String(30))

    member: Mapped[Member] = relationship(back_populates="pods")
    plants: Mapped[list["Plant"]] = relationship(back_populates="pod")


class Plant(Base):
    __tablename__ = "plants"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    member_id: Mapped[str] = mapped_column(ForeignKey("members.id"))
    name: Mapped[str] = mapped_column(String(200))
    capacity_kw: Mapped[float] = mapped_column(Float)
    pod_id: Mapped[str | None] = mapped_column(ForeignKey("pods.id"), nullable=True)

    member: Mapped[Member] = relationship(back_populates="plants")
    pod: Mapped[Pod | None] = relationship(back_populates="plants")
