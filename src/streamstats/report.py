"""Формарование и запись json-отчета."""
import json


def write_report(data: dict, error_critical: dict, output_file) -> None:
    sorted_data = sorted(error_critical.items(), key=lambda item: (-item[1], item[0]))
    top = sorted_data[:5]
    top_list = []
    for sources, cnt in top:
        top_list.append({"sources": sources, "count": cnt})
    data["ERROR|CRITICAL"] = top_list
    if output_file == "-":
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)