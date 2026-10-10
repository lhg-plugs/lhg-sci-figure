# 坏用例 2：坐标轴无单位 + 画布超宽
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial"]

fig, ax = plt.subplots(figsize=(9.0, 4.0))  # 宽度 9.0in > 7.5in，超双栏宽
x = np.arange(5)
ax.bar(x, [3, 5, 2, 6, 4])
ax.set_xlabel("时间")      # 无单位
ax.set_ylabel("浓度")      # 无单位
ax.legend()               # 避免 LEG 误报（本文件只测 UNT/SIZ/VEC）
fig.savefig("fig02.png", dpi=600)  # 只有位图、无矢量主件
