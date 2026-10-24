# Лабораторная работа № 2. Потоковый анализатор файлов

Выполнила Пичугина Елизавета, М8О-106БВ-26
---

## О проекте

`streamstats` — консольная утилита на Python для **потокового анализа событий**
из файлов CSV и JSONL. Читает входные файлы **построчно**, валидирует
обязательные поля каждого события, делает статистику и формирует
**JSON-отчёт**.

Свойства:

- **Потоковость**: файлы не читаются целиком в память (`read()`/`readlines()` не используются).
- **Два формата**: CSV с заголовком и JSONL (по одному JSON-объекту на строку).
- **Два режима**: строгий (остановка на первой битой строке, код возврата 2)
  и `--skip-invalid` (пропуск с WARNING в `WARNING.log`, счётчик в отчёт).
- **Объединение нескольких файлов** в один отчёт.
- **Раздельные счётчики** `ERROR` и `CRITICAL` + top-5 с приоритетом `CRITICAL`.

## Модель события

Обязательные поля каждой записи:

| Поле | Тип | Ограничения |
|---|---|---|
| `timestamp` | строка | ISO 8601 |
| `level` | строка | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `source` | строка | непустая |
| `message` | строка | любая |

## Установка и запуск

### Требования

- Python 3.12+
- `uv` (или стандартный `venv` + `pip`)

### Установка через `uv`

```bash
uv sync
```

### Установка через `venv` + `pip`

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

### Запуск CLI

**1. Базовый анализ CSV (вывод в терминал):**
```bash
python -m streamstats analyze samples/sample1.csv --format csv
```

**2. Объединение нескольких файлов и запись в файл:**
```bash
python -m streamstats analyze samples/sample1.csv samples/sample2.csv --format csv --output report.json
```

**3. Анализ JSONL:**
```bash
python -m streamstats analyze samples/sample.jsonl --format jsonl
```

**4. Строгий режим (обработка ошибки):**
В `broken.csv` есть строка с невалидным уровнем. Без флага программа остановится и вернёт код 2.
```bash
python -m streamstats analyze samples/broken.csv --format csv
```

**5. Мягкий режим (`--skip-invalid`):**
Пропускает битую строку, пишет WARNING в `WARNING.log` и добавляет `skipped_lines` в отчёт.
```bash
python -m streamstats analyze samples/broken.csv --format csv --skip-invalid
```

### Коды возврата

| Код | Значение |
|---|---|
| `0` | успешный анализ и запись отчёта |
| `2` | доменная ошибка (`StreamStatsError`), отсутствие файла или ошибка CLI |

## Формат отчёта

Пример `report.json`:

```json
{
  "min_timestamp": "2024-01-01T00:00:00+00:00",
  "max_timestamp": "2024-01-01T00:00:20+00:00",
  "total_events": 5,
  "level": {"INFO": 1, "ERROR": 1, "CRITICAL": 2, "WARNING": 1},
  "source": {"app": 3, "db": 2},
  "top_CRITICAL_sources": [
    {"sources": "app", "count": 1},
    {"sources": "db", "count": 1}
  ],
  "top_ERROR_sources": [
    {"sources": "db", "count": 1}
  ],
  "top_ERROR|CRITICAL": [
    {"sources": "db", "critical": 1, "error": 1},
    {"sources": "app", "critical": 1, "error": 0}
  ]
}
```

- `min_timestamp` / `max_timestamp` — первая и последняя метки (ISO 8601, UTC),
  пустая строка, если событий нет.
- `total_events` — число валидных событий.
- `level` / `source` — счётчики по уровням и источникам.
- `top_CRITICAL_sources` — top-5 источников **только** `CRITICAL`.
- `top_ERROR_sources` — top-5 источников **только** `ERROR`.
- `top_ERROR|CRITICAL` — объединённый top-5; **`CRITICAL` выше `ERROR`**:
  сначала по убыванию `critical`, затем по убыванию `error`.
- `skipped_lines` — добавляется только при `--skip-invalid`.

## Структура проекта

```
lab2/
├── samples/                   # примеры входных файлов для ручной проверки
│   ├── broken.csv             
│   ├── sample.jsonl           
│   ├── sample1.csv            
│   └── sample2.csv            
├── src/
│   └── streamstats/
│       ├── __init__.py        # инициаоизация
│       ├── __main__.py        # точка входа CLI (argparse, main)
│       ├── analysis.py        # потоковый анализ событий
│       ├── errors.py          # исключения
│       ├── models.py          # валидация строки
│       ├── parsers.py         # потоковые парсеры CSV и JSONL
│       └── report.py          # формирование и запись JSON-отчёта
├── tests/
│   ├── test_csv.py            # unit-тесты CSV-парсера
│   ├── test_jsonl.py          # unit-тесты JSONL-парсера
│   └── test_cli.py            # integration-тесты CLI
├── .gitignore                 # git ignore файл
├── .pre-commit-config.yaml    # средства автоматизации проверки кодстайла
├── pyproject.toml             # зависимости проекта
├── requirements.txt           # требования             
└── README.md                  # описание проекта
```


## Тесты

Запуск всех тестов:

```bash
source .venv/bin/activate
python -m pytest -v
```

## Линтер и типы

```bash
source .venv/bin/activate

# ruff: стиль и автофикс
python -m ruff check . --fix
python -m ruff check .
python -m ruff format --check .

# mypy: проверка типов
python -m mypy src/
```

Ожидаемо: `All checks passed!` от `ruff`, `Success: no issues found` от `mypy`.

`pre-commit` (ruff + ruff-format + pytest) настраивается один раз:

```bash
pre-commit install
```

## Требования задания и соответствие

| Требование | Реализация |
|---|---|
| Чтение построчно, без `read()`/`readlines()` | `parsers.py`: `for line in file` / `enumerate(reader)` |
| CSV с заголовком | `csv.DictReader` в `parser_csv` |
| JSONL | `json.loads(line)` построчно в `parser_jsonl` |
| Валидация обязательных полей | `models.py::validate` |
| Общее число событий | `analysis.py::analyze` → `stats["total_events"]` |
| Количество по каждому уровню | `stats["level"]` |
| Количество по каждому источнику | `stats["source"]` |
| Top-5 ERROR/CRITICAL **раздельно** | `stats["top_CRITICAL_sources"]`, `stats["top_ERROR_sources"]` |
| Top-5 ERROR/CRITICAL **объединённо**, CRITICAL выше | `stats["top_ERROR\|CRITICAL"]`, сортировка `(-critical, -error)` |
| Первая/последняя метка | `min_time` / `max_time` → ISO 8601 |
| JSON-отчёт | `json.dump` / `json.dumps`, `ensure_ascii=False`, `indent=2` |
| Объединение нескольких файлов | `for path in input_files` в `analyze` |
| Strict: остановка, номер файла и строки, код 2 | `parsers.py` → `StreamStatsError` → `__main__.py` → `return 2` |
| `--skip-invalid`: WARNING в лог, счётчик | `logger.warning(...)`, `stats["skipped_lines"] += 1` |
| Исключения: базовое + отдельные | `errors.py`: `StreamStatsError`, `StreamStatsParseError`, `StreamStatsTimestampError`, `UnsupportedFileTypeError` |
| Не перехватывать `Exception` без преобразования | CLI ловит только `StreamStatsError` / `FileNotFoundError`, доменные ошибки преобразуются на границе |
| Unit-тесты парсеров | `tests/test_csv.py`, `tests/test_jsonl.py` |
| Тест пустого файла | есть |
| Тест повреждённой строки, оба режима | есть |
| Тест нескольких файлов | есть |
| Тест Unicode | есть |
| Integration CLI с `tmp_path` | `tests/test_cli.py` |


