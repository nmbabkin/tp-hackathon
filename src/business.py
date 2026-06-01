"""
Бизнес-конфигурация для аналитики обработки почты
Все параметры — экспертные допущения с обоснованием из источников.
Приоритеты и SLA задаются экспертно (это управленческое решение, как
в любой системе тикетинга), метрики поверх них считаются математически.
"""

# --- Приоритеты и SLA по категориям ---
# priority: P1 (критично) – ... – P4 (информационное)
# sla_minutes: целевое время реакции в минутах (None — реакция не требуется)
CATEGORY_SLA = {
    "incidents":       {"priority": "P1", "sla_minutes": 15},
    "access_requests": {"priority": "P2", "sla_minutes": 240},
    "finance":         {"priority": "P2", "sla_minutes": 240},
    "external":        {"priority": "P2", "sla_minutes": 240},
    "hardware":        {"priority": "P3", "sla_minutes": 480},
    "hr":              {"priority": "P3", "sla_minutes": 480},
    "documents":       {"priority": "P3", "sla_minutes": 480},
    "info":            {"priority": "P4", "sla_minutes": None},
    "spam":            {"priority": "—",  "sla_minutes": None},
    # Неизвестное по умолчанию отдается человеку (P2)
    "unclassified":    {"priority": "P2", "sla_minutes": 240},
}

# --- Стоимость труда (источник: hh.ru 2025, средняя ЗП техподдержки 60к) ---
SALARY_PER_MONTH = 60_000      # ₽/мес, средняя по РФ (hh.ru, 2025)
WORK_HOURS_PER_MONTH = 168     # 21 рабочий день × 8 часов
OVERHEAD_COEF = 1.5            # налоги, взносы, рабочее место, ПО (Total CSS / Base salary)
COST_PER_HOUR = round(SALARY_PER_MONTH / WORK_HOURS_PER_MONTH * OVERHEAD_COEF)  # ≈ 535 ₽/час

# --- Время на ручную сортировку одного письма ---
# Три сценария: оптимистичный / базовый / консервативный
TRIAGE_MINUTES = {"low": 1.0, "base": 1.5, "high": 3.0}

WORK_HOURS_PER_DAY = 8

# --- Параметры масштабирования на реальный поток заказчика ---
DAILY_VOLUME = 300             # писем/день в отделе поддержки 

# --- Контекст для cost of misrouting ---
# Gartner: до $5600/мин простоя ИТ; Atlassian: 100–540к $/час.
# В расчёте НЕ используем напрямую (это про гигантов)
# берем консервативную модель через потерю продуктивности команды.
AFFECTED_EMPLOYEES_PER_INCIDENT = 5   # сколько человек простаивают при инциденте 