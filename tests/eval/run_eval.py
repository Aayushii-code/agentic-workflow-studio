#!/usr/bin/env python
"""Runnable independently of pytest:

    python tests/eval/run_eval.py
    python tests/eval/run_eval.py --cases-dir tests/eval/cases

Exits with status 1 if any golden case fails (so it can gate CI on its own,
separately from `pytest tests/`).
"""

import argparse
import asyncio
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))
sys.path.insert(0, str(REPO_ROOT))

import app.executors.bootstrap  # noqa: E402  populate EXECUTOR_REGISTRY
from tests.eval.harness import run_suite  # noqa: E402


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cases-dir",
        type=Path,
        default=Path(__file__).parent / "cases",
        help="Directory of golden-case JSON files (default: tests/eval/cases)",
    )
    args = parser.parse_args()

    results = await run_suite(args.cases_dir)

    passed = [r for r in results if r.passed]
    failed = [r for r in results if not r.passed]

    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.case_id} -- {result.detail}")

    print(f"\n{len(passed)}/{len(results)} cases passed.")
    if failed:
        print(f"{len(failed)} case(s) failed: {', '.join(r.case_id for r in failed)}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
