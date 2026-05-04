# 2026 XUPT Campus MCM

西安邮电大学 2026 校赛数学建模 — 参赛工作目录。

## Layout

```
2026_XUPT_Campus_MCM/
├── data/        # Raw / cleaned competition data
├── code/        # Python scripts (solvers, preprocessing, plotting)
├── figures/     # Generated figures referenced by paper.tex
├── paper.tex    # Main LaTeX manuscript (xelatex + ctex)
└── README.md
```

## Build

Open `paper.tex` in VSCode and press `Ctrl+S` (auto xelatex x2 via LaTeX Workshop),
or from the Git Bash terminal:

```bash
xelatex paper.tex && xelatex paper.tex
```

## Python

Uses the shared venv at `D:\Tool\math\python-venv`. Run solver:

```bash
python code/main.py
```
