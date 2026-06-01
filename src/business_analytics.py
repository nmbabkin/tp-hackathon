from src.business import (
    CATEGORY_SLA, COST_PER_HOUR, TRIAGE_MINUTES,
    WORK_HOURS_PER_DAY, DAILY_VOLUME, AFFECTED_EMPLOYEES_PER_INCIDENT, 
    IMPLEMENTATION_COST, DISCOUNT_RATE_ANNUAL, HORIZON_MONTHS
)

class Analytics:
    def __init__(self, stats: dict) -> None:
        self.stats = stats
        self.total = sum(stats.values())
        self.sortable = self.total - stats.get("unparseable", 0)

    def labor_savings(self) -> dict:
        """Сколько труда экономит автосортировка — в часах и рублях. Считаем по трём сценариям времени на письмо"""
        result = {}
        for name, minutes in TRIAGE_MINUTES.items():
            saved_minutes = self.sortable * minutes
            saved_hours = saved_minutes / 60
            saved_rub = saved_hours * COST_PER_HOUR
            result[name] = {
                "minutes_per_mail": minutes,
                "saved_hours": round(saved_hours, 1),
                "saved_rub": round(saved_rub),
            }
        return result

    def scaled_fte(self, scenario: str = "base") -> dict:
        """Масштаб на реальный поток (DAILY_VOLUME писем/день)"""
        minutes = TRIAGE_MINUTES[scenario]
        hours_per_day = DAILY_VOLUME * minutes / 60
        fte = hours_per_day / WORK_HOURS_PER_DAY
        rub_per_day = hours_per_day * COST_PER_HOUR
        return {
            "daily_volume": DAILY_VOLUME,
            "hours_per_day": round(hours_per_day, 1),
            "fte": round(fte, 2),
            "rub_per_month": round(rub_per_day * 21),
        }

    def urgency_profile(self) -> dict:
        """Сколько писем каждого приоритета (P1...P4)"""
        profile = {}
        for category, count in self.stats.items():
            if category == "unparseable":
                continue
            priority = CATEGORY_SLA.get(category, {}).get("priority", "—")
            profile[priority] = profile.get(priority, 0) + count
        return profile

    def risk_zone(self) -> dict:
        """Письма под риском неверной маршрутизации и оценка стоимости.
        Консервативная модель: через потерю продуктивности команды"""
        unclassified = self.stats.get("unclassified", 0)
        incidents = self.stats.get("incidents", 0)
        misrouted_estimate = round(incidents * 0.1)
        at_risk = unclassified + misrouted_estimate

        delay_hours = 2
        cost_per_misroute = AFFECTED_EMPLOYEES_PER_INCIDENT * delay_hours * COST_PER_HOUR
        total_risk_cost = at_risk * cost_per_misroute

        return {
            "unclassified": unclassified,
            "misrouted_estimate": misrouted_estimate,
            "at_risk": at_risk,
            "cost_per_misroute": cost_per_misroute,
            "total_risk_cost": total_risk_cost,
        }
    
    # === ОТКЛЮЧЕНО: инвестиционная оценка через NPV/IRR ===
    # Метод NPV/IRR рассчитан на проекты с крупными
    # вложениями и окупаемостью в несколько лет. Наш проект окупается за ~1 месяц,
    # поэтому дисконтирование ничего не меняет, а IRR давал абсурдные
    # значения (~154000% годовых). Для такого масштаба корректен только
    # срок окупаемости (payback).
    #
    #
    # def investment_appraisal(self, scenario: str = "base") -> dict:
    #     """Инвестиционная оценка автоматизации как проекта: NPV, IRR, ROI, payback.
    #     Денежный поток = ежемесячная экономия труда; затраты = стоимость внедрения."""
    #     monthly_saving = self.scaled_fte(scenario)["rub_per_month"]
    #     c0 = IMPLEMENTATION_COST
    #     n = HORIZON_MONTHS
    #     r_month = (1 + DISCOUNT_RATE_ANNUAL) ** (1 / 12) - 1

    #     # NPV – сумма дисконтированных денежных потоков минус первоначальные затраты
    #     npv = -c0
    #     for t in range(1, n + 1):
    #         npv += monthly_saving / (1 + r_month) ** t

    #     # ROI за горизонт (недисконтированный, для наглядности)
    #     total_saving = monthly_saving * n
    #     roi = (total_saving - c0) / c0 * 100

    #     # Payback — за сколько месяцев накопленная экономия покроет затраты
    #     payback = c0 / monthly_saving if monthly_saving else None

    #     # IRR — ставка (в месяц), при которой NPV = 0. Ищем перебором.
    #     irr_month = self._irr(monthly_saving, c0, n)
    #     irr_annual = (1 + irr_month) ** 12 - 1 if irr_month is not None else None

    #     return {
    #         "monthly_saving": monthly_saving,
    #         "implementation_cost": c0,
    #         "discount_rate_annual": DISCOUNT_RATE_ANNUAL,
    #         "npv": round(npv),
    #         "roi_percent": round(roi),
    #         "payback_months": round(payback, 1) if payback else None,
    #         "irr_annual_percent": round(irr_annual * 100, 1) if irr_annual else None,
    #     }

    # @staticmethod
    # def _irr(monthly_saving: float, c0: float, n: int) -> float:
    #     """Внутренняя норма доходности (месячная) методом бисекции:
    #     ищем ставку, при которой NPV = 0."""
    #     def npv_at(rate):
    #         return -c0 + sum(monthly_saving / (1 + rate) ** t for t in range(1, n + 1))

    #     low, high = 0.0, 1.0   # ищем ставку в диапазоне 0..100% в месяц
    #     if npv_at(low) < 0:
    #         return None        # проект не окупается даже при нулевой ставке
    #     for _ in range(100):   # 100 итераций бисекции 
    #         mid = (low + high) / 2
    #         if npv_at(mid) > 0:
    #             low = mid
    #         else:
    #             high = mid
    #     return (low + high) / 2


    def payback(self, scenario: str = "base") -> dict:
        """ Срок окупаемости автоматизации """    
        monthly_saving = self.scaled_fte(scenario)["rub_per_month"]
        c0 = IMPLEMENTATION_COST
        payback_months = c0 / monthly_saving if monthly_saving else None
        roi_year = (monthly_saving * 12 - c0) / c0 * 100 if c0 else None
        return {
            "implementation_cost": c0,
            "monthly_saving": monthly_saving,
            "payback_months": round(payback_months, 1) if payback_months else None,
            "roi_year_percent": round(roi_year) if roi_year else None,
        }