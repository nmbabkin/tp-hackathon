import pytest
from src.parser import Email

FIXTURES = "tests/fixtures"

@pytest.fixture
def sample_email():
    """Готовый объект Email для тестов классификатора."""
    return Email(
        from_="user@company.ru",
        subject="Падает Service Desk",
        date="2025-04-17",
        body="Система не работает, массовый сбой",
        raw_text="...",
        source_path="/fake/path/mail.txt",
        is_parseable=True,
    )


@pytest.fixture
def valid_dir():
    return f"{FIXTURES}/valid_emails"

@pytest.fixture
def edge_dir():
    return f"{FIXTURES}/edge_cases"

@pytest.fixture
def unparseable_dir():
    return f"{FIXTURES}/unparseable"