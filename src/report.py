from src.business_analytics import Analytics

def print_console_report(stats: dict) -> None:
    """Печатает отчёт по статистике обработки почты"""
    a = Analytics(stats)
    auto = a.automation_rate()
    fte = a.scaled_fte()
    urgency = a.urgency_profile()
    risk = a.risk_zone()
    pb = a.payback()
    line = "═" * 47
    print()
    print(line)
    print("  ОТЧЁТ ПО ОБРАБОТКЕ ПОЧТЫ")
    print(line)

    # KPI
    print(f"\n  УРОВЕНЬ АВТОМАТИЗАЦИИ:  {auto['rate_percent']}%")
    print(f"  {auto['automated']} из {auto['total']} писем обработано автоматически")
    print(f"  Требуют человека: {auto['needs_human']}   Не распознано: {auto['unparseable']}")

    # Экономия
    print(f"\n  ЭКОНОМИЯ ТРУДА (при потоке {fte['daily_volume']} писем/день)")
    print(f"  {fte['hours_per_day']} ч/день  ≈  {fte['fte']} FTE")
    print(f"  Экономия: {fte['rub_per_month']:,} ₽/мес".replace(",", " "))

    # Окупаемость
    print(f"\n  ОКУПАЕМОСТЬ")
    print(f"  Внедрение: {pb['implementation_cost']:,} ₽".replace(",", " "))
    print(f"  Окупается за {pb['payback_months']} мес   (ROI/год ≈ {pb['roi_year_percent']}%)")

    # Профиль срочности
    print(f"\n  ПРОФИЛЬ СРОЧНОСТИ")
    labels = {"P1": "критично (≤15 мин)", "P2": "высокий (≤4 ч)",
              "P3": "обычный (≤1 дн)", "P4": "информац.", "—": "спам/проч."}
    for p in ["P1", "P2", "P3", "P4"]:
        count = urgency.get(p, 0)
        bar = "█" * count
        print(f"  {p} {labels[p]:20} {count:3}  {bar}")

    # Риски
    print(f"\n  ЗОНА РИСКА")
    print(f"  Под риском маршрутизации: {risk['at_risk']} писем")
    print(f"  Оценка стоимости: {risk['total_risk_cost']:,} ₽/прогон".replace(",", " "))

    print(line)
    print()