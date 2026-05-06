"""
问题 1：时间对齐（附件1，无噪声）

方法：
1. 对两路 (t,x,y) 各建三次样条 S1(t), S2(t)
2. 令 Δτ 为方式2相对方式1的时间偏差：S1(t) ≈ S2(t - Δτ)
   即方式2的真实时间 = 方式2的时间戳 + Δτ
3. 在公共时段上最小化残差平方和：
   J(Δτ) = Σ || S1(t_k) - S2(t_k - Δτ) ||²
4. 一维搜索（scipy.optimize.minimize_scalar，先粗后细）
5. 输出 10Hz 联合轨迹（无噪声 → 两路重合，取均值）

产出：
- output/traj_10hz_1.csv
- docs/problem1_result.md
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
from scipy.optimize import minimize_scalar

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUTPUT = ROOT / "output"
DOCS = ROOT / "docs"
OUTPUT.mkdir(exist_ok=True)
DOCS.mkdir(exist_ok=True)


def load():
    d1 = pd.read_excel(DATA / "附件1.xlsx", sheet_name="方式1(4Hz)")
    d2 = pd.read_excel(DATA / "附件1.xlsx", sheet_name="方式2(5Hz)")
    d1.columns = ["t", "x", "y"]
    d2.columns = ["t", "x", "y"]
    return d1, d2


def build_splines(d: pd.DataFrame):
    t = d["t"].to_numpy()
    sx = CubicSpline(t, d["x"].to_numpy())
    sy = CubicSpline(t, d["y"].to_numpy())
    return sx, sy, t[0], t[-1]


def cost(delta_tau, s1x, s1y, s2x, s2y, t_grid):
    """S1(t) vs S2(t - Δτ) 在 t_grid 上的 SSE"""
    t2 = t_grid - delta_tau
    dx = s1x(t_grid) - s2x(t2)
    dy = s1y(t_grid) - s2y(t2)
    return float(np.sum(dx**2 + dy**2))


def main() -> None:
    d1, d2 = load()
    s1x, s1y, t1_start, t1_end = build_splines(d1)
    s2x, s2y, t2_start, t2_end = build_splines(d2)

    # Δτ 搜索范围：方式2时间 + Δτ ≈ 方式1时间 → Δτ ≈ t1 - t2
    # 附件1：t1_start=221, t2_start=468.83 → Δτ ≈ -247.83
    # 搜索域 [-300, -200]
    dt_guess = t1_start - t2_start
    dt_lo, dt_hi = dt_guess - 50, dt_guess + 50

    # 公共时段计算（Δτ 对齐后）
    def get_overlap(dt):
        # 方式2对齐后时间 = t2 + dt → 范围 [t2_start+dt, t2_end+dt]
        ov_start = max(t1_start, t2_start + dt)
        ov_end = min(t1_end, t2_end + dt)
        return ov_start, ov_end

    # 粗搜 + 细搜
    # 粗搜：网格 0.1s
    best_dt = dt_guess
    best_cost = np.inf
    for dt_try in np.arange(dt_lo, dt_hi, 0.1):
        ov_s, ov_e = get_overlap(dt_try)
        if ov_e <= ov_s:
            continue
        grid = np.arange(ov_s, ov_e, 0.5)  # 粗网格 0.5s
        c = cost(dt_try, s1x, s1y, s2x, s2y, grid)
        if c < best_cost:
            best_cost = c
            best_dt = dt_try

    # 细搜：scipy 在粗搜最优 ±1s 范围内
    ov_s, ov_e = get_overlap(best_dt)
    fine_grid = np.arange(ov_s + 1, ov_e - 1, 0.1)  # 密网格

    def obj(dt):
        ov_s2, ov_e2 = get_overlap(dt)
        if ov_e2 <= ov_s2:
            return 1e18
        g = fine_grid[(fine_grid >= ov_s2) & (fine_grid <= ov_e2)]
        if len(g) < 10:
            return 1e18
        return cost(dt, s1x, s1y, s2x, s2y, g)

    res = minimize_scalar(obj, bounds=(best_dt - 1, best_dt + 1), method="bounded",
                          options={"xatol": 1e-6})
    delta_tau_opt = res.x

    # 最终公共时段和残差
    ov_start, ov_end = get_overlap(delta_tau_opt)
    final_grid = np.arange(ov_start, ov_end, 0.1)  # 10Hz

    x1 = s1x(final_grid)
    y1 = s1y(final_grid)
    x2 = s2x(final_grid - delta_tau_opt)
    y2 = s2y(final_grid - delta_tau_opt)
    rmse = np.sqrt(np.mean((x1 - x2)**2 + (y1 - y2)**2))

    # 无噪声 → 取均值（理论上两路重合）
    x_out = (x1 + x2) / 2
    y_out = (y1 + y2) / 2

    # 输出
    traj = pd.DataFrame({"t": final_grid, "x": x_out, "y": y_out})
    traj.to_csv(OUTPUT / "traj_10hz_1.csv", index=False)

    # 报告
    lines = [
        "# 问题 1 求解结果\n",
        f"- 最优时间偏差 Δτ = {delta_tau_opt:.6f} s",
        f"  - 含义：方式2的真实时间 = 方式2时间戳 + ({delta_tau_opt:.6f})",
        f"- 对齐后 RMSE = {rmse:.2e} m（无噪声理论应为 ~0）",
        f"- 公共时段: [{ov_start:.3f}, {ov_end:.3f}]  长度 {ov_end-ov_start:.3f}s",
        f"- 10Hz 轨迹点数: {len(traj)}",
        f"- 输出: output/traj_10hz_1.csv",
    ]
    report = "\n".join(lines)
    (DOCS / "problem1_result.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
