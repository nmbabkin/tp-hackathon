import pytest
from src.classifier import Classifier
from src.parser import Email

def make_email(subject="", body="", from_=""):
    """быстро собрать Email для теста."""
    return Email(subject=subject, body=body, from_=from_, is_parseable=True)

@pytest.fixture
def classifier():
    return Classifier()

def test_incident(classifier):
    email = make_email(subject="Падает система", body="массовый сбой, работа остановлена")
    assert classifier.classify(email) == "incidents"

def test_spam(classifier):
    email = make_email(subject="Вы выиграли приз", body="срочно подтвердите личность")
    assert classifier.classify(email) == "spam"

def test_fallback_unclassified(classifier):
    """Письмо без ключевых слов → unclassified"""
    email = make_email(subject="Привет", body="как дела, давно не виделись")
    assert classifier.classify(email) == "unclassified"

def test_trap_critical_tag_but_monitoring(classifier):
    email = make_email(
        subject="[CRITICAL] Disk usage > 75%",
        body="Плановый отчёт. Uptime 99.9%, cpu usage в норме.",
        from_="no-reply@monitoring.internal",
    )
    assert classifier.classify(email) == "info"

def test_spam_beats_access(classifier):
    """спам отсекается раньше, чем сработает доступ."""
    email = make_email(
        subject="Аккаунт заблокирован",
        body="срочно подтвердите доступ, иначе аккаунт заблокирован",
    )
    assert classifier.classify(email) == "spam"

@pytest.mark.parametrize("subject,body,expected", [
    ("Запрос доступа к VPN", "выдать права", "access_requests"),
    ("Не работает принтер", "сломался, нужна замена", "hardware"),
    ("Заявление на отпуск", "прошу оформить отпуск", "hr"),
    ("Счёт на оплату", "оплата по договору", "finance"),
    ("Жалоба от клиента", "от клиента поступила жалоба", "external"),
])
def test_categories_parametrized(classifier, subject, body, expected):
    email = make_email(subject=subject, body=body)
    assert classifier.classify(email) == expected