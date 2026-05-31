import logging
import shutil
from collections import Counter
from pathlib import Path
from src.classifier import CATEGORIES, FALLBACK

ALL_FOLDERS = CATEGORIES + [FALLBACK, "unparseable"]

class Router:
    def __init__(self, output_dir: str = "output", log_path: str = "logs/processing.log") -> None:
        self.output_dir = Path(output_dir)
        self.stats: Counter = Counter()
        self.logger = self._setup_logging(log_path)
        self._create_dirs()

    def _setup_logging(self, log_path: str) -> logging.Logger:
        log_file = Path(log_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger = logging.getLogger("mail_processor")
        logger.setLevel(logging.INFO)
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        )
        logger.addHandler(handler)
        return logger

    def _create_dirs(self) -> None:
        for folder in ALL_FOLDERS:
            (self.output_dir / folder).mkdir(parents=True, exist_ok=True)

    def route(self, email, category: str) -> None:
        target_dir = self.output_dir / category
        target_dir.mkdir(parents=True, exist_ok=True)
        name = Path(email.source_path).name

        try:
            shutil.copy2(email.source_path, target_dir)
        except (OSError, shutil.Error) as exc:
            self.logger.error("%s: ошибка копирования в %s/ (%s)", name, category, exc)
            return

        self.stats[category] += 1

        if category == "unparseable":
            self.logger.warning("%s: не распарсилось, скопировано в unparseable/", name)
        elif category == FALLBACK:
            self.logger.warning("%s: не подошло ни под одну категорию → unclassified/", name)
        else:
            self.logger.info("%s → %s/", name, category)

    def get_statistics(self) -> dict:
        return dict(self.stats)

    def print_summary(self) -> None:
        total = sum(self.stats.values())
        lines = [f"ОБРАБОТАНО: {total} файлов"]
        for folder in ALL_FOLDERS:
            count = self.stats.get(folder, 0)
            if count:
                lines.append(f"  {folder:18} {count}")
        summary = "\n".join(lines)
        print(summary)
        self.logger.info("Итоговая статистика:\n%s", summary)