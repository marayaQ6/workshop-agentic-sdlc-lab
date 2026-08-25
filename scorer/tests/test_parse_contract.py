"""Contract tests for usage export parsing."""

from main import load_export
from usage import MonthSnapshot, parse_usage


def test_parse_usage_full_fixture():
    csv_text = load_export()
    parsed = parse_usage(csv_text)

    expected = {
        "hooli": [
            MonthSnapshot(account_id="hooli", month="2026-01", seats_active=12, logins=40, tickets_open=0),
            MonthSnapshot(account_id="hooli", month="2026-02", seats_active=12, logins=45, tickets_open=1),
        ],
        "acme": [
            MonthSnapshot(account_id="acme", month="2026-01", seats_active=10, logins=5, tickets_open=0),
            MonthSnapshot(account_id="acme", month="2026-02", seats_active=8, logins=5, tickets_open=0),
            MonthSnapshot(account_id="acme", month="2026-03", seats_active=None, logins=5, tickets_open=0),  # D3
        ],
        "globex": [
            MonthSnapshot(account_id="globex", month="2026-01", seats_active=4, logins=5, tickets_open=0),
            MonthSnapshot(account_id="globex", month="2026-02", seats_active=10, logins=5, tickets_open=0),
            MonthSnapshot(account_id="globex", month="2026-03", seats_active=6, logins=5, tickets_open=0),
        ],
        "vandelay": [
            MonthSnapshot(account_id="vandelay", month="2026-01", seats_active=10, logins=5, tickets_open=0),
            MonthSnapshot(account_id="vandelay", month="2026-02", seats_active=6, logins=5, tickets_open=0),
            MonthSnapshot(account_id="vandelay", month="2026-03", seats_active=5, logins=5, tickets_open=0),
        ],
        "initech": [
            MonthSnapshot(account_id="initech", month="2026-01", seats_active=6, logins=4, tickets_open=0),
            MonthSnapshot(account_id="initech", month="2026-02", seats_active=6, logins=2, tickets_open=3),
        ],
        "umbrella": [
            MonthSnapshot(account_id="umbrella", month="2026-02", seats_active=3, logins=10, tickets_open=0),
        ],
    }

    assert parsed == expected


def test_parse_usage_blank_seats_parsed_as_none():
    csv_text = (
        "account_id,month,seats_active,logins,tickets_open\n"
        "acme,2026-03,,5,0\n"
    )
    parsed = parse_usage(csv_text)
    assert parsed["acme"][0].seats_active is None  # D3


def test_parse_usage_orders_months_in_ascending_order():
    csv_text = (
        "account_id,month,seats_active,logins,tickets_open\n"
        "custom,2026-03,10,5,0\n"
        "custom,2026-01,10,5,0\n"
        "custom,2026-02,10,5,0\n"
    )
    parsed = parse_usage(csv_text)
    assert [m.month for m in parsed["custom"]] == ["2026-01", "2026-02", "2026-03"]


def test_parse_usage_omits_account_with_no_months():
    csv_text = "account_id,month,seats_active,logins,tickets_open\n"
    parsed = parse_usage(csv_text)
    assert parsed == {}


def test_parse_usage_casts_numeric_fields_to_integers():
    csv_text = (
        "account_id,month,seats_active,logins,tickets_open\n"
        "hooli,2026-01,12,40,0\n"
    )
    parsed = parse_usage(csv_text)
    snapshot = parsed["hooli"][0]
    assert isinstance(snapshot.seats_active, int)
    assert isinstance(snapshot.logins, int)
    assert isinstance(snapshot.tickets_open, int)
