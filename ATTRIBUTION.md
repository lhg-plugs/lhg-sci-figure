# 灵感来源与致谢（Attribution）

本插件的**方法论灵感**来自以下优秀的开源项目，**所有实现代码、检测规则与文案均为原创**，未复制任何第三方的原文案。

| 项目 | 作者 / 组织 | 许可 | 链接 | 借鉴了什么思路 |
|---|---|---|---|---|
| codex-claude-academic-skills | zLanqing | MIT | https://github.com/zLanqing/codex-claude-academic-skills | `scientific-toolkit-skill` 的"投稿图双导出（高清位图+矢量）"与"轴/单位/图例/线宽/字体/分辨率检查清单"的问题意识；本插件审计规则的分类受其启发，**规则条目全部自研** |
| scientific-plotting-skill | dazhiyang | MIT | https://github.com/dazhiyang/scientific-plotting-skill | "期刊栏宽（85/180mm）+ 单一字号 + 图内无标题 + 色盲友好配色"的硬约束思想；本插件规范卡的参数体系受其启发 |
| academic-figures | sai-tv | MIT | https://github.com/sai-tv/academic-figures | "按目标期刊定制配图规范"的产品思路；本插件 `journal` 命令受其启发 |

## 声明

1. **借鉴思路，实现与文案均为原创**：以上项目的具体文案、规则原文、代码实现均未被复制。本插件的 skill 方法论文案、审计规则、命令流程均为独立撰写。
2. **许可合规**：上述项目均为 MIT 许可，允许在保留声明的前提下进行思路借鉴与二次创作。本文件即为保留声明的一部分。
3. **商标与归属**：各项目名称与作者署名归其各自所有者所有。

## 本插件自身的许可

本插件原创部分采用 MIT 许可（见 `LICENSE` 文件），版权所有：刘洪光（https://github.com/lhg-skills）。
