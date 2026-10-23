"""Integration-тесты CLI: JSONL и CSV через subprocess."""

import csv
import json
import subprocess
import sys

data_one = [
    {"timestamp": "2023-03-14T09:12:45", "level": "WARNING", "source": "auth", "message": ""},
    {"timestamp": "2022-08-01T18:05:30", "level": "CRITICAL", "source": "billing", "message": ""},
    {"timestamp": "2021-12-25T03:47:11", "level": "ERROR", "source": "auth", "message": ""},
    {"timestamp": "2023-06-18T22:30:02", "level": "INFO", "source": "web", "message": ""},
]

data_two = [
    {"timestamp": "2022-02-11T07:21:54", "level": "DEBUG", "source": "cache", "message": ""},
    {"timestamp": "2023-09-30T14:08:17", "level": "CRITICAL", "source": "db", "message": ""},
    {"timestamp": "2021-05-07T11:44:08", "level": "ERROR", "source": "cache", "message": ""},
    {"timestamp": "2024-01-19T19:59:33", "level": "WARNING", "source": "web", "message": ""},
]

data_three = [
    {"timestamp": "2024-04-22T12:15:00", "level": "INFO", "source": "db", "message": ""},
    {"timestamp": "2023-11-03T05:36:41", "level": "ERROR", "source": "queue", "message": ""},
    {"timestamp": "2022-07-14T16:22:19", "level": "CRITICAL", "source": "queue", "message": ""},
    {"timestamp": "2021-09-08T23:11:57", "level": "DEBUG", "source": "auth", "message": ""},
]

data_four = [
    {"timestamp": "2020-10-31T13:50:12", "level": "ERROR", "source": "storage", "message": ""},
    {"timestamp": "2024-06-05T08:14:27", "level": "INFO", "source": "storage", "message": ""},
    {"timestamp": "2022-12-19T21:03:45", "level": "WARNING", "source": "api", "message": ""},
    {"timestamp": "2023-08-08T17:26:38", "level": "CRITICAL", "source": "api", "message": ""},
]

data_five = [
    {"timestamp": "2021-03-27T06:42:09", "level": "DEBUG", "source": "worker", "message": ""},
    {"timestamp": "2024-09-14T10:55:21", "level": "ERROR", "source": "worker", "message": ""},
    {"timestamp": "2020-12-02T15:37:54", "level": "INFO", "source": "scheduler", "message": ""},
    {"timestamp": "2025-01-25T04:18:03", "level": "ERROR", "source": "scheduler", "message": ""},
]

expected = {
    "min_timestamp": "2020-10-31T13:50:12+00:00",
    "max_timestamp": "2025-01-25T04:18:03+00:00",
    "total_events": 20,
    "level": {
        "WARNING": 3,
        "CRITICAL": 4,
        "ERROR": 6,
        "INFO": 4,
        "DEBUG": 3,
    },
    "source": {
        "auth": 3,
        "billing": 1,
        "web": 2,
        "cache": 2,
        "db": 2,
        "queue": 2,
        "storage": 2,
        "api": 2,
        "worker": 2,
        "scheduler": 2,
    },
    "ERROR|CRITICAL": [
        {"sources": "queue", "count": 2},
        {"sources": "api", "count": 1},
        {"sources": "auth", "count": 1},
        {"sources": "billing", "count": 1},
        {"sources": "cache", "count": 1},
    ],
}


def test_cli_jsonl(tmp_path) -> None:
    files = []
    for i, data in enumerate(
        [data_one, data_two, data_three, data_four, data_five], start=1,
    ):
        path = tmp_path / f"file_{i}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for line in data:
                json.dump(line, f, ensure_ascii=False)
                f.write("\n")
        files.append(path)

    result = subprocess.run(
        [
            sys.executable, "-m", "streamstats", "analyze", "--format", "jsonl",
            *[str(p) for p in files],
        ],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report == expected


def test_cli_csv(tmp_path):
    files = []
    for i, data in enumerate(
        [data_one, data_two, data_three, data_four, data_five], start=1,
    ):
        path = tmp_path / f"file_{i}.csv"
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["timestamp", "level", "source", "message"],
            )
            writer.writeheader()
            for line in data:
                writer.writerow(line)
        files.append(path)

    result = subprocess.run(
        [
            sys.executable, "-m", "streamstats", "analyze", "--format", "csv",
            *[str(p) for p in files],
        ],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report == expected