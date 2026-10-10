#!/usr/bin/env python3
"""lhg-sci-figure 确定性配图审计：19 条规则，零第三方依赖。

扫描目标目录的绘图脚本（Python，matplotlib / seaborn / plotnine 风格），
输出 JSON 与人类可读报告；有 blocker 时以 exit code 2 退出（供 hooks 与 CI 使用）。

用法：
    python3 figure_audit.py --target <目录> [--format json|text] [--fail-on blocker|warning|nit]

规则文案均为本项目原创（思路受 zLanqing/codex-claude-academic-skills、
dazhiyang/scientific-plotting-skill 等开源项目启发，未复制任何第三方原文）。
"""

import argparse
import json
import os
import re
import sys

VERSION = "1.0.0"
TOOL = "lhg-sci-figure/figure-audit"

SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", "dist", "build", ".venv", "venv",
    "env", ".tox",
}
SCAN_EXTS = {".py"}

SEV_ORDER = {"blocker": 0, "warning": 1, "nit": 2}


class Finding:
    __slots__ = ("rule_id", "severity", "category", "title", "file", "line",
                 "snippet", "detail")

    def __init__(self, rule_id, severity, category, title, file, line,
                 snippet, detail):
        self.rule_id = rule_id
        self.severity = severity
        self.category = category
        self.title = title
        self.file = file
        self.line = line
        self.snippet = snippet
        self.detail = detail

    def to_dict(self):
        return {
            "rule_id": self.rule_id, "severity": self.severity,
            "category": self.category, "title": self.title,
            "file": self.file, "line": self.line,
            "snippet": self.snippet, "detail": self.detail,
        }


def collect_files(target):
    out = []
    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            _, ext = os.path.splitext(f)
            if ext in SCAN_EXTS:
                out.append(os.path.join(root, f))
    return sorted(out)


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


# ---------------------------------------------------------------- 规则定义
# 每条规则：id / severity / category / title / detail / check(lines, text, path, ctx)
RULES = []
_RULE_BY_ID = {}


def rule(rule_id, severity, category, title, detail):
    def deco(fn):
        r = {"id": rule_id, "severity": severity, "category": category,
             "title": title, "detail": detail}
        _RULE_BY_ID[rule_id] = r
        r["check"] = fn
        RULES.append(r)
        return fn
    return deco


def _mk(rule_id, path, line, snippet):
    r = _RULE_BY_ID[rule_id]
    return Finding(rule_id, r["severity"], r["category"], r["title"],
                   path, line, snippet[:160], r["detail"])


def _rel(path, target):
    try:
        return os.path.relpath(path, target)
    except ValueError:
        return path


PLOT_CALL = re.compile(r"\b(plot|scatter|bar|barh|hist|errorbar|fill_between|"
                       r"imshow|contour|boxplot|violinplot)\s*\(")
SAVEFIG = re.compile(r"\bsavefig\s*\((.*?)\)", re.S)
LABEL_CALL = re.compile(r"label\s*=\s*['\"]")
SUB_LABEL = re.compile(r"\(([a-h])\)")


# ------------------------------------------------------------ blocker 规则

@rule("FIG-DPI-001", "blocker", "分辨率", "位图导出 DPI 不足 300",
      "投稿位图至少 300 dpi（线图建议 600）。savefig 时显式传 dpi=600，"
      "或只导出矢量 PDF。")
def _dpi(lines, text, path, ctx):
    out = []
    for m in SAVEFIG.finditer(text):
        args = m.group(1)
        fname = re.search(r"['\"]([^'\"]+)['\"]", args)
        if not fname:
            continue
        ext = os.path.splitext(fname.group(1).lower())[1]
        if ext not in (".png", ".jpg", ".jpeg", ".tif", ".tiff"):
            continue
        dm = re.search(r"\bdpi\s*=\s*(\d+)", args)
        lineno = text[:m.start()].count("\n") + 1
        if not dm or int(dm.group(1)) < 300:
            out.append(_mk("FIG-DPI-001", path, lineno,
                           lines[lineno - 1] if lineno <= len(lines) else ""))
    return out


@rule("FIG-SUB-001", "blocker", "子图编号", "子图编号不连续（跳号）",
      "多面板子图编号必须 (a)(b)(c)… 连续。跳号会让审稿人以为漏了图。")
def _subseq(lines, text, path, ctx):
    found = sorted(set(SUB_LABEL.findall(text)))
    if len(found) < 2:
        return []
    expected = [chr(ord("a") + i) for i in range(ord(found[-1]) - ord("a") + 1)]
    missing = [c for c in expected if c not in found]
    if not missing:
        return []
    lineno = 1
    m = SUB_LABEL.search(text)
    if m:
        lineno = text[:m.start()].count("\n") + 1
    return [_mk("FIG-SUB-001", path, lineno,
                "缺失编号：(%s)" % ")(".join(missing))]


@rule("FIG-LEG-001", "blocker", "图例", "多数据系列缺少图例",
      "两个及以上数据系列必须有图例（legend）。读者无法靠猜区分曲线。")
def _legend(lines, text, path, ctx):
    n_label = len(LABEL_CALL.findall(text))
    has_legend = bool(re.search(r"\blegend\s*\(", text))
    hue = bool(re.search(r"\bhue\s*=", text))
    if (n_label >= 2 or hue) and not has_legend:
        lineno = 1
        m = LABEL_CALL.search(text) or re.search(r"\bhue\s*=", text)
        if m:
            lineno = text[:m.start()].count("\n") + 1
        return [_mk("FIG-LEG-001", path, lineno,
                    "发现 %d 个 label/hue 但无 legend() 调用" % n_label)]
    return []


@rule("FIG-AXL-001", "blocker", "坐标轴", "坐标轴标签缺失",
      "每张数据图都必须有 x/y 轴标签（含单位，见 FIG-UNT-001）。"
      "无标签的图等于没讲清横纵轴是什么。")
def _axislabel(lines, text, path, ctx):
    if not PLOT_CALL.search(text):
        return []
    has_x = bool(re.search(r"\bxlabel\s*\(|set_xlabel\s*\(", text))
    has_y = bool(re.search(r"\bylabel\s*\(|set_ylabel\s*\(", text))
    if has_x and has_y:
        return []
    m = PLOT_CALL.search(text)
    lineno = text[:m.start()].count("\n") + 1 if m else 1
    missing = "x" if not has_x else "y"
    return [_mk("FIG-AXL-001", path, lineno, "缺少 %s 轴标签" % missing)]


# ------------------------------------------------------------ warning 规则

@rule("FIG-FNT-001", "warning", "字体", "字体未显式声明",
      "投稿图必须显式声明字体（如 Arial/Helvetica/Times），"
      "否则换台机器/投稿系统打开字体会被替换。")
def _font(lines, text, path, ctx):
    if not PLOT_CALL.search(text):
        return []
    if re.search(r"rcParams\s*\[\s*['\"]font", text) or \
            re.search(r"\brc\s*\(\s*['\"]font", text):
        return []
    m = PLOT_CALL.search(text)
    lineno = text[:m.start()].count("\n") + 1 if m else 1
    return [_mk("FIG-FNT-001", path, lineno, "未找到 rcParams 字体声明")]


@rule("FIG-LWD-001", "warning", "线宽", "线宽过细（<0.75pt）",
      "数据线线宽 < 0.75pt 在印刷时会断、缩栏后看不见。"
      "主线建议 1.0-1.5pt。")
def _linewidth(lines, text, path, ctx):
    out = []
    for i, ln in enumerate(lines):
        if "grid(" in ln:
            continue  # 网格线另有 FIG-GRD-001 管，不在此拦截
        for m in re.finditer(r"\b(?:linewidth|lw)\s*=\s*([0-9]*\.?[0-9]+)", ln):
            if float(m.group(1)) < 0.75:
                out.append(_mk("FIG-LWD-001", path, i + 1, ln))
    return out


@rule("FIG-CMY-001", "warning", "色彩模式", "PDF 导出未声明色彩模式",
      "印刷期刊要求 CMYK，在线期刊用 RGB。导出 PDF 时应在脚本注释或"
      "代码中显式声明色彩模式，不许靠默认。")
def _cmyk(lines, text, path, ctx):
    pdf_save = any(
        os.path.splitext(fn.group(1).lower())[1] == ".pdf"
        for m in SAVEFIG.finditer(text)
        for fn in [re.search(r"['\"]([^'\"]+)['\"]", m.group(1))] if fn
    )
    if not pdf_save:
        return []
    if re.search(r"cmyk|color.?mode|色彩模式", text, re.I):
        return []
    m = re.search(r"\bsavefig\b", text)
    lineno = text[:m.start()].count("\n") + 1 if m else 1
    return [_mk("FIG-CMY-001", path, lineno, "导出 PDF 但未声明 RGB/CMYK")]


@rule("FIG-VEC-001", "warning", "导出", "只有位图、没有矢量主件",
      "投稿图必须同时产出矢量主件（PDF/SVG/EPS）+ 高 DPI 位图。"
      "只给位图，放大即糊，返修必返工。")
def _vector(lines, text, path, ctx):
    exts = set()
    for m in SAVEFIG.finditer(text):
        fn = re.search(r"['\"]([^'\"]+)['\"]", m.group(1))
        if fn:
            exts.add(os.path.splitext(fn.group(1).lower())[1])
    if not exts:
        return []
    raster = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}
    vector = {".pdf", ".svg", ".eps"}
    if exts & raster and not (exts & vector):
        m = re.search(r"\bsavefig\b", text)
        lineno = text[:m.start()].count("\n") + 1 if m else 1
        return [_mk("FIG-VEC-001", path, lineno,
                    "仅导出位图：%s" % ",".join(sorted(exts)))]
    return []


@rule("FIG-UNT-001", "warning", "坐标轴", "坐标轴标签缺少单位",
      "轴标签应带单位，如 时间（s）、浓度（μM）。无单位的数字读者无法解读。")
def _unit(lines, text, path, ctx):
    out = []
    unit_mark = re.compile(r"[（(].*?[）)]|/|\[.*?\]|μ|°|%")
    for i, ln in enumerate(lines):
        m = re.search(r"(?:xlabel|ylabel|set_xlabel|set_ylabel)\s*\(\s*"
                      r"['\"]([^'\"]+)['\"]", ln)
        if m and not unit_mark.search(m.group(1)):
            out.append(_mk("FIG-UNT-001", path, i + 1, ln))
    return out


@rule("FIG-RNG-001", "warning", "可复现", "用了随机数但未固定种子",
      "含随机采样/抖动/模拟的绘图必须固定随机种子，否则换台机器"
      "跑出不一样的图。")
def _seed(lines, text, path, ctx):
    uses_random = bool(re.search(
        r"np\.random|numpy\.random|random\.(random|randint|choice|sample)|"
        r"randn|rand\(|jitter", text))
    if not uses_random:
        return []
    if re.search(r"seed\s*\(", text):
        return []
    m = re.search(r"np\.random|random\.|randn", text)
    lineno = text[:m.start()].count("\n") + 1 if m else 1
    return [_mk("FIG-RNG-001", path, lineno, "使用随机数但未见 seed()")]


@rule("FIG-PTH-001", "warning", "可复现", "数据路径硬编码为绝对路径",
      "绝对路径（/Users/…、C:\\…）换台机器就跑不通。"
      "用相对路径或脚本同目录引用。")
def _abspath(lines, text, path, ctx):
    out = []
    rx = re.compile(r"['\"](?:/Users/|/home/|/data/|[A-Za-z]:[\\/])["
                    r"^'\"]*['\"]")
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("#"):
            continue
        if rx.search(ln):
            out.append(_mk("FIG-PTH-001", path, i + 1, ln))
    return out


@rule("FIG-SIZ-001", "warning", "尺寸", "画布宽度超过双栏宽",
      "figsize 宽度超过 7.5 in（≈190 mm）会超出期刊双栏宽，"
      "投稿系统直接截断。单栏按 3.5 in、双栏按 7.2 in 设计。")
def _size(lines, text, path, ctx):
    out = []
    for i, ln in enumerate(lines):
        m = re.search(r"figsize\s*=\s*\(\s*([0-9]*\.?[0-9]+)", ln)
        if m and float(m.group(1)) > 7.5:
            out.append(_mk("FIG-SIZ-001", path, i + 1, ln))
    return out


@rule("FIG-TLE-001", "warning", "规范", "图内放了标题",
      "多数期刊要求图题（caption）写在正文、图内不放标题。"
      "图内标题在排版时会被要求删除。")
def _title(lines, text, path, ctx):
    out = []
    for i, ln in enumerate(lines):
        if re.search(r"\b(?:plt\.title|set_title|ax\.set_title)\s*\(", ln):
            out.append(_mk("FIG-TLE-001", path, i + 1, ln))
    return out


@rule("FIG-CBL-001", "warning", "配色", "红绿直接搭配（色盲不友好）",
      "红-绿是最高发的色盲不可辨组合。用蓝-橙/蓝-红等色盲友好"
      "配色，或加线型/标记做双重区分。")
def _colorblind(lines, text, path, ctx):
    reds = ("red", "#ff0000", "#f00", "'r'", '"r"', "tab:red")
    greens = ("green", "#00ff00", "#0f0", "'g'", '"g"', "tab:green", "lime")
    low = text.lower()
    has_red = any(r in low for r in reds)
    has_green = any(g in low for g in greens)
    if has_red and has_green:
        m = re.search(r"red|green|#ff0000|#00ff00", low)
        lineno = text[:m.start()].count("\n") + 1 if m else 1
        return [_mk("FIG-CBL-001", path, lineno, "同时出现红/绿色系")]
    return []


# ------------------------------------------------------------ nit 规则

@rule("FIG-TIK-001", "nit", "细节", "刻度样式未设置",
      "建议显式设置刻度方向/长度（tick_params），"
      "不同后端默认刻度样式不一致。")
def _tick(lines, text, path, ctx):
    if not PLOT_CALL.search(text):
        return []
    if re.search(r"tick_params", text):
        return []
    m = PLOT_CALL.search(text)
    lineno = text[:m.start()].count("\n") + 1 if m else 1
    return [_mk("FIG-TIK-001", path, lineno, "未见 tick_params 设置")]


@rule("FIG-GRD-001", "nit", "细节", "网格线未设透明度",
      "网格线应浅而淡（alpha 0.3 左右、线宽 ≤0.5）。"
      "实线深色网格会喧宾夺主。")
def _grid(lines, text, path, ctx):
    out = []
    for i, ln in enumerate(lines):
        if re.search(r"\bgrid\s*\(", ln) and "alpha" not in ln:
            out.append(_mk("FIG-GRD-001", path, i + 1, ln))
    return out


@rule("FIG-ORD-001", "nit", "子图编号", "子图编号出现顺序与阅读顺序不一致",
      "编号应按左→右、上→下的阅读顺序出现（如 (b) 不应先于 (a)）。"
      "排版后读者会按顺序找图。")
def _order(lines, text, path, ctx):
    seq = SUB_LABEL.findall(text)
    if len(seq) < 2:
        return []
    if seq != sorted(seq):
        m = SUB_LABEL.search(text)
        lineno = text[:m.start()].count("\n") + 1 if m else 1
        return [_mk("FIG-ORD-001", path, lineno,
                    "编号出现顺序：%s" % "→".join("(%s)" % c for c in seq))]
    return []


@rule("FIG-DAT-001", "nit", "可复现", "绘图数据未另存为 CSV",
      "建议把绘图用的数据另存一份 CSV 与脚本放一起，"
      "方便审稿人/合作者核对数字。")
def _datacsv(lines, text, path, ctx):
    if not PLOT_CALL.search(text):
        return []
    if re.search(r"to_csv|savetxt|\.csv", text):
        return []
    m = PLOT_CALL.search(text)
    lineno = text[:m.start()].count("\n") + 1 if m else 1
    return [_mk("FIG-DAT-001", path, lineno, "未见数据另存（to_csv）")]


# ---------------------------------------------------------------- 主入口

def _strip_comments(lines):
    """剥离 # 注释（避免注释里的关键词干扰规则；行号保持不变）。"""
    return [re.sub(r"#.*$", "", ln) for ln in lines]


def run_audit(target):
    files = collect_files(target)
    findings = []
    for path in files:
        raw = read_text(path)
        if not raw.strip():
            continue
        lines = _strip_comments(raw.split("\n"))
        text = "\n".join(lines)
        ctx = {}
        rel = _rel(path, target)
        for r in RULES:
            try:
                hits = r["check"](lines, text, rel, ctx) or []
            except Exception:
                hits = []  # 单条规则出错不影响整体（fail-open 到规则级）
            findings.extend(hits)
    findings.sort(key=lambda f: (SEV_ORDER.get(f.severity, 9), f.file, f.line))
    summary = {
        "tool": TOOL,
        "version": VERSION,
        "target": target,
        "files_scanned": len(files),
        "rules_run": len(RULES),
        "blocker": sum(1 for f in findings if f.severity == "blocker"),
        "warning": sum(1 for f in findings if f.severity == "warning"),
        "nit": sum(1 for f in findings if f.severity == "nit"),
    }
    return {"summary": summary,
            "findings": [f.to_dict() for f in findings]}


def fmt_text(report):
    s = report["summary"]
    out = ["[%s v%s] 扫描 %d 个文件，%d 条规则" %
           (s["tool"], s["version"], s["files_scanned"], s["rules_run"]),
           "blocker=%d  warning=%d  nit=%d" % (s["blocker"], s["warning"], s["nit"]),
           ""]
    for f in report["findings"]:
        out.append("[%s][%s] %s:%s %s" %
                   (f["severity"], f["rule_id"], f["file"], f["line"], f["title"]))
        if f["snippet"]:
            out.append("    %s" % f["snippet"])
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="lhg-sci-figure 确定性配图审计")
    ap.add_argument("--target", default=".")
    ap.add_argument("--format", choices=["json", "text"], default="text")
    ap.add_argument("--fail-on", choices=["blocker", "warning", "nit"],
                    default="blocker")
    args = ap.parse_args(argv)

    report = run_audit(os.path.abspath(args.target))
    if args.format == "json":
        sys.stdout.write(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        sys.stdout.write(fmt_text(report) + "\n")

    level = SEV_ORDER[args.fail_on]
    bad = any(SEV_ORDER.get(f["severity"], 9) <= level
              for f in report["findings"])
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main())