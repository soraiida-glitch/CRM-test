from pydantic import BaseModel


class SlideRequest(BaseModel):
    opportunity_id: str
    name: str
    issues: str
    strategy: str
    description: str
    close_date: str
    amount: float


class SlideMeta(BaseModel):
    company_name: str
    run_month: str


class SlideIssues(BaseModel):
    issue_1: str
    issue_2: str


class SlideUseCases(BaseModel):
    use_case_1: str
    use_case_2: str


class SlideQuestions(BaseModel):
    needs_and_issues: list[str]
    data_details: list[str]
    system_infrastructure: list[str]
    organization_structure: list[str]
    budget_and_timeline: list[str]


class SlideInsight(BaseModel):
    target_process: str
    point_1: str
    point_2: str
    full_sentence: str


class SlideResponse(BaseModel):
    meta: SlideMeta
    issues: SlideIssues
    use_cases: SlideUseCases
    questions: SlideQuestions
    insight: SlideInsight
    case_type: int
