from src.router import Router
from src.parser import Email


def make_email(tmp_path, name="mail.txt", content="тело письма"):
    """Создаёт реальный файл во временной папке и возвращает Email на него"""
    src_file = tmp_path / name
    src_file.write_text(content, encoding="utf-8")
    return Email(
        subject="тест", body=content, source_path=str(src_file), is_parseable=True
    )


def test_creates_category_folders(tmp_path):
    """При инициализации создаются папки всех категорий"""
    out = tmp_path / "output"
    Router(output_dir=str(out), log_path=str(tmp_path / "log.log"))
    assert (out / "incidents").is_dir()
    assert (out / "unclassified").is_dir()
    assert (out / "unparseable").is_dir()


def test_route_copies_file(tmp_path):
    """route() копирует файл в папку нужной категории"""
    out = tmp_path / "output"
    router = Router(output_dir=str(out), log_path=str(tmp_path / "log.log"))
    email = make_email(tmp_path, name="mail_0001.txt")
    router.route(email, "incidents")
    assert (out / "incidents" / "mail_0001.txt").exists()


def test_route_keeps_original(tmp_path):
    """Исходный файл остаётся на месте (копируем)"""
    out = tmp_path / "output"
    router = Router(output_dir=str(out), log_path=str(tmp_path / "log.log"))
    email = make_email(tmp_path, name="mail_0002.txt")
    router.route(email, "hardware")
    assert (tmp_path / "mail_0002.txt").exists()


def test_statistics_count(tmp_path):
    """Статистика правильно считает письма по категориям"""
    out = tmp_path / "output"
    router = Router(output_dir=str(out), log_path=str(tmp_path / "log.log"))
    router.route(make_email(tmp_path, name="a.txt"), "incidents")
    router.route(make_email(tmp_path, name="b.txt"), "incidents")
    router.route(make_email(tmp_path, name="c.txt"), "spam")
    stats = router.get_statistics()
    assert stats["incidents"] == 2
    assert stats["spam"] == 1


def test_rerun_does_not_crash(tmp_path):
    """Повторная инициализация на существующих папках не падает"""
    out = tmp_path / "output"
    Router(output_dir=str(out), log_path=str(tmp_path / "log.log"))
    Router(output_dir=str(out), log_path=str(tmp_path / "log.log"))  # второй раз
    assert (out / "incidents").is_dir()