"""Формирование и запись json-отчёта."""

import json


def top(counts: dict[str, int]) -> list[dict]:
    """Возвращает top-N источников: [{"sources": ..., "count": ...}]."""
    sorted_items = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [{"sources": source, "count": cnt} for source, cnt in sorted_items[:5]]


def top_combined(error_counts: dict[str, int], critical_counts: dict[str, int], ) -> list[dict]:
    """Top-N с приоритетом CRITICAL.
    Для каждого источника:
        critical = critical_counts.get(source, 0)
        error = error_counts.get(source, 0)
    Сортировка: сначала по critical (убывание), затем по error (убывание)
    """
    sources = set(error_counts) | set(critical_counts)
    rows = [
        {
            "sources": source,
            "critical": critical_counts.get(source, 0),
            "error": error_counts.get(source, 0),
        }
        for source in sources
    ]
    rows.sort(key=lambda r: (-r["critical"], -r["error"]))
    return rows[:5]


def write_report(data: dict, error_counts: dict, critical_counts: dict, output_file: str) -> None:
    """Дополняет отчёт top-5 источников и записывает JSON.
    Принимает:
        data: общая статистика (min/max_timestamp, total_events, level, source, при skip_invalid — skipped_lines).
        error_counts: dict[str, int] — источники уровня ERROR.
        critical_counts: dict[str, int] — источники уровня CRITICAL.
        output_file: "-" для stdout или путь к файлу.
    Возвращает:
        None.
    """
    data["top_CRITICAL_sources"] = top(critical_counts)
    data["top_ERROR_sources"] = top(error_counts)
    data["top_ERROR|CRITICAL"] = top_combined(error_counts, critical_counts)
    if output_file == "-":
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)