# GS_MCM — Mathematical Modeling Workspace

个人数学建模主仓库，集中管理校赛 / 国赛 / 美赛的题解、代码与论文。
配套 Claude Code skill (**AutoMCM-Pro**) 与本地 LaTeX (**MiKTeX Portable**) 工具链，
实现 *题目 → 建模 → 求解 → 验证 → 排版* 全流程。

---

## Repository Layout

```
D:\Tool\math\                   # ← Local workspace root (this repo)
├── workspace/                  # 📝 Per-contest folders
│   └── 2026_XUPT_Campus_MCM/   #    one subdir = one contest
│       ├── data/               #    raw data
│       ├── code/               #    Python solvers
│       ├── figures/            #    generated plots
│       └── paper.tex           #    LaTeX manuscript
├── AutoMCM-Pro/                # 🚫 Claude skill, cloned separately (gitignored)
├── miktex/                     # 🚫 Local MiKTeX (gitignored)
├── python-venv/                # 🚫 Python venv (gitignored)
├── .vscode/                    # Workspace-level VSCode config
│   ├── settings.json
│   └── extensions.json
├── math.code-workspace         # Double-click to open entire workspace
├── .gitignore
└── README.md
```

---

## Toolchain (Local Only, Not in Repo)

| Component      | Path                                                 | Role                    |
|----------------|------------------------------------------------------|-------------------------|
| MiKTeX 25.12   | `D:\Tool\math\miktex\`                               | xelatex + Chinese fonts |
| Python venv    | `D:\Tool\math\python-venv\`                          | numpy/scipy/...         |
| AutoMCM-Pro    | `D:\Tool\math\AutoMCM-Pro\`                          | `/cumcm-master` skill   |
| Claude Code    | global                                               | AI copilot              |

---

## Workflow for a New Contest

1. Create a folder under `workspace/`, e.g. `workspace/2026_xxx/`
2. Copy `paper.tex` skeleton, add `data/` `code/` `figures/` subdirs
3. Open `math.code-workspace` in VSCode
4. Build paper: `Ctrl+S` (auto xelatex ×2) or `xelatex paper.tex` in terminal
5. Invoke skill: run `claude` inside the contest folder, then `/cumcm-master`

---

## Build Requirements

- Windows 10/11
- Git Bash (default shell for this workspace)
- VSCode + extensions: **LaTeX Workshop**, **Python**, **Jupyter**, **Claude Code**
- See tool paths above — not required for reviewers, only for compilation

## Bootstrap on a Fresh Machine

```bash
git clone https://github.com/ParacosmYy/GS_MCM.git D:/Tool/math
cd D:/Tool/math

# 1. Install MiKTeX Portable into D:\Tool\math\miktex
# 2. Create venv and install Python deps
python -m venv python-venv
source python-venv/Scripts/activate
pip install numpy scipy matplotlib pandas seaborn scikit-learn sympy statsmodels networkx pulp

# 3. Clone the AutoMCM-Pro skill (kept out of this repo)
git clone https://github.com/RealSeaberry/AutoMCM-Pro
cd AutoMCM-Pro && bash install.sh && cd ..
```

---

## Conventions

- **One contest = one folder** under `workspace/`
- Folder naming: `<year>_<contest>_<keyword>`  (e.g. `2026_XUPT_Campus_MCM`)
- LaTeX engine: **xelatex** (required by `ctex`)
- Python code uses the shared venv, not system Python

---

## License

Private competition work. Contact the author before redistribution.
