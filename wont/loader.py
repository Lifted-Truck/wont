"""loader.py — labeled runs on disk.

A run is one JSON file (`<run_id>.labeled-run.json` by convention, but any
name loads). A corpus is a directory of them. Loading VALIDATES — an invalid
file never enters a corpus silently; a corpus load reports every bad file
with its total error list rather than stopping at the first.

Stdlib only.
"""

from __future__ import annotations

import json
from pathlib import Path

from .schema import LabeledRun, ValidationError

RUN_SUFFIX = ".labeled-run.json"


def save_run(run: LabeledRun, directory: str | Path) -> Path:
    """Validate and write a run to `<directory>/<run_id>.labeled-run.json`."""
    run.validate()
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    run_id = run.run_id if run.run_id is not None else run.computed_run_id()
    path = directory / f"{run_id}{RUN_SUFFIX}"
    path.write_text(run.to_json() + "\n", encoding="utf-8")
    return path


def load_run(path: str | Path) -> LabeledRun:
    """Load and validate a single labeled run."""
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValidationError([f"{path}: not valid JSON ({e})"]) from e
    run = LabeledRun.from_dict(data)
    try:
        run.validate()
    except ValidationError as e:
        raise ValidationError([f"{path}: {msg}" for msg in e.errors]) from e
    return run


def load_corpus(directory: str | Path) -> list[LabeledRun]:
    """Load every `*.labeled-run.json` under a directory (sorted, recursive).

    Total-validation at corpus scale: all files are attempted; if any fail,
    one ValidationError carries every file's every error.
    """
    directory = Path(directory)
    if not directory.is_dir():
        raise ValidationError([f"{directory}: not a directory"])
    paths = sorted(directory.rglob(f"*{RUN_SUFFIX}"))
    runs: list[LabeledRun] = []
    errors: list[str] = []
    for path in paths:
        try:
            runs.append(load_run(path))
        except ValidationError as e:
            errors.extend(e.errors)
    if errors:
        raise ValidationError(errors)
    return runs
