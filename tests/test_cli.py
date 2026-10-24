"""Integration-тесты CLI: JSONL и CSV через subprocess."""

import csv
import json
import subprocess
import sys

data_one = [
    {"timestamp": "2023-03-14T09:12:45", "level": "CRITICAL", "source": "billing", "message": ""},
    {"timestamp": "2022-08-01T18:05:30", "level": "CRITICAL", "source": "billing", "message": ""},
    {"timestamp": "2021-12-25T03:47:11", "level": "ERROR",    "source": "auth",    "message": ""},
    {"timestamp": "2023-06-18T22:30:02", "level": "INFO",     "source": "web",     "message": ""},
]

data_two = [
    {"timestamp": "2022-02-11T07:21:54", "level": "CRITICAL", "source": "billing", "message": ""},
    {"timestamp": "2023-09-30T14:08:17", "level": "CRITICAL", "source": "queue",   "message": ""},
    {"timestamp": "2021-05-07T11:44:08", "level": "ERROR",    "source": "queue",   "message": ""},
    {"timestamp": "2024-01-19T19:59:33", "level": "ERROR",    "source": "auth",    "message": ""},
]

data_three = [
    {"timestamp": "2024-04-22T12:15:00", "level": "ERROR",    "source": "queue",   "message": ""},
    {"timestamp": "2023-11-03T05:36:41", "level": "ERROR",    "source": "auth",    "message": ""},
    {"timestamp": "2022-07-14T16:22:19", "level": "CRITICAL", "source": "api",     "message": ""},
    {"timestamp": "2021-09-08T23:11:57", "level": "ERROR",    "source": "storage", "message": ""},
]

data_four = [
    {"timestamp": "2020-10-31T13:50:12", "level": "ERROR",    "source": "storage", "message": ""},
    {"timestamp": "2024-06-05T08:14:27", "level": "ERROR",    "source": "storage", "message": ""},
    {"timestamp": "2022-12-19T21:03:45", "level": "WARNING",  "source": "api",     "message": ""},
    {"timestamp": "2023-08-08T17:26:38", "level": "CRITICAL", "source": "api",     "message": ""},
]

data_five = [
    {"timestamp": "2021-03-27T06:42:09", "level": "ERROR",    "source": "storage",  "message": ""},
    {"timestamp": "2024-09-14T10:55:21", "level": "ERROR",    "source": "worker",   "message": ""},
    {"timestamp": "2020-12-02T15:37:54", "level": "INFO",     "source": "scheduler","message": ""},
    {"timestamp": "2025-01-25T04:18:03", "level": "WARNING",  "source": "scheduler","message": ""},
]

expected = {
    "min_timestamp": "2020-10-31T13:50:12+00:00",
    "max_timestamp": "2025-01-25T04:18:03+00:00",
    "total_events": 20,
    "level": {
        "INFO": 2,
        "WARNING": 2,
        "ERROR": 10,
        "CRITICAL": 6,
    },
    "source": {
        "billing": 3,
        "auth": 3,
        "web": 1,
        "queue": 3,
        "api": 3,
        "storage": 4,
        "worker": 1,
        "scheduler": 2,
    },
    "top_CRITICAL_sources": [
        {"sources": "billing", "count": 3},
        {"sources": "api", "count": 2},
        {"sources": "queue", "count": 1},
    ],
    "top_ERROR_sources": [
        {"sources": "storage", "count": 4},
        {"sources": "auth", "count": 3},
        {"sources": "queue", "count": 2},
        {"sources": "worker", "count": 1},
    ],
    "top_ERROR|CRITICAL": [
        {"sources": "billing", "critical": 3, "error": 0},
        {"sources": "api", "critical": 2, "error": 0},
        {"sources": "queue", "critical": 1, "error": 2},
        {"sources": "storage", "critical": 0, "error": 4},
        {"sources": "auth", "critical": 0, "error": 3},
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
    for i, data in enumerate([data_one, data_two, data_three, data_four, data_five], start=1):
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