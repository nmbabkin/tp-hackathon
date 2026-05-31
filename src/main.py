import argparse
from pathlib import Path
from src.classifier import Classifier
from src.parser import parse_email
from src.router import Router

def main() -> None:
    arg_parser = argparse.ArgumentParser(description="Обработка корпоративной почты")
    arg_parser.add_argument("--inbox", default="inbox", help="папка с входящими письмами")
    arg_parser.add_argument("--output", default="output", help="папка для результата")
    arg_parser.add_argument(
        "--dry-run", action="store_true", help="не копировать файлы, только показать статистику"
    )
    args = arg_parser.parse_args()
    inbox = Path(args.inbox)
    if not inbox.is_dir():
        raise SystemExit(f"ERROR: папка '{inbox}' не найдена")

    classifier = Classifier()
    router = Router(output_dir=args.output)

    for file_path in sorted(inbox.iterdir()):
        if file_path.name == ".DS_Store" or file_path.is_dir():
            continue

        email = parse_email(str(file_path))
        if email.is_parseable:
            category = classifier.classify(email)
        else:
            category = "unparseable"

        if not args.dry_run:
            router.route(email, category)
        else:
            router.stats[category] += 1

    router.print_summary()

if __name__ == "__main__":
    main()