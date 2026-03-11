from typing import Optional

from pydantic import BaseModel, Field


class Opportunity(BaseModel):
    opportunity_id: str
    owner_id: str
    owner_name: str
    name: str
    stage: str
    amount: float
    probability: float
    close_date: Optional[str] = None
    last_activity_date: Optional[str] = None
    next_step: Optional[str] = None
    decision_maker_contacted: bool = False
    description: str = ""


class PrioritizeRequest(BaseModel):
    opportunities: list[Opportunity]


class PrioritizedOpportunity(BaseModel):
    owner_id: str
    owner_name: str
    rank: int
    opportunity_id: str
    opportunity_name: str
    priority_score: int
    action: str
    action_reason: str


class PrioritizeResponse(BaseModel):
    results: list[PrioritizedOpportunity]


class RecommendedAction(BaseModel):
    row_number: int
    opportunity_name: str
    action: str
    reason: str


class ActualTask(BaseModel):
    task_subject: str
    opportunity_name: str
    priority_score: int = 0
    task_description: str = ""
    task_status: str = ""


class PendingTask(BaseModel):
    row_number: int
    task_date: str
    mark: str = ""


class ScoreRequest(BaseModel):
    user_name: str
    recommended_actions: list[RecommendedAction] = Field(default_factory=list)
    actual_tasks: list[ActualTask] = Field(default_factory=list)
    pending_tasks: list[PendingTask] = Field(default_factory=list)


class CompletedRow(BaseModel):
    row_number: int
    mark: str = ""


class PenaltySummary(BaseModel):
    pending_count: int
    penalty_total: int
    final_score: int


class ScoreResponse(BaseModel):
    user_name: str
    total_score: int
    summary: str
    good_points: list[str]
    improvement_points: list[str]
    action_alignment_status: str
    completed_rows: list[CompletedRow]
    penalty: PenaltySummary
