import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class GridGame():
    def __init__(self, is_render: bool = True):
        self.map = self.create_map()
        self.start_pos = (1, 1)
        self.target_pos = (18, 18)
        self.hero_pos = self.start_pos
        self.step_count = 0
        self.MAX_STEP = 200
        # 渲染相关
        self.is_render = is_render
        if self.is_render:
            self.fig, self.ax = plt.subplots(figsize=(6, 6))
            plt.ion()  # 开启交互模式
        
    def create_map(self):
        """创建地图"""
        grid = np.zeros((20, 20), dtype=np.int32)
        
        # 添加边界墙
        grid[0, :] = 1  # 上边界
        grid[-1, :] = 1  # 下边界
        grid[:, 0] = 1  # 左边界
        grid[:, -1] = 1  # 右边界
        
        # 添加一些内部障碍物
        # 垂直墙
        grid[5:15, 8] = 1
        grid[3:12, 15] = 1
        
        # 水平墙
        grid[8, 3:8] = 1
        grid[12, 10:18] = 1
        
        # L形障碍
        grid[15:18, 5] = 1
        grid[17, 5:10] = 1
        
        return grid

    def action(self, action: int):
        """返回值：是否胜利，是否撞墙，是否时间到失败"""
        next_pos = None
        if action == 0:
            next_pos = (self.hero_pos[0] - 1, self.hero_pos[1])
        elif action == 1:
            next_pos = (self.hero_pos[0] + 1, self.hero_pos[1])
        elif action == 2:
            next_pos = (self.hero_pos[0], self.hero_pos[1] - 1)    
        elif action == 3:
            next_pos = (self.hero_pos[0], self.hero_pos[1] + 1)
            
        self.step_count += 1

        # 检查是否到达终点
        if next_pos == self.target_pos:
            self.hero_pos = next_pos
            return True, False, False
        
        # 检查是否时间到失败
        if self.step_count >= self.MAX_STEP:
            self.hero_pos = next_pos
            return False, False, True
        
        # 检查是否撞墙
        if self.map[next_pos] == 1:
            return False, True, False
        
        # 更新英雄位置
        self.hero_pos = next_pos
        return False, False, False

    def reset(self):
        self.hero_pos = self.start_pos
        self.step_count = 0
        return self.hero_pos

    def render(self):
        if not self.is_render:
            return
        print("当前位置：",self.hero_pos,"步数：",self.step_count)

    def render2(self):
        """图形化渲染游戏界面"""
        if not self.is_render:
            return
            
        self.ax.clear()
        
        # 颜色映射
        colors = {0: 'white', 1: 'black'}  # 0: 空地, 1: 墙
        
        # 绘制网格
        for i in range(self.map.shape[0]):
            for j in range(self.map.shape[1]):
                color = colors[self.map[i, j]]
                rect = patches.Rectangle(
                    (j, self.map.shape[0]-1-i), 1, 1,
                    linewidth=1, edgecolor='gray', facecolor=color
                )
                self.ax.add_patch(rect)
        
        # 绘制起点（绿色）
        start_rect = patches.Rectangle(
            (self.start_pos[1], self.map.shape[0]-1-self.start_pos[0]), 1, 1,
            linewidth=2, edgecolor='green', facecolor='lightgreen'
        )
        self.ax.add_patch(start_rect)
        
        # 绘制终点（红色）
        target_rect = patches.Rectangle(
            (self.target_pos[1], self.map.shape[0]-1-self.target_pos[0]), 1, 1,
            linewidth=2, edgecolor='red', facecolor='lightcoral'
        )
        self.ax.add_patch(target_rect)
        
        # 绘制英雄位置（蓝色）
        hero_rect = patches.Rectangle(
            (self.hero_pos[1], self.map.shape[0]-1-self.hero_pos[0]), 1, 1,
            linewidth=3, edgecolor='blue', facecolor='lightblue'
        )
        self.ax.add_patch(hero_rect)
        
        self.ax.set_xlim(0, self.map.shape[1])
        self.ax.set_ylim(0, self.map.shape[0])
        self.ax.set_aspect('equal')
        self.ax.set_title(f'Grid Game - Steps: {self.step_count}/{self.MAX_STEP}')
        self.ax.grid(True, alpha=0.3)
        
        # 添加图例
        legend_elements = [
            patches.Patch(color='lightgreen', label='Start'),
            patches.Patch(color='lightcoral', label='Target'),
            patches.Patch(color='lightblue', label='Player'),
            patches.Patch(color='black', label='Wall'),
            patches.Patch(color='white', label='Empty')
        ]
        self.ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
        
        plt.tight_layout()
        plt.draw()
        plt.pause(0.1)


    def start(self):
        print("使用wsad控制移动，输入r重新开始，输入q退出")
        
        while True:
            self.render()
            
            # 控制台输入检测
            user_input = input("请输入指令 (w/a/s/d/r/q): ").strip().lower()
            
            action = None
            if user_input == 'w':
                action = 0
            elif user_input == 's':
                action = 1
            elif user_input == 'a':
                action = 2
            elif user_input == 'd':
                action = 3
            elif user_input == 'r':
                self.reset()
                continue
            elif user_input == 'q':
                break
            
            # 如果有动作执行
            if action is not None:
                win, hit_wall, time_up = self.action(action)
                
                if win:
                    print("YOU WIN")
                elif hit_wall:
                    print("HIT WALL")
                elif time_up:
                    print("GAME OVER")
        


if __name__ == "__main__":
    game = GridGame()
    game.start()

