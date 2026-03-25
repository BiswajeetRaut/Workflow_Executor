#!/usr/bin/env python3
"""Lightweight pre-merge sanity checks for local conflict recovery.

Checks:
1) No unresolved merge markers in backend/ or workflow_ui/src/.
2) Python syntax compilation for backend/*.py files.
"""

from __future__ import annotations

import pathlib
import py_compile
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCAN_DIRS = [ROOT / "backend", ROOT / "workflow_ui" / "src"]
MARKERS = ("<<<<<<<", "=======", ">>>>>>>")


def find_merge_markers() -> list[str]:
    hits: list[str] = []
    for scan_dir in SCAN_DIRS:
        for path in scan_dir.rglob("*"):
            if not path.is_file():
                continue
            if "node_modules" in path.parts:
                continue
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except UnicodeDecodeError:
                continue
            for line_no, line in enumerate(lines, start=1):
                if line.startswith(MARKERS):
                    hits.append(f"{path.relative_to(ROOT)}:{line_no}:{line}")
    return hits


def compile_backend() -> list[str]:
    errors: list[str] = []
    for path in (ROOT / "backend").rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:  # pragma: no cover - cli utility
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
    return errors


def main() -> int:
    marker_hits = find_merge_markers()
    compile_errors = compile_backend()

    if marker_hits:
        print("❌ Unresolved merge markers found:")
        for hit in marker_hits:
            print(f"  - {hit}")
    else:
        print("✅ No unresolved merge markers found in backend/ and workflow_ui/src/")

    if compile_errors:
        print("❌ Python compilation errors found:")
        for err in compile_errors:
            print(f"  - {err}")
    else:
        print("✅ Backend Python files compile successfully")

    if marker_hits or compile_errors:
        return 1

    print("\nAll pre-merge sanity checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
