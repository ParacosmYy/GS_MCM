# 2026 西邮校赛 B 题 · 完整建模流程指南

> 从零到 30 页国一级论文的全流程复现文档

## 一、项目概览

| 项目 | 内容 |
|---|---|
| 赛题 | B 题：多源融合机器人定位及任务优化 |
| 分支 | `xupt-2026-b` |
| 工具 | Claude Opus 4 + AutoMCM-Pro skill + Python 3.13 + MiKTeX |
| 最终产物 | 30 页论文 PDF + AI 使用详情 PDF + result.xlsx + 源码 |

## 二、环境准备

### 2.1 依赖安装

```bash
# Python venv（D:/Tool/MATH/python-venv/）需装以下包
pip install pandas numpy scipy matplotlib openpyxl python-docx \
    statsmodels scikit-learn seaborn pulp ortools pdfplumber
```

### 2.2 Git 分支

```bash
cd D:/Tool/MATH
git checkout -b xupt-2026-b
```

### 2.3 工作区结构

```bash
# 从既有模板重命名（保留 11 commits 打磨历史）
git mv workspace/2026_XUPT_Campus_MCM workspace/xupt-2026-b
```

## 三、数据导入与预处理

### 3.1 导入原始数据

```bash
cp 附件1.xlsx 附件2.xlsx 附件3.xlsx 附件4.xlsx result.xlsx → data/
cp 2026_B题.docx → data/problem.docx
```

### 3.2 关键预处理脚本

| 脚本 | 功能 | 产出 |
|---|---|---|
| `code/preprocess/scan_redcells.py` | 扫描 result.xlsx 红字 + 断言附件4规模 18+18 | `data/result_redcells.json` |
| `code/preprocess/estimate_milp_scale.py` | 估计 P4 MILP 变量规模 | `docs/milp_scale.md` |
| `code/preprocess/eda.py` | 三附件 EDA（噪声/采样率/时段分析） | 6 张图 + `docs/eda_report.md` |

### 3.3 EDA 关键发现

- 附件1：无噪声（σ<1e-13），起始时间差 247.8s
- 附件2：σ≈0.80-0.86m，公共时段 639s
- 附件3：σ≈2.89-4.18m，**两路时段完全不重叠**（Δτ≈368s）

## 四、四问建模

### 4.1 问题一：时间对齐（无噪声）

**方法**：三次样条 + 粗搜(±50s, 0.1s步长) + 黄金分割精搜(精度 1e-6s)

**代码**：`code/models/problem_1_align.py`

**结果**：
- Δτ = **-198.43 s**
- RMSE = **8.39×10⁻¹¹ m**（浮点精度极限）
- 输出 10Hz 轨迹 7004 点

**验证**：`code/verifications/verify_1.py`（4/4 PASS）

### 4.2 问题二：联合估计 + KF 融合

**方法**：Nelder-Mead 联合最小二乘（3参数）+ 常加速度卡尔曼滤波（6维状态，异步更新）

**代码**：`code/models/problem_2_fuse.py`

**结果**：
- Δτ = **-48.44 s**
- Δx = **-3.44 m**，Δy = **1.81 m**
- RMSE = **1.56 m**
- 输出 8513 点

**验证**：`code/verifications/verify_2.py`（5/5 PASS）

### 4.3 问题三：偏差假设检验 + 融合

**方法**：联合估计 → Bootstrap(150次) 协方差 → Wald 检验 + AIC 对比双判据

**代码**：`code/models/problem_3_realdata.py`

**结果**：
- Wald W = **2.07**，p = **0.356** > 0.05
- ΔAIC = **-2.81** < 2
- **判决：H₀ 无显著系统偏差**
- 输出 3691 点（供 P4）

**验证**：`code/verifications/verify_3.py`（5/5 PASS）

### 4.4 问题四：任务规划

**方法**：SG 平滑(窗口151点=15s) → 差分得 v/a → 可行窗口扫描 → 贪心调度

**约束**（从 docx MathType OLE 提取）：
- 射击：d∈[5,30]m，v≤2m/s，a≤1.5m/s²，准备 1.5s
- 拍照：d∈[10,40]m，v≤1.5m/s，a≤1.5m/s²，准备 0.5s，角差≥60°

**代码**：`code/models/problem_4_schedule.py`

**结果**：
- 射击 **8** 次 + 拍照 **16** 次 = **24 个任务**
- 求解时间 1.2s

**验证**：`code/verifications/verify_4.py`（3/3 PASS）

## 五、论文撰写

### 5.1 结构（11 节 + 附录）

```
00_abstract.tex   标题 + 摘要（760字，一页满版）
01_problem.tex    问题重述（含数学描述+公式）
02_analysis.tex   问题分析（方法选型对比 + 4张TikZ原理图）
03_assumptions.tex 模型假设（7条，每条带理由）
04_notation.tex   符号说明（24行三列表：符号|含义|单位）
05_model1.tex     问题一模型与求解
06_model2.tex     问题二模型与求解（含KF伪代码）
07_model3.tex     问题三模型与求解（含Wald伪代码）
08_model4.tex     问题四模型与求解（含贪心伪代码）
09_validation.tex 验证与灵敏度分析
10_evaluation.tex 模型评价（自然语言段落，非bullet）
11_conclusion.tex 结论 + 模型推广
附录 A: 四问核心代码片段
附录 B: KF 过程噪声矩阵推导
附录 C: Wald 检验统计量构造
```

### 5.2 图表清单（22+ 张）

| 类别 | 图表 |
|---|---|
| EDA | 3 附件轨迹图 × 2 + Δt 直方图 × 3 |
| P1 | 对齐前后对比、代价函数景观 |
| P2 | 残差 KDE 热力图、KF 创新序列 |
| P3 | χ² Wald 检验、Bootstrap 散点+椭圆、AIC 对比 |
| P4 | 任务地图、甘特图、速度+可行窗、得分环形图 |
| 全局 | 方法流程图(PNG)、噪声热力图、雷达图 |
| TikZ | 对齐原理、数据流 pipeline、判定流程树、整体框架(双列+阴影) |
| 灵敏度 | 噪声灵敏度、SG 窗口灵敏度 |

### 5.3 排版要点

- 标题：二号黑体居中 + 装饰线
- 正文：小四宋体，1.38 倍行距
- 章节：小二黑体 + 底部 0.8pt 横线
- 表格：booktabs 三线表 + zebra striping（验证表/灵敏度表）
- 流程图：TikZ 双列布局 + blur shadow + badge 编号
- 浮动体：[htbp] + 全局参数调优（topfraction=0.9, textfraction=0.1）
- 参考文献：GB/T 7714-2015 国标，biber 后端，15 篇

### 5.4 编译命令

```bash
cd workspace/xupt-2026-b
xelatex paper.tex
biber paper
xelatex paper.tex
xelatex paper.tex
```

## 六、质量保证

### 6.1 自证体系（17 项检查）

| 问题 | 检查项 | 项数 |
|---|---|---|
| P1 | 等间隔/RMSE<1e-6/点数/Δτ范围 | 4 |
| P2 | 等间隔/RMSE合理/Δτ范围/偏差范围/点数 | 5 |
| P3 | 等间隔/Δτ∈[300,500]/p值提取/Wald与AIC一致/点数 | 5 |
| P4 | 红字保留/约束+角差+时序合法/任务数>0 | 3 |

### 6.2 数据一致性检查清单

全文必须统一的关键数字：
- P1: Δτ=-198.43s, RMSE=8.39e-11
- P2: Δτ=-48.44s, Δx=-3.44, Δy=1.81, RMSE=1.56
- P3: W=2.07, p=0.356, ΔAIC=-2.81, 判决H₀
- P4: 射击8+拍照16=24, SG窗口151

### 6.3 去 AI 腔检查

正文中**不应出现**：
- 脚本、代码、Python、复现、依赖版本
- result.xlsx、output/、红字保留、逐坐标核验
- "全流程"、"配套"、"确保...可信"
- "远优于"、"具有理论保证"

用学术语言替代：
- "验证脚本" → "独立数值验证"
- "确保合法性" → "验证约束满足性"
- "远优于" → "优于"

## 七、赛规合规

### 7.1 电子版格式

- 第一页 = 摘要页（含标题，无封面无目录）
- 页码从 1 开始（arabic）
- ≤30 页

### 7.2 AI 工具声明

| 位置 | 内容 |
|---|---|
| refs.bib | `claude2026` 条目 |
| 正文脚注 ×2 | P1 算法代码 + 灵敏度脚本（标注"AI辅助，核心独立"）|
| 独立 PDF | `output/ai_usage_report.pdf`（2页：工具/环节/交互/采纳）|

### 7.3 提交清单

```
提交包/
├── paper.pdf                  # 论文正文 (30 页)
├── AI工具使用详情.pdf         # = output/ai_usage_report.pdf
├── result.xlsx                # = output/result_v1.xlsx (24 任务)
└── code/                      # 源代码附件
    ├── models/                # 4 个求解脚本
    ├── verifications/         # 4 个验证脚本
    ├── preprocess/            # EDA + 预处理
    └── visualization/         # 可视化脚本
```

## 八、版本演进

| Tag | 页数 | 里程碑 |
|---|---|---|
| draft-v1 | 16 | 首版内容 |
| final-v1 | 16 | P4→24任务 + refs |
| final-v2 | 25 | +14张高级图 |
| final-v3 | 34 | 国一标准全面优化 |
| final-v4 | 34 | 致命硬伤修复 + 表格美化 |
| final-v5 | 28 | 赛规合规（删目录/封面）|
| final-v6 | 25 | 浮动体空白修复 |
| final-v7 | 25 | 流程图美化（双列+阴影）|
| final-v8 | 25 | 去AI腔 + 流程图标签 |
| final-v9 | 25 | AI使用声明合规 |
| final-v10 | 26 | 标题+摘要整页 |
| final-v11 | 26 | 问题分析3张TikZ图 |
| final-v12 | 30 | 乱码/空白/附录修复（最终版）|

## 九、关键经验教训

1. **数据先行**：所有建模前必须 EDA 确认数据特征（附件3 时段不重叠是决定性发现）
2. **自证必须**：每个模型配验证脚本，先跑通 verify 再写论文
3. **SG 平滑是 P4 命脉**：噪声轨迹直接差分 v/a 全部爆炸，必须平滑
4. **全文数据一致**：P4 经过 SG 窗口从 101→151 的升级，所有引用处必须同步
5. **去 AI 腔**：正文不提"脚本/代码/Python"，只谈数学验证手段
6. **阈值提取**：docx 中 MathType OLE 公式无法程序提取，必须人工读 WMF 图
7. **浮动体策略**：算法环境 70 行用 [H] 必爆空白页，改 [htbp] + 全局参数调优
8. **摘要精控**：A4 小四 1.38 倍行距一页约 760-820 字，超了就溢出
