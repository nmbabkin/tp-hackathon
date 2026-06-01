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


def generate_html_report(stats: dict, path: str = "output/report.html") -> str:
    """Генерирует статический HTML-отчёт с метриками"""
    from pathlib import Path
    a = Analytics(stats)
    auto = a.automation_rate()
    fte = a.scaled_fte()
    urgency = a.urgency_profile()
    risk = a.risk_zone()
    pb = a.payback()

    def rub(n):
        return f"{n:,}".replace(",", " ")
    
    max_u = max(urgency.get(p, 0) for p in ["P1", "P2", "P3", "P4"]) or 1
    urgency_labels = {
        "P1": ("Критично", "≤15 мин", "#e5484d"),
        "P2": ("Высокий", "≤4 часа", "#f5a623"),
        "P3": ("Обычный", "≤1 день", "#3b82f6"),
        "P4": ("Информационные", "без срока", "#9ca3af"),    }
    bars = ""
    for p in ["P1", "P2", "P3", "P4"]:
        count = urgency.get(p, 0)
        name, sla, color = urgency_labels[p]
        width = count / max_u * 100
        bars += f"""
        <div class="bar-row">
          <div class="bar-label"><b>{p}</b> {name}<span class="sla">{sla}</span></div>
          <div class="bar-track"><div class="bar-fill" style="width:{width}%;background:{color}"></div></div>
          <div class="bar-count">{count}</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Отчёт по обработке почты</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:-apple-system,Segoe UI,Roboto,sans-serif; background:#f5f6f8;
         color:#1a1a2e; padding:40px 20px; }}
  .wrap {{ max-width:880px; margin:0 auto; }}
  h1 {{ font-size:24px; margin-bottom:4px; }}
  .sub {{ color:#6b7280; font-size:14px; margin-bottom:28px; }}
  .kpi {{ background:linear-gradient(135deg,#1a1a2e,#2d3561); color:#fff;
          border-radius:16px; padding:28px 32px; margin-bottom:20px; }}
  .kpi .big {{ font-size:48px; font-weight:700; }}
  .kpi .lbl {{ font-size:14px; opacity:.85; margin-top:4px; }}
  .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:20px; }}
  .card {{ background:#fff; border-radius:14px; padding:22px 24px;
           box-shadow:0 1px 3px rgba(0,0,0,.06); }}
  .card h3 {{ font-size:13px; text-transform:uppercase; letter-spacing:.5px;
             color:#6b7280; margin-bottom:12px; }}
  .card .val {{ font-size:28px; font-weight:700; }}
  .card .note {{ font-size:13px; color:#6b7280; margin-top:6px; }}
  .section {{ background:#fff; border-radius:14px; padding:22px 24px; margin-bottom:20px;
              box-shadow:0 1px 3px rgba(0,0,0,.06); }}
  .section h3 {{ font-size:13px; text-transform:uppercase; letter-spacing:.5px;
                color:#6b7280; margin-bottom:16px; }}
  .bar-row {{ display:flex; align-items:center; gap:12px; margin-bottom:10px; }}
  .bar-label {{ width:240px; font-size:14px; white-space:nowrap; }}  .bar-label .sla {{ color:#9ca3af; font-size:12px; margin-left:8px; }}
  .bar-track {{ flex:1; background:#f0f1f3; border-radius:6px; height:22px; }}
  .bar-fill {{ height:100%; border-radius:6px; transition:width .3s; }}
  .bar-count {{ width:36px; text-align:right; font-weight:600; font-size:14px; }}
  .assumptions {{ background:#fafbfc; border:1px solid #eceef1; border-radius:14px;
                  padding:20px 24px; font-size:13px; color:#6b7280; line-height:1.7; }}
  .assumptions h3 {{ font-size:13px; text-transform:uppercase; color:#9ca3af;
                     margin-bottom:10px; }}
  .assumptions b {{ color:#1a1a2e; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>Отчёт по обработке корпоративной почты</h1>
  <div class="sub">Обработано {auto['total']} писем · бизнес-аналитика mail-sort</div>

  <div class="kpi">
    <div class="big">{auto['rate_percent']}%</div>
    <div class="lbl">Уровень автоматизации — {auto['automated']} из {auto['total']} писем обработано без участия человека</div>
  </div>

  <div class="grid">
    <div class="card">
      <h3>Экономия труда</h3>
      <div class="val">{fte['fte']} FTE</div>
      <div class="note">{fte['hours_per_day']} ч/день при потоке {fte['daily_volume']} писем/день · {rub(fte['rub_per_month'])} ₽/мес</div>
    </div>
    <div class="card">
      <h3>Окупаемость</h3>
      <div class="val">{pb['payback_months']} мес</div>
      <div class="note">Внедрение {rub(pb['implementation_cost'])} ₽ · ROI за год ≈ {pb['roi_year_percent']}%</div>
    </div>
    <div class="card">
      <h3>Требуют человека</h3>
      <div class="val">{auto['needs_human']}</div>
      <div class="note">не классифицировано · {auto['unparseable']} не распознано</div>
    </div>
    <div class="card">
      <h3>Зона риска</h3>
      <div class="val">{rub(risk['total_risk_cost'])} ₽</div>
      <div class="note">{risk['at_risk']} писем под риском неверной маршрутизации</div>
    </div>
  </div>

  <div class="section">
    <h3>Профиль срочности</h3>
    {bars}
  </div>

  <div class="assumptions">
    <h3>Допущения и источники</h3>
    <b>Зарплата специалиста:</b> 60 000 ₽/мес (hh.ru, 2025) · <b>стоимость часа:</b> ~536 ₽ (с учётом налогов и накладных, коэф. 1.5)<br>
    <b>Время на сортировку письма:</b> 1.5 мин (отраслевые бенчмарки triage) · <b>поток:</b> 300 писем/день<br>
    <b>Cost of misrouting:</b> консервативная модель через потерю продуктивности команды. Международный контекст: Gartner — до $5600/мин простоя ИТ.<br>
    <b>Окупаемость:</b> метод payback. NPV/IRR не применялись — при окупаемости за ~месяц дисконтированные методы дают некорректные значения.<br>
    <i>Экономия рассчитана на этапе сортировки (триажа), не на решении обращений.</i>
  </div>
</div>
</body>
</html>"""

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return str(out)