#!/usr/bin/env python3
"""Generate release notes from CHANGELOG and metrics."""

import json
import pathlib
import re
import sys
from textwrap import dedent


def build_notes(version: str) -> str:
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    changelog = (repo_root / "CHANGELOG.md").read_text()
    pattern = r"## \[" + re.escape(version) + r"\](.*?)(?:\n## |\Z)"
    match = re.search(pattern, changelog, re.S)
    section = match.group(0).strip() if match else f"## [{version}]"

    metrics_path = repo_root / f"models/metrics_{version}.json"
    metrics = json.loads(metrics_path.read_text())
    metrics_json = json.dumps(metrics, indent=2)

    return dedent(
        f"""{section}

        ## Metrics
        ```json
        {metrics_json}
        ```
        """
    ).strip()


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: generate_release_notes.py <version>")
    version = sys.argv[1]
    notes = build_notes(version)
    pathlib.Path("release_notes.md").write_text(notes)


if __name__ == "__main__":
    main()
