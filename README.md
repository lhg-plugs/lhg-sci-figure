<!-- About 简介（推送后填写到仓库 About 栏）：
学术图表专家：数据→期刊配图规范→图表生成→规范脚本校验，投稿前一次过关 ｜ 一键安装：/plugin marketplace add lhg-plugs/lhg-sci-figure
-->
<!-- topics（推送后打）：claude-code, claude-plugin, agent-skills, scientific-figure, matplotlib, academic, journal -->

# lhg-sci-figure：学术图表专家

> **一句话介绍**：给 AI 写作助手装上"期刊配图流水线"——数据→规范卡→图表生成→18 条确定性规则校验，投稿前把编辑部一眼打回的问题全部提前消灭。
>
> **一键安装**：在 Claude Code 里运行
> ```
> /plugin marketplace add lhg-plugs/lhg-sci-figure
> /plugin install lhg-sci-figure@lhg-plugs
> ```

## 它是什么

`lhg-sci-figure` 是一个 Claude Code 插件（plugin 为主、skill 为辅）：

- **4 个命令**（小白入口）：`figure` 数据→配图主流程，`journal` 期刊规范速查，`revise` 返修迭代，`audit` 配图规范审计
- **4 个平台中立 skill**（方法论，可移植到豆包/Workbuddy 等 agent 平台）：配图规划、视觉规范、图型选型、投稿前自查
- **2 个专家 agent**：图表构建、配图审计
- **2 个硬门 hooks**：commit 前配图审计拦截、绘图脚本写入提醒（均可一键豁免）
- **18 条确定性审计规则**：DPI/字体/线宽/色彩模式/子图编号/图例全覆盖，纯 Python、零第三方依赖

## 4 个命令用法

| 命令 | 作用 | 示例 |
|---|---|---|
| `/lhg-sci-figure:figure` | 数据→规范卡→图表生成→校验，一次产出可投的配图 | `/lhg-sci-figure:figure data.csv Nature` |
| `/lhg-sci-figure:journal` | 期刊配图规范预设速查（栏宽/DPI/字体/色彩模式） | `/lhg-sci-figure:journal IEEE` |
| `/lhg-sci-figure:revise` | 按审稿意见逐条改图，改前改后留档对照 | `/lhg-sci-figure:revise "审稿人要求补误差棒"` |
| `/lhg-sci-figure:audit` | 配图规范审计（脚本 + 人工评审清单） | `/lhg-sci-figure:audit figures/` |

## 自查说明

自查 = 确定性脚本（机器）+ 人工评审清单（人）：

1. 先跑 `scripts/audit/figure_audit.py`（18 条规则），零 LLM 成本；
2. 发现分三级：**blocker**（DPI 不足/子图跳号/缺图例/缺轴标签，必须修，commit 前 hook 会拦截）、**warning**（修或写豁免理由）、**nit**（顺手修）；
3. 再按 `sci-fig-audit` 第 5 节清单过一遍脚本抓不到的（栏宽下可读性、纵轴截断、误差棒说明、色盲友好）。

blocker 清零才算可投；为清零改规则算作弊，不许。

## 目录结构

```
lhg-sci-figure/
├── .claude-plugin/          # plugin.json（插件清单）+ marketplace.json（本仓即市场）
├── commands/                # 4 个命令：figure / journal / revise / audit
├── skills/                  # 4 个平台中立 skill（plan/style/types/audit）
├── agents/                  # 2 个专家 agent（figure-builder / figure-auditor）
├── hooks/                   # 2 个硬门（commit 前审计拦截 / 绘图脚本写入提醒）+ 豁免说明
├── scripts/audit/           # 18 条确定性审计规则（零第三方依赖）
├── fixtures/                # 冒烟测试用例（坏/好对照）
├── smoke_test.py            # 一键冒烟测试
├── ATTRIBUTION.md           # 灵感来源与许可声明
└── LICENSE                  # MIT
```

## 什么时候用 / 什么时候不用（FAQ）

**什么时候用：**

- 你要投论文/会议，配图总被编辑部以"分辨率不足""字体不符"打回时 → 用 `/lhg-sci-figure:figure` 走完整流程
- 你不知道目标期刊的栏宽/DPI/字体要求时 → `/lhg-sci-figure:journal` 速查
- 审稿人让你改图，你怕改完还有规范问题时 → `/lhg-sci-figure:revise` + `/lhg-sci-figure:audit`
- 你想给课题组立一套"配图必须过审计才能投稿"的纪律时 → 它的 hooks 硬门开箱即用

**什么时候不用：**

- 你只是随手画个探索性分析图自己看 → 直接画，别走投稿流程（skill 里有分流说明）
- 你的图是示意图/机制图（非数据图）→ 本插件的规则面向数据图，示意图规范请自行把握
- 你希望 AI 自由发挥、不接受任何硬门 → 它的 commit 拦截会让你烦（可关，但那就别装它）

## 诚实声明

- 期刊规范预设表是公开投稿指南常用值的汇总，**各期刊要求会更新，投稿前请以目标期刊官网 Author Guidelines 最新版为准**。
- 审计脚本检查的是**绘图脚本**的代码规范，不是渲染后的图片；最终的视觉判断仍需人工完成。
- 本插件不承诺"按此流程必过审"——它消灭的是规范性硬伤，科学内容本身的评审它管不着。

## lhg-plugs 插件矩阵

| 插件 | 一句话 | 安装 |
|---|---|---|
| [lhg-sci-figure](https://github.com/lhg-plugs/lhg-sci-figure) | 学术图表专家：数据→期刊规范→图表生成→规范校验，投稿前一次过关 | `/plugin install lhg-sci-figure@lhg-plugs` |
| [lhg-sop](https://github.com/lhg-plugs/lhg-sop) | SOP沉淀专家：流程访谈→SOP文档→检查清单→版本管理 | `/plugin install lhg-sop@lhg-plugs` |
| [lhg-fullstack](https://github.com/lhg-plugs/lhg-fullstack) | 小白一句话 → 高质量全栈应用 | `/plugin install lhg-fullstack@lhg-plugs` |
| [lhg-thesis](https://github.com/lhg-plugs/lhg-thesis) | 毕业论文助手：开题到盲审的写作流水线 | `/plugin install lhg-thesis@lhg-plugs` |
| [lhg-lit-review](https://github.com/lhg-plugs/lhg-lit-review) | 文献综述专家：框架到引用校验一条龙 | `/plugin install lhg-lit-review@lhg-plugs` |
| *（更多插件见 [lhg-plugs/marketplace](https://github.com/lhg-plugs/marketplace)）* | | |

## 自检与反馈

本插件自带质检：每次使用后可跑 `python3 smoke_test.py` 一键验证（JSON 合法、skill/command/agent 完整性、18 条规则、fixtures 命中、hooks 行为）。

发现 bug 或有改进建议，以 `[QC] <一句话问题>` 为标题提交到 https://github.com/lhg-plugs/lhg-sci-figure/issues，正文写清"复现步骤 → 实际表现 → 期望表现"。

## 出品：刘洪光

本插件由真人出镜 IP「刘洪光」（安徽合肥）出品，归属 [lhg-skills](https://github.com/lhg-skills)。

- GitHub 主页：https://github.com/lhg-skills —— 全部 skill 开源在此，欢迎 star
- 视频号：搜「刘洪光实名上网」
- 微信：lhgsmsw
