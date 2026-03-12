from collections import defaultdict
from datetime import date

from fastapi import APIRouter, Depends

from app.dependencies import verify_token
from app.schemas.sales_eval import (
    CompletedRow,
    PenaltySummary,
    PrioritizedOpportunity,
    PrioritizeRequest,
    PrioritizeResponse,
    ScoreRequest,
    ScoreResponse,
)
from app.services.openai_service import get_openai_service
from app.services.scoring import calc_pending_penalty, calc_priority_score

router = APIRouter(dependencies=[Depends(verify_token)])


@router.post("/prioritize", response_model=PrioritizeResponse)
async def prioritize_sales(payload: PrioritizeRequest) -> PrioritizeResponse:
    grouped = defaultdict(list)
    for item in payload.opportunities:
        grouped[(item.owner_id, item.owner_name)].append(item)

    results: list[PrioritizedOpportunity] = []
    service = get_openai_service()
    for (owner_id, owner_name), opportunities in grouped.items():
        ranked = sorted(
            opportunities,
            key=lambda item: calc_priority_score(
                close_date=item.close_date,
                last_activity_date=item.last_activity_date,
                amount=item.amount,
                probability=item.probability,
                decision_maker_contacted=item.decision_maker_contacted,
                next_step=item.next_step,
            ),
            reverse=True,
        )[:3]

        for index, item in enumerate(ranked, start=1):
            score = calc_priority_score(
                close_date=item.close_date,
                last_activity_date=item.last_activity_date,
                amount=item.amount,
                probability=item.probability,
                decision_maker_contacted=item.decision_maker_contacted,
                next_step=item.next_step,
            )
            action_result = await service.generate_sales_action(item.model_dump(), score)
            results.append(
                PrioritizedOpportunity(
                    owner_id=owner_id,
                    owner_name=owner_name,
                    rank=index,
                    opportunity_id=item.opportunity_id,
                    opportunity_name=item.name,
                    priority_score=score,
                    action=action_result["action"],
                    action_reason=action_result["action_reason"],
                )
            )

    return PrioritizeResponse(results=results)


@router.post("/score", response_model=ScoreResponse)
def score_sales_activity(payload: ScoreRequest) -> ScoreResponse:
    actual_names = {task.opportunity_name for task in payload.actual_tasks}
    completed_rows = [
        CompletedRow(row_number=item.row_number, mark="")
        for item in payload.recommended_actions
        if item.opportunity_name in actual_names
    ]

    aligned_count = len(completed_rows)
    recommended_count = len(payload.recommended_actions)
    total_score = (
        100 if recommended_count == 0 else round((aligned_count / recommended_count) * 100)
    )

    penalty_total = sum(
        calc_pending_penalty(item.task_date, today=date.today())
        for item in payload.pending_tasks
    )
    final_score = max(total_score - penalty_total, 0)

    good_points = []
    if payload.actual_tasks:
        good_points.append("営業活動の記録が残されていた")
    if aligned_count:
        good_points.append("推奨アクションに沿った実績が確認できた")

    improvement_points = []
    if aligned_count < recommended_count:
        improvement_points.append("未実施の推奨アクションが残っています")
    if penalty_total:
        improvement_points.append("放置タスクによる減点が発生しています")

    status = "達成" if aligned_count == recommended_count else "一部未達"
    summary = (
        f"推奨アクションの{aligned_count}/{recommended_count}件を実行しました。"
        f"放置タスク減点後の最終スコアは{final_score}点です。"
    )

    return ScoreResponse(
        user_name=payload.user_name,
        total_score=total_score,
        summary=summary,
        good_points=good_points or ["営業活動の基本記録は確認できました"],
        improvement_points=improvement_points or ["大きな改善点は確認されませんでした"],
        action_alignment_status=status,
        completed_rows=completed_rows,
        penalty=PenaltySummary(
            pending_count=len(payload.pending_tasks),
            penalty_total=penalty_total,
            final_score=final_score,
        ),
    )
