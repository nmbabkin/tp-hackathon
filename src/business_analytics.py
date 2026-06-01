from src.business import (
    CATEGORY_SLA, COST_PER_HOUR, TRIAGE_MINUTES,
    WORK_HOURS_PER_DAY, DAILY_VOLUME, AFFECTED_EMPLOYEES_PER_INCIDENT,
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