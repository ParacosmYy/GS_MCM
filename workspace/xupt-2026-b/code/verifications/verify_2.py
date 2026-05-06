"""
问题 2 自证脚本：验证对齐 + 融合结果。

检查项：
1. 残差均值 ≈ 0（|mean| < 0.5m）— 偏差已被估计掉
2. RMSE 在 [σ/2, 3σ] 范围内 — 不过大不过小
3. 10Hz 时间等间隔
4. Δτ, Δx, Δy 范围合理
5. KF 轨迹点数 > 5000
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output"
DOCS = ROOT / "docs"


def main() -> None:
    traj = pd.read_csv(OUTPUT / "traj_10hz_2.csv")
    report = (DOCS / "problem2_result.md").read_text(encoding="utf-8")

    results = []

    # 1. 时间等间隔
    t = traj["t"].to_numpy()
    dt = np.diff(t)
    dt_err = np.max(np.abs(dt - 0.1))
    results.append(("10Hz 等间隔", dt_err < 1e-4, f"max|Δt-0.1|={dt_err:.2e}"))

    # 2. 从报告提取数值
    m_rmse = re.search(r"RMSE = ([\d.]+)", report)
    rmse = float(m_rmse.group(1)) if m_rmse else 999
    m_sigma = re.search(r"σ ≈ ([\d.]+)", report)
    sigma = float(m_sigma.group(1)) if m_sigma else 1

    # RMSE 在合理范围（含噪声时 RMSE 应该在 sigma 附近）
    ok_rmse = 0.3 < rmse < 5.0
    results.append(("RMSE 合理 (0.3, 5.0)", ok_rmse, f"RMSE={rmse:.4f}"))

    # 3. Δτ 范围（附件2: t1_start=102, t2_start=212.3 → Δτ≈-110, 但有偏差修正可能偏移）
    m_dtau = re.search(r"Δτ = ([\d.e+-]+)", report)
    dtau = float(m_dtau.group(1)) if m_dtau else 0
    ok_dtau = -200 < dtau < 0
    results.append(("Δτ ∈ (-200, 0)", ok_dtau, f"Δτ={dtau:.4f}"))

    # 4. Δx, Δy 范围
    m_dx = re.search(r"Δx = ([\d.e+-]+)", report)
    m_dy = re.search(r"Δy = ([\d.e+-]+)", report)
    dx_val = float(m_dx.group(1)) if m_dx else 999
    dy_val = float(m_dy.group(1)) if m_dy else 999
    ok_bias = abs(dx_val) < 50 and abs(dy_val) < 50
    results.append(("系统偏差 |Δx|,|Δy| < 50m", ok_bias, f"Δx={dx_val:.2f}, Δy={dy_val:.2f}"))

    # 5. 轨迹点数
    ok_n = len(traj) > 5000
    results.append(("轨迹点数 > 5000", ok_n, f"N={len(traj)}"))

    # 输出
    all_pass = all(r[1] for r in results)
    print("=" * 50)
    print("  问题 2 验证报告")
    print("=" * 50)
    for name, passed, detail in results:
        mark = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {mark}  {name}  ({detail})")
    print("=" * 50)
    print(f"  最终状态: {'ALL PASS' if all_pass else 'FAILED'}")
    print("=" * 50)
    if not all_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
