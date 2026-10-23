"""Потоковые парсеры csv и jsonl."""

import csv
import json
import logging
from collections.abc import Generator
from json import JSONDecodeError

from .errors import StreamStatsError
from .models import validate

logger = logging.getLogger(__name__)

def parser_jsonl(stats: dict, file, skip_invalid: bool = False) -> Generator[dict, None, None]:
    """Отдает валидные события jsonl-файла."""
    for line_number, line in enumerate(file, start=1):
        try:
            data = json.loads(line)
            validate(data, file, line_number)
        except StreamStatsError as error:
            if skip_invalid:
                logger.warning("Skipping invalid line %s: %s. %s.", line_number, line, error)
                stats["skipped_lines"] += 1
                continue
            else:
                raise StreamStatsError(f"Invalid JSON line {line_number}: {line}")
        except JSONDecodeError as error:
            if skip_invalid:
                logger.warning("Skipping invalid line %s: %s. %s.", line_number, line, error)
                stats["skipped_lines"] += 1
                continue
            else:
                raise StreamStatsError(f"Invalid JSON line {line_number}: {line}")
        yield data


def parser_csv(stats: dict, file, skip_invalid: bool = False) -> Generator[dict, None, None]:
    """Отдает валидные события csv-файла."""
    reader = csv.DictReader(file)
    for line_number, line in enumerate(reader, start=2):
        try:
            validate(line, file, line_number)
        except StreamStatsError as error:
            if skip_invalid:
                logger.warning("Skipping invalid line %s: %s. %s.", line_number, line, error)
                stats["skipped_lines"] += 1
                continue
            else:
                raise StreamStatsError(f"Invalid CSV line {line_number}: {line}")
        yield line

