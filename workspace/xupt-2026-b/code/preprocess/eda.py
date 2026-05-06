"""
B 题三附件 EDA：
- 采样间隔分布（应严格 0.25s / 0.2s）
- 时间重叠区间
- 附件2/3 的噪声特征（方式内差分统计 + 两路位置差）
- 轨迹图 / 噪声直方图 / 采样间隔直方图

输出到 figures/eda_*.png，报告写到 docs/eda_report.md
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
FIG = ROOT / "figures"
DOCS = ROOT / "docs"
FIG.mkdir(exist_ok=True)
DOCS.mkdir(exist_ok=True)

# 使用默认字体避免中文字体缺失问题（论文图表用英文）
plt.rcParams["axes.unicode_minus"] = False


def load(n: int):
    d1 = pd.read_excel(DATA / f"附件{n}.xlsx", sheet_name="方式1(4Hz)")
    d2 = pd.read_excel(DATA / f"附件{n}.xlsx", sheet_name="方式2(5Hz)")
    d1.columns = ["t", "x", "y"]
    d2.columns = ["t", "x", "y"]
    return d1, d2


def describe(n: int, d1: pd.DataFrame, d2: pd.DataFrame) -> list[str]:
    dt1 = np.diff(d1["t"].to_numpy())
    dt2 = np.diff(d2["t"].to_numpy())
    lines = [
        f"## 附件{n}",
        "",
        f"| 方式 | 行数 | t_start | t_end | span | Δt 均值 | Δt 标准差 |",
        f"|---|---|---|---|---|---|---|",
        f"| 方式1 | {len(d1)} | {d1['t'].iloc[0]:.3f} | {d1['t'].iloc[-1]:.3f} | {d1['t'].iloc[-1]-d1['t'].iloc[0]:.3f} | {dt1.mean():.4f} | {dt1.std():.2e} |",
        f"| 方式2 | {len(d2)} | {d2['t'].iloc[0]:.3f} | {d2['t'].iloc[-1]:.3f} | {d2['t'].iloc[-1]-d2['t'].iloc[0]:.3f} | {dt2.mean():.4f} | {dt2.std():.2e} |",
        "",
    ]
    # 公共时段
    t_start = max(d1["t"].iloc[0], d2["t"].iloc[0])
    t_end = min(d1["t"].iloc[-1], d2["t"].iloc[-1])
    lines.append(f"- 公共时段: [{t_start:.3f}, {t_end:.3f}]  长度 {max(0,t_end-t_start):.3f}s")
    lines.append(f"- 起始时间差: 方式2 − 方式1 = {d2['t'].iloc[0]-d1['t'].iloc[0]:.3f}s")
    lines.append("")
    return lines


def plot_trajectories(n: int, d1, d2):
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    ax[0].plot(d1["x"], d1["y"], ".", ms=1.5, label=f"Sensor 1 (4Hz, N={len(d1)})")
    ax[0].plot(d2["x"], d2["y"], ".", ms=1.5, label=f"Sensor 2 (5Hz, N={len(d2)})", alpha=0.6)
    ax[0].set_xlabel("X [m]"); ax[0].set_ylabel("Y [m]")
    ax[0].set_title(f"Attachment {n}: XY trajectories")
    ax[0].legend(); ax[0].set_aspect("equal", adjustable="datalim"); ax[0].grid(alpha=0.3)

    ax[1].plot(d1["t"], d1["x"], ".", ms=1.2, label="Sensor 1 X")
    ax[1].plot(d2["t"], d2["x"], ".", ms=1.2, label="Sensor 2 X", alpha=0.6)
    ax[1].set_xlabel("t [s]"); ax[1].set_ylabel("X [m]")
    ax[1].set_title(f"Attachment {n}: X vs time")
    ax[1].legend(); ax[1].grid(alpha=0.3)

    fig.tight_layout()
    out = FIG / f"eda_a{n}_trajectory.png"
    fig.savefig(out, dpi=140); plt.close(fig)
    return out


def plot_dt(n: int, d1, d2):
    dt1 = np.diff(d1["t"].to_numpy()); dt2 = np.diff(d2["t"].to_numpy())
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].hist(dt1, bins=40); ax[0].set_title(f"A{n} Sensor1 Δt (expected 0.25)")
    ax[0].set_xlabel("Δt [s]")
    ax[1].hist(dt2, bins=40); ax[1].set_title(f"A{n} Sensor2 Δt (expected 0.20)")
    ax[1].set_xlabel("Δt [s]")
    fig.tight_layout()
    out = FIG / f"eda_a{n}_dt_hist.png"
    fig.savefig(out, dpi=140); plt.close(fig)
    return out


def estimate_noise(d: pd.DataFrame, label: str):
    """基于二阶差分估计观测噪声方差（假设底层轨迹二阶可微，二阶差分主要反映噪声）"""
    x = d["x"].to_numpy(); y = d["y"].to_numpy()
    d2x = np.diff(x, n=2); d2y = np.diff(y, n=2)
    # Var(二阶差分) = 6 * Var(噪声) 当噪声独立
    sx = np.sqrt(d2x.var() / 6)
    sy = np.sqrt(d2y.var() / 6)
    return sx, sy


def main() -> None:
    lines = ["# B 题数据 EDA 报告\n"]
    for n in (1, 2, 3):
        d1, d2 = load(n)
        lines += describe(n, d1, d2)
        traj = plot_trajectories(n, d1, d2)
        dt = plot_dt(n, d1, d2)
        lines.append(f"- 轨迹图: `figures/{traj.name}`")
        lines.append(f"- Δt 直方图: `figures/{dt.name}`")
        sx1, sy1 = estimate_noise(d1, "s1")
        sx2, sy2 = estimate_noise(d2, "s2")
        lines.append(f"- 二阶差分估计噪声 σ: 方式1 ({sx1:.4f}, {sy1:.4f}) m, 方式2 ({sx2:.4f}, {sy2:.4f}) m")
        lines.append("")

    lines.append("## 关键结论\n")
    lines.append("- 附件1：两路 Δt 标准差极小 → 采样稳定无噪声；起始时间差约 247s 需对齐")
    lines.append("- 附件2：两路噪声 σ 显著大于附件1；两路轨迹在公共时段有可见平移偏差")
    lines.append("- 附件3：真实数据，待后续问题3 Wald 检验判定系统偏差")
    lines.append("- **附件3 两路时长不匹配（345 vs 324 s）**：融合后 10Hz 轨迹取两路公共时段")

    (DOCS / "eda_report.md").write_text("\n".join(lines), encoding="utf-8")
    print("[OK] EDA 完成，报告 docs/eda_report.md，图 figures/eda_*.png")


if __name__ == "__main__":
    main()
