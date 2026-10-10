---
description: 配图规范审计：跑确定性脚本 + 人工评审清单，输出 blocker/warning/nit 分级报告。
argument-hint: [图表脚本目录] [--fix]
---

# /lhg-sci-figure:audit —— 配图规范审计

用户输入在 `$ARGUMENTS` 中：`[图表脚本目录] [--fix]`。目录缺省为 `figures/`。

## 流程（加载 sci-fig-audit 全程指导）

### 1. 跑脚本
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audit/figure_audit.py --target <目录> --format text
```
记下 blocker / warning / nit 的数量与明细（含文件、行号、规则说明）。

### 2. 分级与修复
- blocker：逐条修。`--fix` 缺省即自动修（最小改动原则）；修一条用脚本复查一条。
- 修不掉的（如期刊有特殊要求与默认规范冲突）→ 列入"需人工确认"，不许为清零改规则。
- warning：修掉或写豁免理由；nit：顺手修。

### 3. 人工评审
按 sci-fig-audit 第 5 节清单执行脚本抓不到的：
- 图例在缩小到栏宽后是否可读
- 红绿配色等色盲不友好组合
- 子图编号阅读顺序（左→右、上→下）
- 坐标轴单位、有效数字位数是否合理

### 4. 输出报告
按 sci-fig-audit 第 6 节模板输出审计报告，存为 `figures/audit-YYYYMMDD.md`，结论写清"可投 / 不可投"。

## 硬规则
- 有 blocker 就说"可投" → 不许。
- 为清零改脚本规则或阈值 → 这是作弊，不许。
