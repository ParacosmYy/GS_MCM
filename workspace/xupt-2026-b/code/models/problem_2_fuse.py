"""
问题 2：数据对齐与融合（附件2，含噪声 + 固定系统偏差）

方法：
1. 联合最小二乘估计 (Δτ, Δx, Δy)
   - 方式1 为参考系（偏差 0）
   - 方式2 观测模型: z2(t) = p(t - Δτ) + (Δx, Δy) + ε2
   - 对两路建样条后，在对齐后公共时段网格上：
     min_{Δτ,Δx,Δy} Σ || S1(t) - (S2(t-Δτ) + [Δx,Δy]) ||²
2. 异步卡尔曼滤波融合
   - 状态 x = [px, py, vx, vy, ax, ay]^T (常加速度模型)
   - 两路观测按到达时刻异步更新
   - 对齐后在 10Hz 网格上输出滤波轨迹

产出：
- output/traj_10hz_2.csv
- docs/problem2_result.md
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUTPUT = ROOT / "output"
DOCS = ROOT / "docs"
OUTPUT.mkdir(exist_ok=True)
DOCS.mkdir(exist_ok=True)


def load():
    d1 = pd.read_excel(DATA / "附件2.xlsx", sheet_name="方式1(4Hz)")
    d2 = pd.read_excel(DATA / "附件2.xlsx", sheet_name="方式2(5Hz)")
    d1.columns = ["t", "x", "y"]
    d2.columns = ["t", "x", "y"]
    return d1, d2


def build_splines(d: pd.DataFrame):
    t = d["t"].to_numpy()
    sx = CubicSpline(t, d["x"].to_numpy())
    sy = CubicSpline(t, d["y"].to_numpy())
    return sx, sy, t[0], t[-1]


# ─── 阶段 1: 联合估计 (Δτ, Δx, Δy) ───────────────────────────

def joint_estimate(d1, d2):
    s1x, s1y, t1s, t1e = build_splines(d1)
    s2x, s2y, t2s, t2e = build_splines(d2)

    # 初始猜测 Δτ（和问题1类似的逻辑）
    dt_guess = t1s - t2s  # ≈ 102 - 212.3 = -110.3

    def cost(params):
        dtau, dx, dy = params
        ov_s = max(t1s, t2s + dtau)
        ov_e = min(t1e, t2e + dtau)
        if ov_e - ov_s < 10:
            return 1e18
        grid = np.arange(ov_s + 1, ov_e - 1, 0.5)
        x1 = s1x(grid)
        y1 = s1y(grid)
        x2 = s2x(grid - dtau) + dx
        y2 = s2y(grid - dtau) + dy
        return float(np.sum((x1 - x2)**2 + (y1 - y2)**2))

    # 粗搜 Δτ
    best_dt, best_cost = dt_guess, np.inf
    for dt_try in np.arange(dt_guess - 50, dt_guess + 50, 0.5):
        c = cost([dt_try, 0, 0])
        if c < best_cost:
            best_cost = c
            best_dt = dt_try

    # 细搜：Nelder-Mead（3 参数）
    res = minimize(cost, [best_dt, 0, 0], method="Nelder-Mead",
                   options={"xatol": 1e-6, "fatol": 1e-8, "maxiter": 50000})
    dtau_opt, dx_opt, dy_opt = res.x

    # 计算残差统计
    ov_s = max(t1s, t2s + dtau_opt)
    ov_e = min(t1e, t2e + dtau_opt)
    grid = np.arange(ov_s + 1, ov_e - 1, 0.25)
    x1 = s1x(grid); y1 = s1y(grid)
    x2 = s2x(grid - dtau_opt) + dx_opt; y2 = s2y(grid - dtau_opt) + dy_opt
    res_x = x1 - x2; res_y = y1 - y2
    rmse = np.sqrt(np.mean(res_x**2 + res_y**2))
    sigma_est = np.sqrt((np.var(res_x) + np.var(res_y)) / 2)

    return dtau_opt, dx_opt, dy_opt, rmse, sigma_est, (t1s, t1e, t2s, t2e)


# ─── 阶段 2: 异步卡尔曼滤波 ────────────────────────────────────

def kalman_fuse(d1, d2, dtau, dx, dy):
    """
    常加速度模型 KF，两路异步观测。
    对齐后：方式2 真实时间 = t2_原始 + dtau，偏差已校正 (减去 dx, dy)。
    """
    # 校正方式2
    t1 = d1["t"].to_numpy()
    obs1 = np.column_stack([d1["x"].to_numpy(), d1["y"].to_numpy()])

    t2_aligned = d2["t"].to_numpy() + dtau
    obs2 = np.column_stack([d2["x"].to_numpy() - dx, d2["y"].to_numpy() - dy])

    # 合并观测并按时间排序
    all_t = np.concatenate([t1, t2_aligned])
    all_obs = np.concatenate([obs1, obs2], axis=0)
    # 标记来源（用于潜在不同 R）
    src = np.concatenate([np.ones(len(t1)), 2 * np.ones(len(t2_aligned))])
    order = np.argsort(all_t)
    all_t = all_t[order]
    all_obs = all_obs[order]
    src = src[order]

    # 状态: [x, y, vx, vy, ax, ay]
    n = 6
    # 初始状态
    x_state = np.zeros(n)
    x_state[0] = all_obs[0, 0]
    x_state[1] = all_obs[0, 1]

    # 初始协方差
    P = np.eye(n) * 100.0

    # 过程噪声 (调参：加速度抖动)
    q_a = 5.0  # m/s² 过程噪声强度

    # 观测噪声
    r1 = 0.8**2  # 方式1 噪声方差（从 EDA σ≈0.82）
    r2 = 0.8**2  # 方式2 噪声方差（从 EDA σ≈0.80）

    H = np.zeros((2, n))
    H[0, 0] = 1.0; H[1, 1] = 1.0  # 观测位置

    # 存储 10Hz 输出
    t_start = all_t[0]
    t_end = all_t[-1]
    t_10hz = np.arange(t_start, t_end, 0.1)
    out_states = np.zeros((len(t_10hz), 2))
    out_idx = 0

    prev_t = all_t[0]

    for i in range(len(all_t)):
        dt = all_t[i] - prev_t
        if dt < 0:
            dt = 0
        prev_t = all_t[i]

        # Predict
        if dt > 0:
            F = np.eye(n)
            F[0, 2] = dt; F[0, 4] = 0.5 * dt**2
            F[1, 3] = dt; F[1, 5] = 0.5 * dt**2
            F[2, 4] = dt; F[3, 5] = dt

            # Q: 离散化常加速度噪声
            dt2 = dt**2; dt3 = dt**3; dt4 = dt**4; dt5 = dt**5
            Q = np.zeros((n, n))
            Q[0, 0] = dt5/20; Q[0, 2] = dt4/8; Q[0, 4] = dt3/6
            Q[2, 0] = dt4/8;  Q[2, 2] = dt3/3; Q[2, 4] = dt2/2
            Q[4, 0] = dt3/6;  Q[4, 2] = dt2/2; Q[4, 4] = dt
            Q[1, 1] = dt5/20; Q[1, 3] = dt4/8; Q[1, 5] = dt3/6
            Q[3, 1] = dt4/8;  Q[3, 3] = dt3/3; Q[3, 5] = dt2/2
            Q[5, 1] = dt3/6;  Q[5, 3] = dt2/2; Q[5, 5] = dt
            Q *= q_a**2

            x_state = F @ x_state
            P = F @ P @ F.T + Q

        # Update
        r = r1 if src[i] == 1 else r2
        R = np.eye(2) * r
        z = all_obs[i]
        y_innov = z - H @ x_state
        S = H @ P @ H.T + R
        K = P @ H.T @ np.linalg.inv(S)
        x_state = x_state + K @ y_innov
        P = (np.eye(n) - K @ H) @ P

        # 输出 10Hz 轨迹（当经过 10Hz 时刻时记录）
        while out_idx < len(t_10hz) and t_10hz[out_idx] <= all_t[i]:
            # 插值到精确 10Hz 时刻（用当前状态近似）
            dt_back = all_t[i] - t_10hz[out_idx]
            out_states[out_idx, 0] = x_state[0] - x_state[2] * dt_back
            out_states[out_idx, 1] = x_state[1] - x_state[3] * dt_back
            out_idx += 1

    # 填充尾部
    while out_idx < len(t_10hz):
        out_states[out_idx] = x_state[:2]
        out_idx += 1

    return t_10hz, out_states


def main() -> None:
    d1, d2 = load()

    # 联合估计
    dtau, dx, dy, rmse, sigma, spans = joint_estimate(d1, d2)
    print(f"联合估计结果: Δτ={dtau:.6f}s, Δx={dx:.4f}m, Δy={dy:.4f}m")
    print(f"  RMSE={rmse:.4f}m, σ_est={sigma:.4f}m")

    # 卡尔曼融合
    t_10hz, states = kalman_fuse(d1, d2, dtau, dx, dy)

    # 输出
    traj = pd.DataFrame({"t": t_10hz, "x": states[:, 0], "y": states[:, 1]})
    traj.to_csv(OUTPUT / "traj_10hz_2.csv", index=False)

    # 报告
    lines = [
        "# 问题 2 求解结果\n",
        f"- 时间偏差 Δτ = {dtau:.6f} s",
        f"- 系统偏差 Δx = {dx:.4f} m,  Δy = {dy:.4f} m",
        f"- 对齐残差 RMSE = {rmse:.4f} m",
        f"- 估计噪声 σ ≈ {sigma:.4f} m",
        f"- KF 融合 10Hz 轨迹点数: {len(traj)}",
        f"- 轨迹时间范围: [{t_10hz[0]:.3f}, {t_10hz[-1]:.3f}]",
        f"- 输出: output/traj_10hz_2.csv",
    ]
    report = "\n".join(lines)
    (DOCS / "problem2_result.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
