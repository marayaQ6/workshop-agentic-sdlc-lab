"""Contract tests for account health scoring."""

from usage import MonthSnapshot, Result, score


def test_score_perfect_account():
    months = [
        MonthSnapshot(account_id="hooli", month="2026-01", seats_active=12, logins=40, tickets_open=0),
        MonthSnapshot(account_id="hooli", month="2026-02", seats_active=12, logins=45, tickets_open=1),
    ]
    result = score(months)
    assert result == Result(score=10, tier="HEALTHY", reasons=[])


def test_score_single_month_cannot_fire_seat_decline():
    months = [
        MonthSnapshot(account_id="umbrella", month="2026-02", seats_active=3, logins=10, tickets_open=0),
    ]
    result = score(months)
    assert result == Result(score=10, tier="HEALTHY", reasons=[])


def test_score_seat_decline_sharp_drop_deducts_four():
    months = [
        MonthSnapshot(account_id="globex", month="2026-01", seats_active=4, logins=5, tickets_open=0),
        MonthSnapshot(account_id="globex", month="2026-02", seats_active=10, logins=5, tickets_open=0),
        MonthSnapshot(account_id="globex", month="2026-03", seats_active=6, logins=5, tickets_open=0),
    ]
    result = score(months)
    assert result.score == 6  # D2
    assert result.tier == "MEDIUM"  # D2
    assert result.reasons == ["seats down sharply"]


def test_score_seat_decline_compares_to_immediately_preceding_month():
    months = [
        MonthSnapshot(account_id="vandelay", month="2026-01", seats_active=10, logins=5, tickets_open=0),
        MonthSnapshot(account_id="vandelay", month="2026-02", seats_active=6, logins=5, tickets_open=0),
        MonthSnapshot(account_id="vandelay", month="2026-03", seats_active=5, logins=5, tickets_open=0),
    ]
    result = score(months)
    assert result.score == 10  # D1
    assert result.tier == "HEALTHY"  # D1
    assert result.reasons == []  # D1


def test_score_blank_seats_does_not_trigger_seat_decline():
    months = [
        MonthSnapshot(account_id="acme", month="2026-01", seats_active=10, logins=5, tickets_open=0),
        MonthSnapshot(account_id="acme", month="2026-02", seats_active=8, logins=5, tickets_open=0),
        MonthSnapshot(account_id="acme", month="2026-03", seats_active=None, logins=5, tickets_open=0),
    ]
    result = score(months)
    assert result.score == 10  # D3
    assert result.tier == "HEALTHY"  # D3
    assert result.reasons == []  # D3


def test_score_low_engagement_deducts_three():
    months = [
        MonthSnapshot(account_id="sample", month="2026-01", seats_active=10, logins=10, tickets_open=0),
        MonthSnapshot(account_id="sample", month="2026-02", seats_active=10, logins=2, tickets_open=0),
    ]
    result = score(months)
    assert result.score == 7  # D2
    assert result.tier == "MEDIUM"  # D2
    assert result.reasons == ["low engagement"]


def test_score_unresolved_support_load_deducts_two():
    months = [
        MonthSnapshot(account_id="sample", month="2026-01", seats_active=10, logins=10, tickets_open=0),
        MonthSnapshot(account_id="sample", month="2026-02", seats_active=10, logins=10, tickets_open=2),
    ]
    result = score(months)
    assert result.score == 8  # D2
    assert result.tier == "HEALTHY"  # D2
    assert result.reasons == ["unresolved support load"]


def test_score_five_is_in_at_risk_tier():
    months = [
        MonthSnapshot(account_id="initech", month="2026-01", seats_active=6, logins=4, tickets_open=0),
        MonthSnapshot(account_id="initech", month="2026-02", seats_active=6, logins=2, tickets_open=3),
    ]
    result = score(months)
    assert result.score == 5  # D2
    assert result.tier == "AT RISK"  # D2
    assert result.reasons == ["low engagement", "unresolved support load"]


def test_score_all_rules_fire_in_specified_reason_order():
    months = [
        MonthSnapshot(account_id="crisis", month="2026-01", seats_active=10, logins=10, tickets_open=0),
        MonthSnapshot(account_id="crisis", month="2026-02", seats_active=5, logins=1, tickets_open=4),
    ]
    result = score(months)
    assert result.score == 1  # D2
    assert result.tier == "AT RISK"  # D2
    assert result.reasons == ["seats down sharply", "low engagement", "unresolved support load"]


def test_score_only_evaluates_latest_month_for_logins_and_tickets():
    months = [
        MonthSnapshot(account_id="recovered", month="2026-01", seats_active=10, logins=0, tickets_open=10),
        MonthSnapshot(account_id="recovered", month="2026-02", seats_active=10, logins=10, tickets_open=0),
    ]
    result = score(months)
    assert result == Result(score=10, tier="HEALTHY", reasons=[])
