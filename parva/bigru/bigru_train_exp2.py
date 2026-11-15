"""Experiment 2. Run from the repository root:  python parva/bigru/bigru_train_exp2.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bigru_train_common import run  # noqa: E402

if __name__ == "__main__":
    run("exp2")
