from typing import Optional

from pydantic import BaseModel, Field


class SuggestionCase(BaseModel):
    opportunity_id: str
    amount: float
    income: float
    family: str
    log: str


class EmbedRequest(BaseModel):
    cases: list[SuggestionCase] = Field(default_factory=list)


class EmbedResponse(BaseModel):
    stored_count: int


class AdviceOpportunity(BaseModel):
    name: str
    stage: str
    amount: float
    probability: float
    close_date: Optional[str] = None
    family: Optional[str] = None
    income: Optional[float] = None
    age: Optional[int] = None
    cause: Optional[str] = None
    rival: bool = False
    description: str = ""


class AdviceRequest(BaseModel):
    opportunity: AdviceOpportunity


class AdviceResponse(BaseModel):
    advice: str
    similar_cases_count: int
