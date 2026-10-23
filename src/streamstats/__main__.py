import argparse
import logging
import sys
from pathlib import Path

from . import analysis, report
from .errors import StreamStatsError


def main() -> int:
    """Точка входа CLI.
    Принимает аргументы командной строки
        command: analyze
        INPUT: один или несколько путей к файлам .jsonl .csv
        --format: "jsonl" или "csv"
        --output: путь к файлу отчета
        --skip-invalid: пропускает некорректные строки с WARNING.
    Возвращает:
        0 - успешные анализ и запись отчета
        2 - доменная ошибка(StreamStatsError) или отсутствие файла(FileNotFoundError).
    """
    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s %(asctime)s %(message)s",
        filename="WARNING.log",
        encoding="utf-8",
    )
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=["analyze"],
        type=str,
    )
    parser.add_argument(
        "INPUT",
        type=str,
        nargs="+",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["jsonl", "csv"],
        required=True,
    )
    parser.add_argument(
        "--output",
        type=str,
        default="-",
    )
    parser.add_argument(
        "--skip-invalid",
        action="store_true",
    )
    args = parser.parse_args()
    try:
        path_output = Path(args.output).resolve()
        for input_file in args.INPUT:
            if path_output == Path(input_file).resolve():
                raise StreamStatsError(f"{input_file} уже содержит данные.")
        stats, error_critical = analysis.analyze(args.INPUT, args.format, args.skip_invalid)
        report.write_report(stats, error_critical, args.output)
    except StreamStatsError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    except FileNotFoundError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
