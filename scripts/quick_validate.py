#!/usr/bin/env python3
from __future__ import annotations

import py_compile
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def check_file(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"Missing required file: {path}")


def main() -> int:
    required = [
        ROOT / "skills/aihot-crossborder-intel/SKILL.md",
        ROOT / "skills/hex2077-intelligence-bridge/SKILL.md",
        ROOT / "skills/amazon-official-news-bridge/SKILL.md",
        ROOT / "aihot-feishu-daily/scripts/generate_report.py",
        ROOT / "aihot-feishu-daily/scripts/run_daily.sh",
        ROOT / "aihot-feishu-daily/sources.example.json",
        ROOT / "install.sh",
    ]
    for path in required:
        check_file(path)

    python_files = [
        ROOT / "skills/aihot-crossborder-intel/scripts/fetch_aihot_items.py",
        ROOT / "skills/hex2077-intelligence-bridge/scripts/fetch_latest_hex2077.py",
        ROOT / "skills/amazon-official-news-bridge/scripts/fetch_amazon_official_news.py",
        ROOT / "aihot-feishu-daily/scripts/generate_report.py",
    ]
    python_files.extend((ROOT / "aihot-feishu-daily/scripts/intel_pipeline").rglob("*.py"))
    for path in python_files:
        py_compile.compile(str(path), doraise=True)

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "aihot-feishu-daily/scripts/generate_report.py"),
            "--source-config",
            str(ROOT / "aihot-feishu-daily/sources.example.json"),
            "--list-sources",
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr or result.stdout)

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "skills/hex2077-intelligence-bridge/scripts/fetch_latest_hex2077.py"),
            "daily",
            "--items-json",
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr or result.stdout)

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "skills/amazon-official-news-bridge/scripts/fetch_amazon_official_news.py"),
            "--take",
            "3",
            "--items-json",
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr or result.stdout)

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
