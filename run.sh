set -e
echo "==> Mail Processor: запуск обработки почты..."

if [ ! -d "inbox" ]; then
    echo "ОШИБКА: папка 'inbox' не найдена" >&2
    exit 1
fi

if [ -d "venv" ]; then
    source venv/bin/activate
fi

mkdir -p output logs
python3 -m src.main --report 2>&1 | tee -a logs/run.log

echo "==> Готово. Результат в output/, логи в logs/processing.log"