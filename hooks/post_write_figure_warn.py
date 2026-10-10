#!/usr/bin/env python3
"""lhg-sci-figure 硬门②：写入绘图脚本后，提醒跑规范审计 + 检查可复现三件套。

触发：PostToolUse / Write|Edit。只对疑似绘图脚本的文件生效
（文件名含 plot/figure/fig 或内容含 matplotlib/seaborn/plotnine），
其他文件 0 开销直接放行。

逃生方式：LHG_FIG_HOOKS_OFF=1（单次豁免本次 hook）。

设计原则：只做提醒（additionalContext），不拦截；内部出错 fail-open；
零第三方依赖。
"""

import json
import os
import sys

PLOT_HINTS = ("plot", "figure", "fig", "chart")
PLOT_LIBS = ("matplotlib", "seaborn", "plotnine", "plt.", "sns.")


def main() -> int:
    if os.environ.get("LHG_FIG_HOOKS_OFF") == "1":
        return 0

    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0  # fail-open

    tool_input = payload.get("tool_input", {}) or {}
    path = tool_input.get("file_path", "") or ""
    base = os.path.basename(path).lower()

    if not base.endswith(".py"):
        return 0
    name_hit = any(h in base for h in PLOT_HINTS)
    if not name_hit:
        # 文件名不像绘图脚本：读一点内容再判断，读失败就放行
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                head = fh.read(4000).lower()
        except OSError:
            return 0
        if not any(lib in head for lib in PLOT_LIBS):
            return 0
    # 文件名命中则直接提醒，不再读文件（省 IO）

    msg = (
        "lhg-sci-figure 提醒：检测到绘图脚本 %s。提交前请确认三件事："
        "① 跑一遍配图审计（/lhg-sci-figure:audit）；"
        "② 可复现三件套齐了吗（随机种子 / 数据文件 / 导出矢量PDF+位图）；"
        "③ 参数与规范卡一致（字号/线宽/DPI/配色）。"
        % os.path.basename(path)
    )
    out = {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                 "additionalContext": msg}}
    sys.stdout.write(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
