"""Валидация строк."""

from datetime import datetime

from .errors import StreamStatsParseError, StreamStatsTimestampError

LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def validate(line: dict, file: str, line_number: int) -> None:
    """Проверяет обязательные поля.
    Принимает:
        line: распарсенная строка
        file: путь к файлу
        line_number: номер строки.
    Возвращает:
        None - если строка валидна.
    Исключения:
        StreamStatsParseError - если поле отсутствует, неверного типа, уровень не из LEVELS или source пустой.
        StreamStatsTimestampError - если timestamp не ISO 8601.
    """
    if not isinstance(line, dict):
        raise StreamStatsParseError(f"file {file} line {line_number}: line must be a dict.")
    if line.get("timestamp") is None:
        raise StreamStatsParseError(f"file {file} line {line_number}: timestamp field is required.")
    if line.get("level") is None:
        raise StreamStatsParseError(f"file {file} line {line_number}: level field is required.")
    if line.get("source") is None:
        raise StreamStatsParseError(f"file {file} line {line_number}: source field is required.")
    timestamp, level, source = line["timestamp"], line["level"], line["source"]
    if level not in LEVELS:
        raise StreamStatsParseError(f"file {file} line {line_number}: level must be in {LEVELS}.")
    if source.strip() == "":
        raise StreamStatsParseError(f"file {file} line {line_number}: source cannot be empty.")
    try:
        datetime.fromisoformat(timestamp)
    except ValueError:
        raise StreamStatsTimestampError(f"file {file} line {line_number}: timestamp must be ISO 8601.")
