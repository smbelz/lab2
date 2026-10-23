"""Модуль потокового анализа событий."""

from datetime import UTC, datetime

from .errors import UnsupportedFileTypeError
from .parsers import parser_csv, parser_jsonl


def analyze(input_files: list[str], input_format: str, skip_invalid: bool = False) -> tuple[dict, dict]:
    """Считает статистику по событиям.
    Принимает:
        input_files: список путей к файлам
        input_format: "jsonl" или "csv"
        skip_invalid: при True - пропускает некорректные строки.
    Возвращает:
        (stats, error_critical)
        stats - счетчики:
            min_timestamp: str - первая временная метка
            max_timestamp: str - последняя временная метка
            total_events: int - общее число событий
            level: dict[str, int] - счетчик по уровням
            source: dict[str, str] - счетчик по источникам
            skipped_lines: int - при skip_invalid
        error_critical - источники ERROR/CRITICAL и их количество
    """
    min_time: datetime | None = None
    max_time: datetime | None = None
    stats: dict = {
        "min_timestamp": "",
        "max_timestamp": "",
        "total_events": 0,
        "level": {},
        "source": {},
    }
    error_critical: dict[str, int] = {}
    if skip_invalid:
        stats["skipped_lines"] = 0
    for path in input_files:
        if not path.endswith(".csv") and not path.endswith(".jsonl"):
            raise UnsupportedFileTypeError(f"File {path} does not end with .csv or .jsonl.")
        if path.endswith(".csv") and input_format == "jsonl":
            raise UnsupportedFileTypeError(f"File {path} cannot be opened with jsonl parser.")
        if path.endswith(".jsonl") and input_format == "csv":
            raise UnsupportedFileTypeError(f"File {path} cannot be opened with csv parser.")
        with open(path, "r", encoding="utf-8", newline="") as file:
            if input_format == "jsonl":
                events = parser_jsonl(stats, file, skip_invalid)
            else:
                events = parser_csv(stats, file, skip_invalid)
            for event in events:
                level = event["level"]
                source = event["source"]
                if level not in stats["level"]:
                    stats["level"][level] = 1
                else:
                    stats["level"][level] += 1
                stats["total_events"] += 1
                if level in ("ERROR", "CRITICAL"):
                    if source not in error_critical:
                        error_critical[source] = 1
                    else:
                        error_critical[source] += 1
                if source not in stats["source"]:
                    stats["source"][source] = 1
                else:
                    stats["source"][source] += 1
                time = datetime.fromisoformat(event["timestamp"])
                if time.tzinfo is None:
                    time = time.replace(tzinfo=UTC)
                if min_time is None or time < min_time:
                    min_time = time
                if max_time is None or time > max_time:
                    max_time = time
    if max_time is not None:
        stats["max_timestamp"] = max_time.isoformat()
    else:
        stats["max_timestamp"] = ""
    if min_time is not None:
        stats["min_timestamp"] = min_time.isoformat()
    else:
        stats["min_timestamp"] = ""
    return stats, error_critical