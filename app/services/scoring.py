from datetime import date
from typing import Optional


def calc_priority_score(
    close_date: Optional[str],
    last_activity_date: Optional[str],
    amount: float,
    probability: float,
    decision_maker_contacted: bool,
    next_step: Optional[str],
) -> int:
    today = date.today()
    score = 0

    if last_activity_date:
        days_since = (today - date.fromisoformat(last_activity_date)).days
        if days_since >= 7:
            score += 3

    if close_date:
        days_to = (date.fromisoformat(close_date) - today).days
        if days_to <= 14:
            score += 3

    if not decision_maker_contacted:
        score += 2
    if amount >= 5_000_000:
        score += 2
    if probability >= 70:
        score += 2
    if not next_step:
        score += 1

    return score
