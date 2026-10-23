import json

import pytest

from streamstats import parsers
from streamstats.errors import StreamStatsError


def test_jsonl_parser(tmp_path):
    expected = [
        {
            "timestamp": "2021-11-15T07:42:09",
            "level": "WARNING",
            "source": "yandex",
            "message": "",
        },
        {
            "timestamp": "2024-06-02T23:18:44",
            "level": "ERROR",
            "source": "yandex",
            "message": "",
        },
    ]
    path = tmp_path / "valid.jsonl"

    with path.open("w", encoding="utf-8") as file:
        for line in expected:
            json.dump(line, file, ensure_ascii=False)
            file.write("\n")

    with path.open(encoding="utf-8") as file:
        result = list(parsers.parser_jsonl({"skipped_lines": 0}, file))

    assert result == expected


def test_invalid_jsonl_parser(tmp_path):
    path = tmp_path / "invalid.jsonl"

    expected = {
        "timestamp": "2023-02-08T16:05:31",
        "level": "CRITICAL",
        "source": "",
        "message": "",
    }

    with path.open("w", encoding="utf-8") as file:
        json.dump(expected, file, ensure_ascii=False)
        file.write("\n")

    stats = {"skipped_lines": 0}

    with path.open(encoding="utf-8") as file, pytest.raises(StreamStatsError):
        list(parsers.parser_jsonl(stats, file))

    with path.open(encoding="utf-8") as file:
        list(parsers.parser_jsonl(stats, file, skip_invalid=True))
        assert stats["skipped_lines"] == 1


def test_empty_file_jsonl_parser(tmp_path):
    path = tmp_path / "empty.jsonl"

    path.touch()

    with path.open(encoding="utf-8") as file:
        result = list(parsers.parser_jsonl({"skipped_lines": 0}, file))
        assert result == []


def test_parser_jsonl_unicode(tmp_path):
    expected = {
        "timestamp": "2024-01-01T00:00:00Z",
        "level": "ERROR",
        "source": "сервер",
        "message": "💅",
    }
    stats = {"skipped_lines": 0}
    path = tmp_path / "unicode.jsonl"

    with path.open("w", encoding="utf-8") as file:
        json.dump(expected, file, ensure_ascii=False)
        file.write("\n")

    with path.open(encoding="utf-8") as file:
        result = list(parsers.parser_jsonl(stats, file))

    assert result == [expected]
    assert stats["skipped_lines"] == 0