"""
2026 XUPT Campus MCM - Main solver entry point.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "figures"
FIG_DIR.mkdir(exist_ok=True)


def load_data(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / name)


def main() -> None:
    print("XUPT MCM 2026 - solver skeleton ready")


if __name__ == "__main__":
    main()
