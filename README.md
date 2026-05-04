# GS_MCM — 数学建模论文仓库

个人数学建模主仓库，集中管理 **校赛 / 国赛 / 美赛** 的题解、Python 求解代码与 LaTeX 论文。

## 仓库定位

本仓库**只追踪比赛论文源码**（LaTeX、Python、数据、图）。
工具链（MiKTeX Portable / Python venv / AutoMCM-Pro skill）**不在仓库中**，按下文指引本地安装到 `D:\Tool\math\` 下即可配合使用。

---

## 目录结构

```
D:\Tool\math\                   ← 本仓库根目录
├── workspace/                  📝 按赛事组织的工作目录
│   └── 2026_XUPT_Campus_MCM/   每场比赛一个子目录
│       ├── paper.tex           主 LaTeX 文件
│       ├── preamble.tex        宏包 / 字体 / 排版
│       ├── sections/           分章节源码
│       ├── refs.bib            参考文献（国标 gb7714-2015）
│       ├── code/               Python 求解脚本
│       ├── data/               题目数据
│       ├── figures/            生成的图
│       └── README.md
├── .vscode/                    工作区级别的 VSCode 配置（共享）
├── math.code-workspace         双击此文件用 VSCode 打开（推荐）
├── .gitignore
└── README.md
```

以下目录 / 文件**不入库**（由 `.gitignore` 管理）：
`miktex/` `texlive/` `python-venv/` `AutoMCM-Pro/` `miktex-portable.exe` `_diag.ps1` 以及所有 LaTeX 编译中间产物。

---

## 本地工具链（不入库，按机器安装）

| 组件           | 本机路径                                             | 作用                              |
|----------------|------------------------------------------------------|-----------------------------------|
| MiKTeX 25.12   | `D:\Tool\math\miktex\`                               | xelatex 编译器 + 中文字体支持     |
| Python venv    | `D:\Tool\math\python-venv\`                          | AutoMCM-Pro 运行所需 Python 环境  |
| AutoMCM-Pro    | `D:\Tool\math\AutoMCM-Pro\`                          | Claude Code skill（`/cumcm-master`） |
| Claude Code    | 全局安装                                             | AI 协作助手                       |

### AutoMCM-Pro（第三方 Claude Skill）

- 项目地址：**https://github.com/RealSeaberry/AutoMCM-Pro**
- 作用：提供 `/cumcm-master` 斜杠命令，驱动 *题目 → 建模 → 求解 → 验证 → 排版* 全流程
- 安装：见下方 bootstrap，`install.sh` 会自动创建 `python-venv/` 并下载 MiKTeX Portable

---

## 新机器 Bootstrap

```bash
# 1. 克隆本仓库到固定路径（路径敏感，工具链配置写死在此）
git clone https://github.com/ParacosmYy/GS_MCM.git D:/Tool/math
cd D:/Tool/math

# 2. 克隆并安装 AutoMCM-Pro（会自动准备 MiKTeX Portable 与 Python venv）
git clone https://github.com/RealSeaberry/AutoMCM-Pro
cd AutoMCM-Pro && bash install.sh && cd ..

# 3. 双击 math.code-workspace 用 VSCode 打开
```

> ⚠️ **务必从 `math.code-workspace` 打开项目**，否则 VSCode 无法找到便携版 MiKTeX 的 `xelatex.exe`，编译会失败。

---

## 编译论文

**推荐方式**：在 VSCode 中打开 `paper.tex`，按 `Ctrl+S` 自动触发 LaTeX Workshop 的 `xelatex ×2` 配方。

**命令行方式**：在 Git Bash 终端里：

```bash
cd workspace/2026_XUPT_Campus_MCM
xelatex paper.tex && xelatex paper.tex     # 跑两遍解决交叉引用
```

首次编译时 MiKTeX 会自动联网下载所需宏包（`ctex`、`biblatex-gb7714-2015` 等），耐心等待即可。

---

## 新建一场比赛

1. 在 `workspace/` 下复制现有模板目录，重命名为 `<年份>_<赛事>_<关键词>`，例如 `2026_CUMCM_A`
2. 清空 `paper.tex` 内容占位符，按新题目填写
3. `sections/` 下按需增删章节文件
4. 在该目录下启动 `claude`，用 `/cumcm-master` 进入 AutoMCM-Pro 流程

### 命名约定

- **一场比赛 = 一个子目录**
- 目录名：`<年份>_<赛事简称>_<关键词>`（如 `2026_XUPT_Campus_MCM`、`2026_CUMCM_A`、`2026_MCM_B`）
- LaTeX 引擎固定为 **xelatex**（`ctex` 宏包要求）
- 论文语言：**中文**（国赛 / 校赛 / 研究生赛）

---

## 常见问题

| 现象 | 原因 | 解决 |
|---|---|---|
| `xelatex` 找不到命令 | 没从 `math.code-workspace` 打开 | 关掉当前窗口，双击该文件重新打开 |
| 中文字体缺失 / 宏包找不到 | MiKTeX 首次编译需联网下载 | 保持联网，重新编译即可 |
| PDF 预览空白或不更新 | LaTeX Workshop 缓存 | 手动删除 `.aux .log` 后重编两次 |
| Python 脚本运行报 import 错误 | venv 未激活 | 在 Git Bash 中 `source D:/Tool/math/python-venv/Scripts/activate` |

---

## License

个人比赛作品，转载请联系作者。
