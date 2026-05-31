import re

CATEGORIES = [
    "spam",
    "incidents",
    "hr",
    "access_requests",
    "hardware",
    "finance",
    "documents",
    "external",
    "info",
]
FALLBACK = "unclassified"

SPAM_KEYWORDS = [
    "выиграли", "iphone 15", "приз", "скидка", "деньги", "заработок",
    "лотерея", "кредит", "казино", "наследство", "exclusive offer",
    "limited time", "верификация аккаунта", "подтвердите личность",
    "аккаунт заблокирован", "срочно подтвердите",
]

INCIDENT_KEYWORDS = [
    "падает", "не работает", "не отвечает", "недоступен", "недоступна",
    "массовый сбой", "критический инцидент", "инцидент", "работа остановлена",
    "не запускается", "сбой авторизации", "active directory",
    "зависает", "ошибка", "ошибку", "не открывает", "перестал запускаться",
    "не могу войти", "код ошибки", "ошибка 500", "появляется ошибка",
]

HR_KEYWORDS = [
    "отпуск", "больничный", "больничный лист", "изменение графика",
    "график работы", "оформление нового сотрудника",
    "bolnichnyy", "otpusk", "grafik", "izmenenie grafika",
]

ACCESS_KEYWORDS = [
    "доступ", "права в", "запрос доступа", "выдать права", "нет доступа",
    "vpn", "1c", "gitlab", "confluence", "bi-система", "учётная запись",
    "после перевода", "для нового сотрудника", "логин",
]

HARDWARE_KEYWORDS = [
    "оборудование", "неисправность оборудования", "гарнитура", "принтер",
    "сканер", "ноутбук", "мышь", "клавиатура", "сломал", "замена",
]

FINANCE_KEYWORDS = [
    "счёт на оплату", "счет на оплату", "оплата", "оплате", "договор",
    "акт выполненных работ", "счёта", "договору",
]

DOCUMENTS_KEYWORDS = [
    "закрывающие документы", "финальная версия", "техническое задание",
    "правки к", "на согласование", "инструкция", "согласования",
]

EXTERNAL_KEYWORDS = [
    "внешнего пользователя", "от клиента", "жалоба клиента",
    "партнёр не может", "клиент",
]

INFO_KEYWORDS = [
    "дайджест", "плановый отчёт", "отчёт мониторинга",
    "обновления корпоративного портала", "перенос созвона",
    "сгенерировано автоматически", "no-reply", "noreply", "healthcheck",
]

MONITORING_MARKERS = [
    "uptime", "5xx", "среднее время ответа", "disk usage", "cpu usage", "метрика",
]

class Classifier:
    def __init__(self) -> None:
        self.categories = CATEGORIES
    def classify(self, email) -> str:
        text = self.normalize(email)
        if self.is_spam(text):
            return "spam"
        if self.is_auto_notification(email):
            return "info"
        if self.is_incident(email, text):
            return "incidents"
        if self.is_hr(text):
            return "hr"
        if self.is_access(text):
            return "access_requests"
        if self.is_hardware(text):
            return "hardware"
        if self.is_finance(text):
            return "finance"
        if self.is_documents(text):
            return "documents"
        if self.is_external(text):
            return "external"
        if self.is_info(text):
            return "info"
        
        return FALLBACK
    @staticmethod
    def normalize(email) -> str:
        subject = (email.subject or "").lower()
        body = (email.body or "").lower()
        return f"{body}\n{subject}"

    @staticmethod
    def _any(text: str, keywords: list[str]) -> bool:
        return any(kw in text for kw in keywords)
    
    def is_spam(self, text: str) -> bool:
        return self._any(text, SPAM_KEYWORDS)

    def is_auto_notification(self, email) -> bool:
        subject = (email.subject or "").lower()
        body = (email.body or "").lower()
        from_ = (email.from_ or "").lower()
        machine_sender = any(s in from_ for s in (
            "no-reply", "noreply", "alerts@", "monitoring", "grafana"
        ))
        machine_body = any(s in body for s in (
            "сгенерировано автоматически", "плановый отчёт", "автоматическое уведомление", "healthcheck"
        ))
        info_tag = bool(re.search(r"\[(info|warning)\]", subject))
        real_outage = any(s in body for s in (
            "работа остановлена", "массовый сбой", "критический инцидент"
        ))
        if real_outage:
            return False
        return (info_tag and (machine_sender or machine_body)) or machine_body
    
    def is_incident(self, email, text: str) -> bool:
        subject = (email.subject or "").lower()
        body = (email.body or "").lower()
        has_critical_tag = bool(re.search(r"\[(critical|urgent|warning)\]", subject))
        looks_like_monitoring = self._any(body, MONITORING_MARKERS)
        if has_critical_tag and looks_like_monitoring:
            return False
        return self._any(text, INCIDENT_KEYWORDS) or has_critical_tag
    
    def is_hr(self, text: str) -> bool:
        return self._any(text, HR_KEYWORDS)

    def is_access(self, text: str) -> bool:
        return self._any(text, ACCESS_KEYWORDS)

    def is_hardware(self, text: str) -> bool:
        return self._any(text, HARDWARE_KEYWORDS)

    def is_finance(self, text: str) -> bool:
        return self._any(text, FINANCE_KEYWORDS)

    def is_documents(self, text: str) -> bool:
        return self._any(text, DOCUMENTS_KEYWORDS)

    def is_external(self, text: str) -> bool:
        return self._any(text, EXTERNAL_KEYWORDS)

    def is_info(self, text: str) -> bool:
        return self._any(text, INFO_KEYWORDS)
