from dataclasses import dataclass
from dataclasses import field
import json
import logging
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)
extensions = {".jpeg", ".jpg", ".png", ".gif", ".bin", ".pdf", ".zip"}
header_patterns = {
    "from_": r"^(?:From|От кого|Ot kogo)\s*:\s*(.+)$",
    "to": r"^(?:To|Кому|Komu)\s*:\s*(.+)$",
    "date": r"^(?:Date|Дата|Data)\s*:\s*(.+)$",
    "subject": r"^(?:Subject|Тема|Tema)\s*:\s*(.+)$",
}



@dataclass
class Email:
    from_: str = ""
    subject: str = ""
    date: Optional[str] = None
    body: str = ""
    raw_text: str = ""
    source_path: str = ""
    is_parseable: bool = True
    headers: dict = field(default_factory=dict)

def extract_headers(text: str) -> tuple[dict, str]:
    fields: dict = {}
    for key, pattern in header_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            fields[key] = match.group(1).strip()

    # тело идёт после первой пустой строки
    parts = re.split(r"\n\s*\n", text, maxsplit=1)
    if len(parts) == 2:
        return fields, parts[1].strip()

    # Пустой строки нет: телом считаем строки, которые не являются заголовками
    header_line = re.compile(
        r"^(?:From|От кого|Ot kogo|To|Кому|Komu|Date|Дата|Data|Subject|Тема|Tema)\s*:",
        re.IGNORECASE,
    )
    body_lines = [line for line in text.splitlines() if not header_line.match(line)]
    body = "\n".join(body_lines).strip()
    return fields, body


def parse_text(raw: str, path: str) -> Email:
    fields, body = extract_headers(raw)
    return Email(
        from_=fields.get("from_", ""),
        subject=fields.get("subject", ""),
        date=fields.get("date"),
        body=body,
        raw_text=raw,
        source_path=path,
        is_parseable=True,
        headers=fields,
    )

def parse_json(raw: str, path: str) -> Email:
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning("%s: повреждённый JSON (%s)", Path(path).name, exc)
        return Email(raw_text=raw, source_path=path, is_parseable=False)

    return Email(
        from_=str(data.get("from", data.get("from_", ""))),
        subject=str(data.get("subject", "")),
        date=data.get("date"),
        body=str(data.get("body", "")),
        raw_text=raw,
        source_path=path,
        is_parseable=True,
    )

def parse_email(path: str) -> Email:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix in extensions:
        logger.warning("%s: бинарный файл, не парсится", p.name)
        return Email(source_path=path, is_parseable=False)
    try:
        raw = p.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        logger.error("%s: не удалось прочитать файл (%s)", p.name, exc)
        return Email(source_path=path, is_parseable=False)

    if "\x00" in raw[:1024]:
        logger.warning("%s: похоже на бинарный файл, не парсится", p.name)
        return Email(raw_text=raw, source_path=path, is_parseable=False)
    
    if suffix == ".json":
        return parse_json(raw, path)
    return parse_text(raw, path)