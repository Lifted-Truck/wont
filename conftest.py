"""Test path setup. Loaded by pytest before any test module, so the Wend import
inside wont/clients/wend.py resolves during collection.

Puts the repo root (for `import wont` / `import harness`) and the synthetic-worlds
parent (for `import Wend`, the in-process client transport, D16) on sys.path.
Run the suite on the Tonality venv, which carries both mts and importable Wend
(see CLAUDE.md Conventions / LIBRARY L0001).
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))      # .../wont (repo root)
PARENT = os.path.dirname(HERE)                          # .../synthetic-worlds
for _p in (HERE, PARENT):
    if _p not in sys.path:
        sys.path.insert(0, _p)
