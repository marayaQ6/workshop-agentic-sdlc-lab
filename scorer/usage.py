"""Interface definitions for usage export parsing and account health scoring."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import io


@dataclass(frozen=True)
class MonthSnapshot:
    account_id: str
    month: str  # "YYYY-MM"
    seats_active: int | None
    logins: int
    tickets_open: int


@dataclass(frozen=True)
class Result:
    score: int
    tier: str  # "HEALTHY" | "MEDIUM" | "AT RISK"
    reasons: list[str]


def parse_usage(csv_text: str) -> dict[str, list[MonthSnapshot]]:
    """Group the export text by account, each list in ascending month order.

    An account with no months to score is omitted, so score() is never
    called with an empty list.
    """
    reader = csv.DictReader(io.StringIO(csv_text))
    accounts: dict[str, list[MonthSnapshot]] = {}

    for row in reader:
        account_id = row["account_id"].strip()
        if not account_id:
            continue

        seats_raw = row["seats_active"].strip()
        seats_active = int(seats_raw) if seats_raw else None

        snapshot = MonthSnapshot(
            account_id=account_id,
            month=row["month"].strip(),
            seats_active=seats_active,
            logins=int(row["logins"].strip()),
            tickets_open=int(row["tickets_open"].strip()),
        )
        if account_id not in accounts:
            accounts[account_id] = []
        accounts[account_id].append(snapshot)

    for account_id in accounts:
        accounts[account_id].sort(key=lambda m: m.month)

    return accounts


def score(months: list[MonthSnapshot]) -> Result:
    """Score one account's months. Never reads the CSV."""
    if not months:
        raise ValueError("months list cannot be empty")

    latest = months[-1]
    reasons: list[str] = []
    current_score = 10

    # Rule 1: The latest month's seat count has fallen by 40% or more
    # Evaluated against the immediately preceding month present for that account.
    if len(months) >= 2:
        prev = months[-2].seats_active
        curr = latest.seats_active
        if prev is not None and curr is not None and prev > 0:
            if (prev - curr) * 5 >= prev * 2:
                current_score -= 4
                reasons.append("seats down sharply")

    # Rule 2: Fewer than 3 logins in the latest month
    if latest.logins < 3:
        current_score -= 3
        reasons.append("low engagement")

    # Rule 3: 2 or more tickets open in the latest month
    if latest.tickets_open >= 2:
        current_score -= 2
        reasons.append("unresolved support load")

    current_score = max(0, current_score)

    if current_score >= 8:
        tier = "HEALTHY"
    elif current_score >= 6:
        tier = "MEDIUM"
    else:
        tier = "AT RISK"

    return Result(score=current_score, tier=tier, reasons=reasons)

