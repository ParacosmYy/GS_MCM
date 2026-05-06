"""
估计问题 4 的 MILP/CP-SAT 变量规模，输出报告到 docs/milp_scale.md。

变量构成（以 10Hz 融合轨迹为基础）:
  N_s 射击目标 x N_t 决策时刻         (射击决策变量)
  N_p 拍照目标 x M 方位角 x N_t       (拍照决策变量)

扫多档决策网格（1Hz / 2Hz / 5Hz / 10Hz）+ 多档最小角差 (30°/45°/60°/90°)。
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
DOCS = ROOT / "docs"
DOCS.mkdir(exist_ok=True)


def main() -> None:
    a3_1 = pd.read_excel(DATA / "附件3.xlsx", sheet_name="方式1(4Hz)")
    a3_2 = pd.read_excel(DATA / "附件3.xlsx", sheet_name="方式2(5Hz)")
    # 融合后 10Hz 轨迹的时间跨度 = 两路时间并集 —— 估计保守上界
    t_start = max(a3_1.iloc[0, 0], a3_2.iloc[0, 0])
    t_end = min(a3_1.iloc[-1, 0], a3_2.iloc[-1, 0])
    # 公共时段（若非空），否则取两路分别时长的平均
    if t_end > t_start:
        span = t_end - t_start
    else:
        span = min(a3_1.iloc[-1, 0] - a3_1.iloc[0, 0],
                   a3_2.iloc[-1, 0] - a3_2.iloc[0, 0])

    N_s, N_p = 18, 18

    lines = ["# 问题 4 变量规模估计\n"]
    lines.append(f"- 附件3 方式1: {len(a3_1)} 行 @ 4Hz, span ≈ {a3_1.iloc[-1,0]-a3_1.iloc[0,0]:.2f}s")
    lines.append(f"- 附件3 方式2: {len(a3_2)} 行 @ 5Hz, span ≈ {a3_2.iloc[-1,0]-a3_2.iloc[0,0]:.2f}s")
    lines.append(f"- 融合后 10Hz 轨迹估计时长: {span:.2f}s")
    lines.append(f"- 射击目标: {N_s}  拍照目标: {N_p}\n")

    lines.append("## 变量规模矩阵\n")
    lines.append("| 决策网格 | 时刻数 N_t | M=8 (Δθ=45°) | M=12 (Δθ=30°) |")
    lines.append("|---|---|---|---|")
    for hz, label in [(1, "1Hz"), (2, "2Hz"), (5, "5Hz"), (10, "10Hz")]:
        N_t = int(span * hz) + 1
        for M in (8, 12):
            n_var = N_s * N_t + N_p * M * N_t
            lines[-1]  # no-op
        n_var_8 = N_s * N_t + N_p * 8 * N_t
        n_var_12 = N_s * N_t + N_p * 12 * N_t
        lines.append(f"| {label} | {N_t} | {n_var_8:,} | {n_var_12:,} |")

    lines.append("\n## 求解器预算建议\n")
    lines.append("- 2Hz + Δθ=45°: 约 5k 变量 → CBC / CP-SAT 可在 1-3 min 出最优")
    lines.append("- 5Hz + Δθ=30°: 约 35k 变量 → CP-SAT 约 5-15 min；CBC 可能 15-30 min")
    lines.append("- 10Hz + Δθ=30°: 约 70k 变量 → 建议只用 CP-SAT + 贪心；CBC 易超时")
    lines.append("\n**默认策略**: 决策网格 2Hz，Δθ_min 取题面值（待 WMF 阅读确认）；")
    lines.append("贪心基线 2 min 内必出，CP-SAT 预算 20 min，CBC 兜底 40 min。")

    report = "\n".join(lines)
    out = DOCS / "milp_scale.md"
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"\n[OK] 报告已写入 {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
