# 好用例：规范卡全部落实（目标期刊：通用英文期刊单栏）
# 规范卡 fig01 v1.0：栏宽 89mm / DPI 600 / Arial 7pt / 线宽 1.0pt / RGB / 色盲友好配色
import matplotlib
matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans"]
matplotlib.rcParams["font.size"] = 7
matplotlib.rcParams["axes.linewidth"] = 0.8
matplotlib.rcParams["pdf.fonttype"] = 42  # PDF 嵌入 TrueType 字体

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

np.random.seed(42)  # 固定随机种子，可复现
COLOR_MODE = "RGB"  # 色彩模式声明：在线发表用 RGB，印刷前转 CMYK 并复查颜色

df = pd.read_csv("exp01_data.csv")  # 相对路径
df.to_csv("fig01_plot_data.csv", index=False)  # 绘图数据另存

fig, axes = plt.subplots(1, 2, figsize=(3.5, 1.8))  # 3.5in = 89mm 单栏
x = df["time_min"].to_numpy()

axes[0].plot(x, df["control"], label="对照组", color="#0072B2",
             linewidth=1.0, marker="o", markersize=3)
axes[0].plot(x, df["treated"], label="实验组", color="#E69F00",
             linewidth=1.0, linestyle="--", marker="s", markersize=3)
axes[0].set_xlabel("时间（min）")
axes[0].set_ylabel("浓度（μM）")
axes[0].legend(frameon=False, fontsize=7)
axes[0].tick_params(direction="in", length=3)
axes[0].grid(True, alpha=0.3, linewidth=0.5)
axes[0].text(0.05, 0.92, "(a)", transform=axes[0].transAxes,
             fontsize=8, fontweight="bold")

axes[1].bar(["A", "B", "C"], [3.1, 5.2, 4.0], color="#0072B2",
            yerr=[0.3, 0.4, 0.3], capsize=2, error_kw={"linewidth": 1.0})
axes[1].set_xlabel("组别（n=30）")
axes[1].set_ylabel("均值 ± 标准误")
axes[1].tick_params(direction="in", length=3)
axes[1].text(0.05, 0.92, "(b)", transform=axes[1].transAxes,
             fontsize=8, fontweight="bold")

fig.tight_layout(pad=0.5)
fig.savefig("fig01.pdf")              # 矢量主件
fig.savefig("fig01.png", dpi=600)     # 高清位图
