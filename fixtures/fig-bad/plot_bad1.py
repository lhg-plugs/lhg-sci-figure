# 坏用例 1：多重规范问题（投稿会被打回的典型）
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 50)
y1 = np.sin(x) + np.random.randn(50) * 0.1   # 随机数：无 seed
y2 = np.cos(x) + np.random.randn(50) * 0.1

# 子图编号：跳号（缺 b），且 (c) 先于 (a) 出现
plt.text(0.05, 0.9, "(c) 实验组", transform=plt.gca().transAxes)
plt.plot(x, y1, label="对照组", color="red", linewidth=0.5)     # 线宽过细 + 红色
plt.plot(x, y2, label="实验组", color="green", linewidth=0.5)   # 绿色：红绿直配，且无 legend()
plt.text(0.05, 0.8, "(a) 对照组", transform=plt.gca().transAxes)
# 注意：无 xlabel/ylabel；无 rcParams 字体声明；无 tick_params

data = np.loadtxt("/Users/lhg/data/exp01.csv", delimiter=",")  # 绝对路径硬编码

plt.grid(True)  # 网格无 alpha
plt.title("药物效应曲线")  # 图内标题
plt.savefig("fig01.png", dpi=150)   # DPI 不足
plt.savefig("fig01.pdf")            # 矢量导出：未声明色彩模式
