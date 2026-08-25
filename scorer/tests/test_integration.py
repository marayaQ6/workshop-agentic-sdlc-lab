"""Integration tests composing parse_usage and score."""

from main import load_export
from usage import Result, parse_usage, score


def test_end_to_end_scoring_on_fixture():
    csv_text = load_export()
    accounts = parse_usage(csv_text)

    # hooli: stable seats, good logins, 1 ticket
    assert score(accounts["hooli"]) == Result(score=10, tier="HEALTHY", reasons=[])

    # acme: 10 -> 8 -> None (unrecorded usage, no deduction)
    assert score(accounts["acme"]) == Result(score=10, tier="HEALTHY", reasons=[])  # D3

    # globex: seats drop from 10 to 6 (-40% vs preceding month)
    assert score(accounts["globex"]) == Result(score=6, tier="MEDIUM", reasons=["seats down sharply"])  # D2

    # vandelay: 10 -> 6 -> 5 (-16.7% vs preceding month)
    assert score(accounts["vandelay"]) == Result(score=10, tier="HEALTHY", reasons=[])  # D1

    # initech: logins=2 (-3), tickets=3 (-2) -> score 5
    assert score(accounts["initech"]) == Result(score=5, tier="AT RISK", reasons=["low engagement", "unresolved support load"])  # D2

    # umbrella: single month, cannot fire seat decline
    assert score(accounts["umbrella"]) == Result(score=10, tier="HEALTHY", reasons=[])
