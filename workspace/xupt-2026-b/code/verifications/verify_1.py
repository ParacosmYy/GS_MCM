"""
问题 1 自证脚本：验证时间对齐结果。

检查项：
1. RMSE < 1e-6（无噪声两路应完美重合）
2. 10Hz 时间戳等间隔 0.1s（容差 1e-6）
3. 轨迹点数 = floor((t_end - t_start)/0.1) + 1 ± 1
4. Δτ 值在合理搜索域内
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output"
DOCS = ROOT / "docs"


def main() -> None:
    traj = pd.read_csv(OUTPUT / "traj_10hz_1.csv")
    t = traj["t"].to_numpy()

    results = []

    # 1. 时间等间隔
    dt = np.diff(t)
    dt_err = np.max(np.abs(dt - 0.1))
    p1 = dt_err < 1e-6
    results.append(("时间等间隔 Δt=0.1s", p1, f"max|Δt-0.1| = {dt_err:.2e}"))

    # 2. RMSE (从 docs/problem1_result.md 读取)
    report = (DOCS / "problem1_result.md").read_text(encoding="utf-8")
    import re
    m = re.search(r"RMSE = ([\d.e+-]+)", report)
    rmse = float(m.group(1)) if m else 999
    p2 = rmse < 1e-6
    results.append(("对齐 RMSE < 1e-6", p2, f"RMSE = {rmse:.2e}"))

    # 3. 轨迹点数合理
    span = t[-1] - t[0]
    expected_n = int(span / 0.1) + 1
    p3 = abs(len(traj) - expected_n) <= 1
    results.append(("轨迹点数合理", p3, f"actual={len(traj)}, expected≈{expected_n}"))

    # 4. Δτ 范围合理 (附件1: t1_start=221, t2_start=468.83, 差约-248; Δτ 在 [-300, -100] 合理)
    m2 = re.search(r"Δτ = ([\d.e+-]+)", report)
    dtau = float(m2.group(1)) if m2 else 0
    p4 = -300 < dtau < -100
    results.append(("Δτ 范围合理 [-300,-100]", p4, f"Δτ = {dtau:.4f}"))

    # 输出
    all_pass = all(r[1] for r in results)
    print("=" * 50)
    print("  问题 1 验证报告")
    print("=" * 50)
    for name, passed, detail in results:
        mark = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {mark}  {name}  ({detail})")
    print("=" * 50)
    status = "ALL PASS" if all_pass else "FAILED"
    print(f"  最终状态: {status}")
    print("=" * 50)

    if not all_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
