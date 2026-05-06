Problem 3 Visualization Summary
================================

Generated: 2026-05-07
Script: code/visualization/fig_p3.py
Python: D:/Tool/MATH/python-venv/Scripts/python.exe

Figures Generated (all dpi=200, professional style):
---------------------------------------------------

1. fig_p3_wald_chi2.png (109K)
   - Chi-square(2) distribution PDF curve
   - Critical value chi2_0.05(2) = 5.991 (red dashed line)
   - Observed Wald statistic W = 2.066 (green line)
   - Annotated: "W = 2.07, p = 0.356"
   - Rejection region shaded (right tail, alpha=0.05)
   - Title: "Wald Test for Systematic Bias"
   - Interpretation: W < critical value → fail to reject H0 (no bias)

2. fig_p3_bootstrap_scatter.png (178K)
   - Bootstrap estimates from 150 resamples: (Δx, Δy)
   - Point estimate: (0.088, 0.296) marked with red star
   - Null hypothesis origin: (0, 0) marked with black cross
   - 95% confidence ellipse (red dashed) using chi-square(2)
   - All 150 bootstrap samples successfully computed
   - Interpretation: confidence ellipse includes origin → consistent with H0

3. fig_p3_model_comparison.png (118K)
   - Bar chart comparison: Zero-bias vs Biased model
   - Left Y-axis: SSE and AIC values
   - Right Y-axis: Number of parameters (k)
   - Zero-bias: SSE=28659.6, AIC=2318.92, k=1
   - Biased: SSE=28602.7, AIC=2321.73, k=3
   - ΔAIC = -2.81 (annotated with arrow)
   - Interpretation: Zero-bias model preferred (lower AIC)

Key Statistical Results:
-----------------------
- Wald statistic: W = 2.066, p-value = 0.356 (> 0.05)
- ΔAIC = -2.81 (zero-bias model has lower AIC)
- Bootstrap: 150/150 successful estimates
- Biased model parameters: Δτ=367.87s, Δx=0.088m, Δy=0.296m
- Conclusion: No significant systematic bias detected

Technical Details:
-----------------
- Data source: data/附件3.xlsx (Method 1: 4Hz, Method 2: 5Hz)
- Bootstrap: 150 iterations with random seed 42
- Matplotlib backend: Agg (non-interactive)
- Font: Arial/DejaVu Sans
- Grid style: seaborn-paper
- All labels in English for professional publication

Notes:
------
- Minor warnings about subscript glyphs in Arial font (cosmetic only)
- Bootstrap took ~40 seconds on full dataset
- All figures suitable for academic paper inclusion
