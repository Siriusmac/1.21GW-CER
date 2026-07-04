from pydantic import BaseModel


class PodSchema(BaseModel):
    id: str
    code: str
    direction_type: str


class PlantSchema(BaseModel):
    id: str
    name: str
    capacity_kw: float
    pod_id: str | None = None


class MemberSchema(BaseModel):
    id: str
    name: str
    role: str
    benefit_share_percent: float | None = None
    pods: list[PodSchema]
    plants: list[PlantSchema]


class CommunitySchema(BaseModel):
    id: str
    name: str
    primary_substation: str
    benefit_rule: str
    members: list[MemberSchema]
