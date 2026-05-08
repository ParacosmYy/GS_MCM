# 2026 西安邮电大学 校赛数学建模（B 题）

本目录是 **2026 年西邮校赛 B 题（多源融合机器人定位及任务优化）** 的参赛工作目录，位于 `xupt-2026-b` 分支。

**当前状态：final-v20（29 页），全部 16 张图表已中文化，论文定稿。**

## 目录结构

```
xupt-2026-b/
├── paper.tex              主 LaTeX 文件（ctex + xelatex）
├── preamble.tex           宏包 / 字体 / 排版设置
├── refs.bib               参考文献（国标 GB/T 7714-2015）
├── sections/              分章节源码（12 节）
│   ├── 00_cover.tex       封面承诺书
│   ├── 00_abstract.tex    摘要
│   ├── 01_problem.tex     一、问题重述
│   ├── 02_analysis.tex    二、问题分析
│   ├── 03_assumptions.tex 三、模型假设
│   ├── 04_notation.tex    四、符号说明
│   ├── 05_model1.tex      五、问题一（时间对齐）
│   ├── 06_model2.tex      六、问题二（对齐+融合）
│   ├── 07_model3.tex      七、问题三（真实数据+偏差检验）
│   ├── 08_model4.tex      八、问题四（任务规划 CP-SAT）
│   ├── 09_validation.tex  九、模型验证与灵敏度
│   ├── 10_evaluation.tex  十、模型评价
│   └── 11_conclusion.tex  十一、结论
├── code/                  Python 求解脚本
│   ├── preprocess/        数据预处理（EDA / 红字扫描 / 规模估计）
│   ├── models/            问题 1-4 求解代码
│   └── verifications/     自证脚本（与 models 一一对应）
├── data/                  题目原始材料
│   ├── problem.docx       原题
│   ├── 附件1-4.xlsx       附件数据
│   ├── result.xlsx        问题 4 答题模板
│   └── result_redcells.json  红字保护基线（17 个单元）
├── figures/               图表输出（23 张 png，全部中文标注）
│   ├── fig_method_flowchart.png    总方法流程图
│   ├── fig_p1_*.png                问题一（对齐 + 代价曲面）
│   ├── fig_p2_*.png                问题二（KF创新 + 残差热力图）
│   ├── fig_p3_*.png                问题三（Bootstrap / Wald / 模型对比）
│   ├── fig_p4_*.png                问题四（Gantt / 地图 / 得分饼图 / 速度）
│   ├── fig_results_radar.png       综合雷达图
│   ├── fig_noise_heatmap.png       噪声热力图
│   ├── sensitivity_*.png           灵敏度分析
│   └── eda_*.png                   EDA 探索性分析
├── output/                最终交付
│   ├── final_paper.pdf             定稿论文（29 页）
│   ├── ai_usage_report.pdf         AI 工具使用声明
│   ├── result.xlsx / result_v{1,2}.xlsx  问题 4 答案
│   └── traj_10hz_{1,2,3}.csv      问题 1/2/3 的 10Hz 轨迹
├── docs/                  非论文文档
│   ├── BUILD_GUIDE.md     完整建模流程指南（530+ 行复现文档）
│   ├── constraints.md     问题 4 约束阈值记录
│   ├── milp_scale.md      MILP 变量规模估计
│   ├── eda_report.md      EDA 报告
│   ├── sensitivity_report.md  灵敏度分析报告
│   └── problem{1-4}_result.md  各问题求解记录
├── CUMCM_Workspace/       AutoMCM-Pro 沙盒（`.gitignore` 屏蔽）
└── README.md
```

## 编译

```bash
xelatex paper.tex
biber paper
xelatex paper.tex
xelatex paper.tex
```

## Python 环境

共享 venv: `D:/Tool/MATH/python-venv/`  
已装：pandas, numpy, scipy, matplotlib, openpyxl, python-docx, statsmodels, scikit-learn, pulp, ortools 等。

## AutoMCM-Pro 流水线

在本目录下启动（`CUMCM_Workspace/` 子目录作为 AI 建模沙盒）：

```bash
cd D:/Tool/MATH/workspace/xupt-2026-b
D:/Tool/MATH/python-venv/Scripts/python.exe D:/Tool/MATH/AutoMCM-Pro/scripts/setup_workspace.py --mode cumcm
D:/Tool/MATH/python-venv/Scripts/python.exe D:/Tool/MATH/AutoMCM-Pro/scripts/pipeline_manager.py init \
    --mode MANUAL --contest CUMCM --choice B --problems 4
```

模式 MANUAL / 4 并行 / 不开 `--git`（沙盒整目录已被 `.gitignore` 屏蔽）。

## 版本历程

| 版本 | 页数 | 关键变更 |
|------|------|----------|
| final-v4 | 34 | 致命硬伤修复 + 表格美化 |
| final-v5 | 28 | 赛规合规 + 摘要精简 + 版面压缩 |
| final-v8 | 25 | 去AI腔 + 流程图标签修复 |
| final-v11 | 26 | 问题分析配图 + 摘要精控 |
| final-v16 | 29 | CP-SAT优化 + 去AI腔 + 图表视觉升级 |
| final-v17 | 30 | 四问精美流程图 + 附录精简 |
| final-v19 | 30 | 修复中文乱码 + 全部图表中文化 |
| **final-v20** | **29** | **全部16张图表中文化定稿 + 删除孤立脚注** |
