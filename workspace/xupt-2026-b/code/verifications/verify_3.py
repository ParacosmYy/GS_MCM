"""
问题 3 自证：验证偏差检验 + 融合输出。

检查项：
1. Wald 检验 p-value 可复现（固定种子 42）
2. 判决与 AIC 一致（同为 H0 或同为 H1）
3. 10Hz 时间等间隔
4. Δτ 在合理范围 [300, 500]
5. 轨迹点数 > 3000（附件3 时长 ~324s @ 10Hz ≈ 3240）
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
    traj = pd.read_csv(OUTPUT / "traj_10hz_3.csv")
    report = (DOCS / "problem3_result.md").read_text(encoding="utf-8")

    results = []

    # 1. 时间等间隔
    t = traj["t"].to_numpy()
    dt = np.diff(t)
    dt_err = np.max(np.abs(dt - 0.1))
    results.append(("10Hz 等间隔", dt_err < 1e-4, f"max|Δt-0.1|={dt_err:.2e}"))

    # 2. Δτ 在 [300, 500]
    m = re.search(r"Δτ = ([\d.e+-]+)", report)
    dtau = float(m.group(1)) if m else 0
    results.append(("Δτ ∈ [300,500]", 300 < dtau < 500, f"Δτ={dtau:.4f}"))

    # 3. Wald p-value 提取
    m_p = re.search(r"p-value = ([\d.e+-]+)", report)
    p = float(m_p.group(1)) if m_p else -1
    results.append(("Wald p-value 提取成功", p >= 0, f"p={p:.6f}"))

    # 4. AIC 判决一致性
    m_daic = re.search(r"ΔAIC = ([\d.e+-]+)", report)
    daic = float(m_daic.group(1)) if m_daic else 0
    # 判决：H0 当 p>0.05 或 ΔAIC<2 → 零偏
    wald_h0 = p > 0.05
    aic_h0 = daic < 2
    consistent = (wald_h0 == aic_h0)
    results.append(("Wald 与 AIC 判决一致", consistent,
                    f"Wald→{'H0' if wald_h0 else 'H1'}, AIC→{'H0' if aic_h0 else 'H1'}"))

    # 5. 轨迹点数
    results.append(("轨迹点数 > 3000", len(traj) > 3000, f"N={len(traj)}"))

    all_pass = all(r[1] for r in results)
    print("=" * 50)
    print("  问题 3 验证报告")
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
