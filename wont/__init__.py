"""wont — the satisfaction-loop learner (provisional name; design-dialogue phase).

Only the labeled-run schema + loader exist. See DESIGN.md before adding code.
"""

from .schema import (  # noqa: F401
    SCHEMA_VERSION,
    LabeledRun,
    SatisfactionCurve,
    ValidationError,
    compute_run_id,
)
from .loader import load_run, save_run, load_corpus  # noqa: F401
