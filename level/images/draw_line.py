
import numpy as np
import matplotlib.pyplot as plt

# 设置matplotlib支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False    # 正常显示负号

# 横坐标：moves_diff，范围0到target_moves
target_moves = 8
moves_diff = np.linspace(0, 12, 200)

# 没有平方的reward
moves_reward_linear = np.maximum(0, 1.0 - moves_diff / target_moves)
# 有平方的reward
moves_reward_square = moves_reward_linear ** 2

plt.figure(figsize=(8, 5))
plt.plot(moves_diff, moves_reward_linear, label="moves_reward（无平方）", linestyle='--')
plt.plot(moves_diff, moves_reward_square, label="moves_reward（平方）", linestyle='-')
plt.xlabel("步数差（moves_diff）")
plt.ylabel("步数奖励（moves_reward）")
plt.title("步数奖励对比：线性与平方（设target_moves=8）")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
