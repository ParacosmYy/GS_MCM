# 2026 西安邮电大学 校赛数学建模

本目录是 **2026 年西邮校赛数学建模** 的参赛工作目录。

## 目录结构

```
2026_XUPT_Campus_MCM/
├── paper.tex           主 LaTeX 文件（ctex + xelatex）
├── preamble.tex        宏包 / 字体 / 排版设置
├── sections/           分章节源码
│   ├── 00_abstract.tex
│   ├── 01_problem.tex
│   ├── 02_assumptions.tex
│   ├── 03_notation.tex
│   ├── 04_model1.tex
│   ├── 05_model2.tex
│   ├── 06_sensitivity.tex
│   ├── 07_evaluation.tex
│   └── 08_conclusion.tex
├── refs.bib            参考文献（国标 GB/T 7714-2015）
├── code/               Python 求解脚本
│   └── main.py
├── data/               题目数据
├── figures/            生成的图
└── README.md
```

## 编译

**VSCode 方式**：打开 `paper.tex`，按 `Ctrl+S` 自动编译（LaTeX Workshop 使用 xelatex ×2 配方）。

**命令行方式**（Git Bash）：

```bash
xelatex paper.tex
biber paper                # 处理参考文献
xelatex paper.tex
xelatex paper.tex          # 解决交叉引用
```

## Python 求解

使用仓库根目录下的共享 venv（`D:\Tool\math\python-venv`）：

```bash
source D:/Tool/math/python-venv/Scripts/activate
python code/main.py
```
