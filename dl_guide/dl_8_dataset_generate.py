
import json
import os
import numpy as np

def generate_data(num_samples=1000):
    # 创建保存数据的文件夹
    output_dir = "player_data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for i in range(num_samples):
        # 为每个玩家生成6个维度的数据
        player_id = f"player_{i+1:04d}"
        
        # 生成基础等级
        level = np.random.randint(1, 101)
        
        # 攻击力：基础值 + 等级加成 + 随机变化
        base_attack = 50 + level * 5 + np.random.normal(0, level * 0.3)
        attack = max(10, int(base_attack))
        
        # 生命值：基础值 + 等级加成 + 随机变化  
        base_hp = 500 + level * 50 + np.random.normal(0, level * 2)
        hp = max(100, int(base_hp))
        
        # 防御力：基础值 + 等级加成 + 随机变化
        base_defense = 20 + level * 2 + np.random.normal(0, level * 0.2)
        defense = max(5, int(base_defense))
        
        # 暴击率：基础值 + 等级加成 + 随机变化（百分比，0-100）
        base_crit_rate = 5 + level * 0.3 + np.random.normal(0, 2)
        crit_rate = max(0, min(100, base_crit_rate))  # 限制在0-100之间
        
        # 战斗力计算公式：
        # 战斗力 = 攻击力 * 2.5 + 生命值 * 0.8 + 防御力 * 3.0 + 暴击率 * 10
        combat_power = int(attack * 2.5 + hp * 0.8 + defense * 3.0 + crit_rate * 10)
        combat_power += np.random.randint(-10, 10)
        combat_power = int(combat_power/1.5)
        
        # 生成其他相关属性
        player_data = {
            "player_id": player_id,
            "level": int(level),
            "attack": attack,
            "hp": hp,
            "defense": defense,
            "crit_rate": int(crit_rate),
            "combat_power": combat_power
        }
        
        # 保存每个玩家的数据到单独的JSON文件
        filename = os.path.join(output_dir, f"{player_id}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(player_data, f, ensure_ascii=False, indent=2)
    
    print(f"已生成 {num_samples} 个玩家数据文件，保存在 {output_dir} 文件夹中")

if __name__ == "__main__":
    generate_data(200)
