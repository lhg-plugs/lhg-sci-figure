---
description: 主流程：数据→选期刊规范→生成投稿级图表→跑规范脚本校验，一次产出可投的配图。
argument-hint: <数据文件或需求描述> [目标期刊]
---

# /lhg-sci-figure:figure —— 学术图表主流程

用户输入在 `$ARGUMENTS` 中：`<数据文件或需求描述> [目标期刊]`。目标期刊缺省为"通用英文期刊"。

## 流程（加载 sci-fig-plan / sci-fig-style / sci-fig-types 全程指导）

### 1. 定规范（先定，后画）
- 确认目标期刊（用 `/lhg-sci-figure:journal` 查预设：栏宽/DPI/字体/色彩模式要求）。
- 输出一张"规范卡"：画布尺寸（mm→in）、DPI、字体、线宽、配色、子图编号格式、导出格式。
- **规范卡不确认，不动手画。**

### 2. 选型（数据决定图型）
按 sci-fig-types 的选型表定：比较组→柱/点图、趋势→折线、分布→箱线/小提琴、矩阵→热图、多故事线→多面板。
多面板先出 panel plan（每个子图的图型+数据+编号），用户确认后再画。

### 3. 生成（脚本可复现）
- 绘图脚本存为 `figures/figNN_plot.py`，数据另存 `figures/figNN_data.csv`。
- 脚本头部写清：随机种子、依赖版本、期刊规范卡参数。
- 导出：矢量 PDF（主件）+ 300 DPI PNG（预览/投稿系统上传用）。

### 4. 校验（脚本 + 人工）
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audit/figure_audit.py --target figures/ --format text
```
blocker 必须清零；再按 sci-fig-audit 第 5 节做人工评审（图例可读性、色盲友好、编号顺序）。

## 硬规则
- 无规范卡直接画图 → 不许。
- 只有位图、没有矢量主件 → 不许交付。
- 数据文件硬编码绝对路径 → 不许。
- blocker 未清零就说"投吧" → 不许。
