"""
问题 3：真实数据（附件3）— 偏差判定 + 融合

流程：
1. 联合估计 (Δτ, Δx, Δy)（同问题2方法）
2. Wald 检验：H0: (Δx, Δy) = (0, 0)
   - 构造 W = [Δx̂, Δŷ] @ Σ_bias_inv @ [Δx̂, Δŷ]^T ~ χ²(2)
   - 协方差通过 bootstrap 估计
3. AIC 对比：零偏模型 vs 带偏模型
4. 判决后执行相应流程
5. 输出 10Hz 轨迹供问题 4

注意：附件3 两路时段完全不重叠（方式1 t∈[469,814], 方式2 t∈[77,401]）
→ Δτ 在 [+300, +500] 范围（方式2 + Δτ ≈ 方式1）

产出：
- output/traj_10hz_3.csv
- docs/problem3_result.md
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
from scipy.optimize import minimize
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUTPUT = ROOT / "output"
DOCS = ROOT / "docs"
OUTPUT.mkdir(exist_ok=True)


def load():
    d1 = pd.read_excel(DATA / "附件3.xlsx", sheet_name="方式1(4Hz)")
    d2 = pd.read_excel(DATA / "附件3.xlsx", sheet_name="方式2(5Hz)")
    d1.columns = ["t", "x", "y"]
    d2.columns = ["t", "x", "y"]
    return d1, d2


def build_splines(d):
    t = d["t"].to_numpy()
    sx = CubicSpline(t, d["x"].to_numpy())
    sy = CubicSpline(t, d["y"].to_numpy())
    return sx, sy, t[0], t[-1]


def joint_estimate_3params(d1, d2):
    """估计 (Δτ, Δx, Δy)"""
    s1x, s1y, t1s, t1e = build_splines(d1)
    s2x, s2y, t2s, t2e = build_splines(d2)

    # 附件3: Δτ ≈ t1_start - t2_start ≈ 469 - 77 ≈ 392
    dt_guess = t1s - t2s

    def cost(params):
        dtau, dx, dy = params
        ov_s = max(t1s, t2s + dtau)
        ov_e = min(t1e, t2e + dtau)
        if ov_e - ov_s < 5:
            return 1e18
        grid = np.arange(ov_s + 0.5, ov_e - 0.5, 0.5)
        if len(grid) < 10:
            return 1e18
        x1 = s1x(grid); y1 = s1y(grid)
        x2 = s2x(grid - dtau) + dx; y2 = s2y(grid - dtau) + dy
        return float(np.sum((x1 - x2)**2 + (y1 - y2)**2))

    # 粗搜 Δτ
    best_dt, best_c = dt_guess, np.inf
    for dt_try in np.arange(dt_guess - 50, dt_guess + 50, 1.0):
        c = cost([dt_try, 0, 0])
        if c < best_c:
            best_c = c
            best_dt = dt_try

    res = minimize(cost, [best_dt, 0, 0], method="Nelder-Mead",
                   options={"xatol": 1e-5, "fatol": 1e-6, "maxiter": 80000})
    return res.x, res.fun


def joint_estimate_1param(d1, d2):
    """仅估 Δτ（零偏假设）"""
    s1x, s1y, t1s, t1e = build_splines(d1)
    s2x, s2y, t2s, t2e = build_splines(d2)
    dt_guess = t1s - t2s

    def cost(params):
        dtau = params[0]
        ov_s = max(t1s, t2s + dtau)
        ov_e = min(t1e, t2e + dtau)
        if ov_e - ov_s < 5:
            return 1e18
        grid = np.arange(ov_s + 0.5, ov_e - 0.5, 0.5)
        if len(grid) < 10:
            return 1e18
        x1 = s1x(grid); y1 = s1y(grid)
        x2 = s2x(grid - dtau); y2 = s2y(grid - dtau)
        return float(np.sum((x1 - x2)**2 + (y1 - y2)**2))

    best_dt, best_c = dt_guess, np.inf
    for dt_try in np.arange(dt_guess - 50, dt_guess + 50, 1.0):
        c = cost([dt_try])
        if c < best_c:
            best_c = c
            best_dt = dt_try

    res = minimize(cost, [best_dt], method="Nelder-Mead",
                   options={"xatol": 1e-5, "fatol": 1e-6, "maxiter": 50000})
    return res.x[0], res.fun


def bootstrap_bias_cov(d1, d2, dtau_hat, dx_hat, dy_hat, n_boot=200):
    """Bootstrap 估计 (Δx, Δy) 的协方差"""
    rng = np.random.default_rng(42)
    n1, n2 = len(d1), len(d2)
    estimates = []
    for _ in range(n_boot):
        idx1 = rng.choice(n1, n1, replace=True)
        idx2 = rng.choice(n2, n2, replace=True)
        b1 = d1.iloc[np.sort(idx1)].reset_index(drop=True)
        b2 = d2.iloc[np.sort(idx2)].reset_index(drop=True)
        # 去重时间（样条需要严格递增）
        b1 = b1.drop_duplicates(subset="t").sort_values("t").reset_index(drop=True)
        b2 = b2.drop_duplicates(subset="t").sort_values("t").reset_index(drop=True)
        if len(b1) < 50 or len(b2) < 50:
            continue
        try:
            params, _ = joint_estimate_3params(b1, b2)
            estimates.append(params[1:])  # (Δx, Δy)
        except Exception:
            continue
    estimates = np.array(estimates)
    if len(estimates) < 30:
        return np.eye(2) * 1.0  # fallback
    return np.cov(estimates.T)


def kalman_fuse_3(d1, d2, dtau, dx, dy):
    """同问题2的 KF，但用附件3的噪声水平"""
    t1 = d1["t"].to_numpy()
    obs1 = np.column_stack([d1["x"].to_numpy(), d1["y"].to_numpy()])
    t2_aligned = d2["t"].to_numpy() + dtau
    obs2 = np.column_stack([d2["x"].to_numpy() - dx, d2["y"].to_numpy() - dy])

    all_t = np.concatenate([t1, t2_aligned])
    all_obs = np.concatenate([obs1, obs2], axis=0)
    src = np.concatenate([np.ones(len(t1)), 2 * np.ones(len(t2_aligned))])
    order = np.argsort(all_t)
    all_t = all_t[order]; all_obs = all_obs[order]; src = src[order]

    n = 6
    x_state = np.zeros(n)
    x_state[0] = all_obs[0, 0]; x_state[1] = all_obs[0, 1]
    P = np.eye(n) * 200.0
    q_a = 8.0
    r1, r2 = 4.2**2, 2.9**2  # EDA 估计 σ
    H = np.zeros((2, n)); H[0, 0] = 1; H[1, 1] = 1

    t_start, t_end = all_t[0], all_t[-1]
    t_10hz = np.arange(t_start, t_end, 0.1)
    out_states = np.zeros((len(t_10hz), 2))
    out_idx = 0
    prev_t = all_t[0]

    for i in range(len(all_t)):
        dt = all_t[i] - prev_t
        if dt < 0: dt = 0
        prev_t = all_t[i]
        if dt > 0:
            F = np.eye(n)
            F[0, 2] = dt; F[0, 4] = 0.5*dt**2
            F[1, 3] = dt; F[1, 5] = 0.5*dt**2
            F[2, 4] = dt; F[3, 5] = dt
            dt2 = dt**2; dt3 = dt**3; dt4 = dt**4; dt5 = dt**5
            Q = np.zeros((n, n))
            Q[0,0]=dt5/20; Q[0,2]=dt4/8; Q[0,4]=dt3/6
            Q[2,0]=dt4/8;  Q[2,2]=dt3/3; Q[2,4]=dt2/2
            Q[4,0]=dt3/6;  Q[4,2]=dt2/2; Q[4,4]=dt
            Q[1,1]=dt5/20; Q[1,3]=dt4/8; Q[1,5]=dt3/6
            Q[3,1]=dt4/8;  Q[3,3]=dt3/3; Q[3,5]=dt2/2
            Q[5,1]=dt3/6;  Q[5,3]=dt2/2; Q[5,5]=dt
            Q *= q_a**2
            x_state = F @ x_state; P = F @ P @ F.T + Q

        r = r1 if src[i] == 1 else r2
        R = np.eye(2) * r
        z = all_obs[i]
        y_innov = z - H @ x_state
        S = H @ P @ H.T + R
        K = P @ H.T @ np.linalg.inv(S)
        x_state = x_state + K @ y_innov
        P = (np.eye(n) - K @ H) @ P

        while out_idx < len(t_10hz) and t_10hz[out_idx] <= all_t[i]:
            dt_back = all_t[i] - t_10hz[out_idx]
            out_states[out_idx, 0] = x_state[0] - x_state[2]*dt_back
            out_states[out_idx, 1] = x_state[1] - x_state[3]*dt_back
            out_idx += 1

    while out_idx < len(t_10hz):
        out_states[out_idx] = x_state[:2]
        out_idx += 1

    return t_10hz, out_states


def main() -> None:
    d1, d2 = load()

    # 带偏估计
    params_3, sse_3 = joint_estimate_3params(d1, d2)
    dtau, dx, dy = params_3
    print(f"带偏模型: Δτ={dtau:.4f}, Δx={dx:.4f}, Δy={dy:.4f}, SSE={sse_3:.2f}")

    # 零偏估计
    dtau_0, sse_0 = joint_estimate_1param(d1, d2)
    print(f"零偏模型: Δτ={dtau_0:.4f}, SSE={sse_0:.2f}")

    # AIC 对比（n = 公共时段网格点数）
    s1x, s1y, t1s, t1e = build_splines(d1)
    s2x, s2y, t2s, t2e = build_splines(d2)
    ov_s = max(t1s, t2s + dtau); ov_e = min(t1e, t2e + dtau)
    n_obs = int((ov_e - ov_s) / 0.5)
    aic_3 = n_obs * np.log(sse_3 / n_obs) + 2 * 3
    aic_0 = n_obs * np.log(sse_0 / n_obs) + 2 * 1
    delta_aic = aic_0 - aic_3  # 正值 → 带偏模型更好
    print(f"AIC: 带偏={aic_3:.2f}, 零偏={aic_0:.2f}, ΔAIC={delta_aic:.2f}")

    # Wald 检验
    print("Running bootstrap for bias covariance...")
    Sigma = bootstrap_bias_cov(d1, d2, dtau, dx, dy, n_boot=150)
    bias_vec = np.array([dx, dy])
    try:
        Sigma_inv = np.linalg.inv(Sigma)
        W = bias_vec @ Sigma_inv @ bias_vec
    except np.linalg.LinAlgError:
        W = 0.0
    p_value = 1 - chi2.cdf(W, df=2)
    print(f"Wald: W={W:.4f}, p={p_value:.6f}")

    # 判决
    has_bias = (p_value < 0.05) and (delta_aic > 2)
    verdict = "存在系统偏差 (H1)" if has_bias else "无显著系统偏差 (H0)"
    print(f"判决: {verdict}")

    # 融合
    if has_bias:
        t_10hz, states = kalman_fuse_3(d1, d2, dtau, dx, dy)
    else:
        t_10hz, states = kalman_fuse_3(d1, d2, dtau_0, 0, 0)

    traj = pd.DataFrame({"t": t_10hz, "x": states[:, 0], "y": states[:, 1]})
    traj.to_csv(OUTPUT / "traj_10hz_3.csv", index=False)

    # 报告
    lines = [
        "# 问题 3 求解结果\n",
        "## 带偏模型",
        f"- Δτ = {dtau:.6f} s",
        f"- Δx = {dx:.4f} m, Δy = {dy:.4f} m",
        f"- SSE = {sse_3:.2f}\n",
        "## 零偏模型",
        f"- Δτ = {dtau_0:.6f} s",
        f"- SSE = {sse_0:.2f}\n",
        "## 偏差检验",
        f"- AIC 带偏 = {aic_3:.2f}, AIC 零偏 = {aic_0:.2f}, ΔAIC = {delta_aic:.2f}",
        f"- Wald W = {W:.4f}, p-value = {p_value:.6f}",
        f"- Bootstrap 协方差 Σ_bias = {Sigma.tolist()}",
        f"- **判决: {verdict}**\n",
        "## 融合输出",
        f"- 10Hz 轨迹点数: {len(traj)}",
        f"- 时间范围: [{t_10hz[0]:.3f}, {t_10hz[-1]:.3f}]",
        f"- 输出: output/traj_10hz_3.csv",
    ]
    (DOCS / "problem3_result.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\n10Hz 轨迹 {len(traj)} 点 → output/traj_10hz_3.csv")


if __name__ == "__main__":
    main()
