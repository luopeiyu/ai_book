import random

def simulate_one(max_steps=200):
    x, y = 1, 1
    for step in range(max_steps):
        # 随机走一步
        dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        new_x, new_y = x + dx, y + dy
        
        # 检查是否超出20*20格子范围
        if 0 <= new_x < 20 and 0 <= new_y < 20:
            x, y = new_x, new_y
        # 如果超出范围，则行动无效，位置不变
        
        # 检查是否到达终点
        if (x, y) == (18, 18):
            return True,step
    return False,step

def monte_carlo(trials=1_000_00, max_steps=200):
    success = 0
    total_steps = 0
    while total_steps < trials:
        isok, step =  simulate_one(max_steps)
        if isok:
            success += 1
        total_steps += step
    return success, success / total_steps,

if __name__ == "__main__":
    trials = 500000
    success, prob, = monte_carlo(trials)
    print(f"模拟次数: {trials}, 成功概率: {prob*100:.5f}%")
    print(f"成功次数: {success}")