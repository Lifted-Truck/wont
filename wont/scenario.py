"""scenario.py — a named training context (schema FINAL as of the harness build).

> Introduced by Julian, 2026-07-08 (DECISIONS.md D14). The scaffold left this a
> DRAFT for the build-agent to revise as the GUI/generator took form; the
> audition harness (D13) exercised every field end-to-end — seed_rulesets ->
> WendClient, parameter_space -> the sweep, capture -> the time-shift, client /
> engine_pins / fingerprint -> the saved LabeledRun's provenance — and the shape
> held with no changes. So it is now frozen at `wont.scenario.1` (D17). Future
> needs bump the version (e.g. `.2`); the fingerprint excludes schema_version,
> so freezing does not disturb runs already tagged with a scenario fingerprint.

A **scenario** is a bounded preference-training context: "teach wont what I like
*for lo-fi lounge*", starting from predefined Tonality/Wend rulesets and
refining to taste. Its purpose is REUSE — every labeled run captured under a
scenario is tagged with the scenario id, so the feedback (and the bias artifact
learned from it) can be recalled by Wend and other tools *for that context*
without bleeding into unrelated ones. A listener's lounge taste and their
math-rock taste are different corpora; the scenario is what keeps them apart.

How it wires the pieces:
  seed_rulesets   the Tonality/Wend rulesets a session STARTS from (predefined)
  parameter_space what the generator sweeps around them (generate.py)
  capture         the dial config for this scenario (bipolar range, lag)
  feedback_dir    where this scenario's LabeledRuns accumulate (scoped store)
  -> the learner trains a scenario-scoped BiasArtifact, tagged scenario_id, that
     Wend applies deterministically when generating for that context.

Deliberately NOT here: the learned weights (a bias artifact, not scenario
config), any satisfaction data (lives in the per-run LabeledRuns), engine
analysis (derived downstream). Stdlib only, total validation (schema.py style).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

SCHEMA_VERSION = "wont.scenario.1"  # FINAL (D17) — frozen; changes bump the version


class ScenarioError(ValueError):
    def __init__(self, errors: list[str]):
        self.errors = list(errors)
        super().__init__(
            "invalid Scenario (%d error%s):\n  - %s"
            % (len(errors), "" if len(errors) == 1 else "s", "\n  - ".join(errors))
        )


def _canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


@dataclass
class Scenario:
    scenario_id: str                       # stable kebab slug — the reuse handle
    description: str = ""
    target: str = ""                       # free-form genre/style, "" = general
    client: dict = field(default_factory=lambda: {"name": "wend", "version": "0"})
    engine_pins: dict = field(default_factory=lambda: {"key_profile": "kk-1982.1"})
    # references to predefined starter rulesets (Tonality/Wend DSL). A ref is a
    # path or a named id the client resolves; inline DSL JSON is also allowed.
    seed_rulesets: list = field(default_factory=list)
    # the sweep the generator explores around the seeds (generate.ParameterSpace
    # .to_dict()); opaque here, validated by generate.py.
    parameter_space: dict = field(default_factory=dict)
    # dial config for captures in this scenario (defaults = D8 bipolar + lag 2).
    capture: dict = field(default_factory=lambda: {
        "value_min": -1.0, "value_max": 1.0, "lag_bars": 2})
    # where this scenario's labeled runs accumulate (relative to the scenario
    # file, by convention scenarios/<id>/runs/).
    feedback_dir: str = ""
    notes: list = field(default_factory=list)

    def fingerprint(self) -> str:
        """Content hash of the definition (provenance for artifacts trained
        under it). Excludes accumulated feedback — the scenario is the recipe,
        not the data."""
        return hashlib.sha256(_canonical_json({
            "scenario_id": self.scenario_id,
            "target": self.target,
            "client": self.client,
            "engine_pins": self.engine_pins,
            "seed_rulesets": self.seed_rulesets,
            "parameter_space": self.parameter_space,
        }).encode("utf-8")).hexdigest()

    def validate(self) -> list[str]:
        errs: list[str] = []
        if not isinstance(self.scenario_id, str) or not self.scenario_id.strip():
            errs.append("scenario_id must be a non-empty string")
        elif self.scenario_id != self.scenario_id.strip().lower().replace(" ", "-"):
            errs.append(f"scenario_id should be a kebab slug, got {self.scenario_id!r}")
        if not isinstance(self.client, dict) or "name" not in self.client:
            errs.append("client must be a dict with at least a 'name'")
        if not isinstance(self.seed_rulesets, list):
            errs.append("seed_rulesets must be a list")
        if not isinstance(self.parameter_space, dict):
            errs.append("parameter_space must be a dict")
        cap = self.capture
        if not isinstance(cap, dict):
            errs.append("capture must be a dict")
        else:
            if cap.get("value_min", -1.0) >= cap.get("value_max", 1.0):
                errs.append("capture.value_min must be < capture.value_max")
            if not isinstance(cap.get("lag_bars", 2), int) or cap.get("lag_bars", 2) < 0:
                errs.append("capture.lag_bars must be a non-negative int")
        return errs

    def validated(self) -> "Scenario":
        errs = self.validate()
        if errs:
            raise ScenarioError(errs)
        return self

    def to_dict(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "scenario_id": self.scenario_id,
            "fingerprint": self.fingerprint(),
            "description": self.description,
            "target": self.target,
            "client": self.client,
            "engine_pins": self.engine_pins,
            "seed_rulesets": self.seed_rulesets,
            "parameter_space": self.parameter_space,
            "capture": self.capture,
            "feedback_dir": self.feedback_dir,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Scenario":
        return cls(
            scenario_id=d["scenario_id"],
            description=d.get("description", ""),
            target=d.get("target", ""),
            client=d.get("client", {"name": "wend", "version": "0"}),
            engine_pins=d.get("engine_pins", {"key_profile": "kk-1982.1"}),
            seed_rulesets=d.get("seed_rulesets", []),
            parameter_space=d.get("parameter_space", {}),
            capture=d.get("capture", {"value_min": -1.0, "value_max": 1.0, "lag_bars": 2}),
            feedback_dir=d.get("feedback_dir", ""),
            notes=d.get("notes", []),
        )
