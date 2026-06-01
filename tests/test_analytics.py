import pytest
from src.business_analytics import Analytics

# Фиксированная статистика для проверки расчётов
STATS = {
    "spam": 6, "incidents": 35, "hr": 6, "access_requests": 22,
    "hardware": 8, "finance": 8, "documents": 5, "external": 4,
    "info": 7, "unclassified": 5, "unparseable": 3,
}


@pytest.fixture
def analytics():
    return Analytics(STATS)

def test_total_and_sortable(analytics):
    assert analytics.total == 109
    assert analytics.sortable == 106  # минус 3 unparseable

def test_automation_rate(analytics):
    auto = analytics.automation_rate()
    assert auto["total"] == 109
    assert auto["automated"] == 101  # 109 - 5 unclassified - 3 unparseable
    assert auto["rate_percent"] == 92.7

def test_automation_rate_excludes_unclassified():
    """unclassified и unparseable НЕ считаются автоматизированными"""
    stats = {"incidents": 10, "unclassified": 5, "unparseable": 5}
    auto = Analytics(stats).automation_rate()
    assert auto["automated"] == 10
    assert auto["rate_percent"] == 50.0

def test_labor_savings_scenarios(analytics):
    """Три сценария: больше минут на письмо — больше экономия"""
    saved = analytics.labor_savings()
    assert saved["low"]["saved_hours"] < saved["base"]["saved_hours"]
    assert saved["base"]["saved_hours"] < saved["high"]["saved_hours"]

def test_scaled_fte(analytics):
    fte = analytics.scaled_fte()
    assert fte["daily_volume"] == 300
    assert fte["fte"] > 0
    assert fte["rub_per_month"] > 0

def test_urgency_profile_sums(analytics):
    """Сумма по приоритетам = все письма кроме unparseable"""
    profile = analytics.urgency_profile()
    assert sum(profile.values()) == 106  # 109 - 3 unparseable

def test_urgency_incidents_are_p1(analytics):
    """Инциденты должны попадать в P1"""
    profile = analytics.urgency_profile()
    assert profile.get("P1", 0) == 35  # все incidents

def test_risk_zone(analytics):
    risk = analytics.risk_zone()
    assert risk["unclassified"] == 5
    assert risk["at_risk"] >= 5  # минимум unclassified
    assert risk["total_risk_cost"] > 0

def test_payback(analytics):
    pb = analytics.payback()
    assert pb["payback_months"] > 0
    assert pb["implementation_cost"] == 100_000

def test_empty_stats():
    """Граничный случай: пустая статистика не падает"""
    a = Analytics({})
    assert a.total == 0
    auto = a.automation_rate()
    assert auto["rate_percent"] == 0