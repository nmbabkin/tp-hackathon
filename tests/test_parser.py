import pytest

from src.parser import parse_email, Email


def test_parse_valid_txt(valid_dir):
    """Корректное письмо .txt: поля заполнены, is_parseable=True."""
    email = parse_email(f"{valid_dir}/incident.txt")
    assert email.is_parseable is True
    assert email.subject == "Падает Service Desk"
    assert "массовый сбой" in email.body


def test_parse_no_extension(edge_dir):
    """Файл без расширения парсится как текст."""
    email = parse_email(f"{edge_dir}/no_extension")
    assert email.is_parseable is True
    assert email.subject == "Письмо без расширения"


def test_parse_jpeg_unparseable(unparseable_dir):
    """Бинарный .jpeg не парсится, но без падения."""
    email = parse_email(f"{unparseable_dir}/image.jpeg")
    assert email.is_parseable is False


def test_parse_broken_json_unparseable(edge_dir):
    """Битый JSON помечается is_parseable=False, не роняет программу."""
    email = parse_email(f"{edge_dir}/broken.json")
    assert email.is_parseable is False


def test_parse_empty_file(edge_dir):
    """Пустой файл не вызывает исключение."""
    email = parse_email(f"{edge_dir}/empty.txt")
    assert email.is_parseable is True
    assert email.body == ""


def test_translit_headers_parsed(valid_dir):
    """Транслит-заголовки (Tema, Ot kogo) распознаются."""
    email = parse_email(f"{valid_dir}/translit.txt")
    assert email.is_parseable is True
    assert email.subject == "Izmenenie grafika raboty"


@pytest.mark.parametrize("filename,expected_subject", [
    ("incident.txt", "Падает Service Desk"),
    ("access.txt", "Запрос доступа к VPN"),
    ("hardware.txt", "Не работает принтер"),
    ("spam.txt", "Вы выиграли iPhone 15!"),
])
def test_subject_extraction(valid_dir, filename, expected_subject):
    """Параметризованный тест: тема извлекается из разных писем."""
    email = parse_email(f"{valid_dir}/{filename}")
    assert email.subject == expected_subject