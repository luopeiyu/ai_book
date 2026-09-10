import json
import os
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

def load_json_data(folder_path):
    """
    加载文件夹中所有JSON文件的数据
    
    Args:
        folder_path: JSON文件所在的文件夹路径
    
    Returns:
        dict: 包含所有属性数据的字典
    """
    data = defaultdict(list)
    
    # 遍历文件夹中的所有JSON文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    player_data = json.load(f)
                    
                # 提取数值属性（排除player_id）
                for key, value in player_data.items():
                    if key != 'player_id' and key != 'combat_power' and isinstance(value, (int, float)):
                        data[key].append(value)
            except Exception as e:
                print(f"读取文件 {filename} 时出错: {e}")
                continue
    
    return data

def plot_histograms(data, title="玩家属性数据分布"):
    """
    绘制各属性的直方图
    
    Args:
        data: 包含各属性数据的字典
        title: 图表标题
    """
    # 计算子图布局
    num_attributes = len(data)
    if num_attributes == 0:
        print("没有找到有效的数据")
        return
    
    # 计算行列数
    cols = 3 if num_attributes > 3 else num_attributes
    rows = (num_attributes + cols - 1) // cols
    
    # 创建子图
    fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    # 如果只有一行，确保axes是数组
    if rows == 1 and cols == 1:
        axes = [axes]
    elif rows == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 属性名称映射（用于更好的显示）
    attribute_names = {
        'level': '等级',
        'attack': '攻击力',
        'hp': '生命值',
        'defense': '防御力',
        'crit_rate': '暴击率',
        'combat_power': '战斗力'
    }
    
    # 为每个属性绘制直方图
    for i, (attr, values) in enumerate(data.items()):
        if i >= len(axes):
            break
            
        ax = axes[i]
        
        # 计算统计信息
        mean_val = np.mean(values)
        std_val = np.std(values)
        min_val = np.min(values)
        max_val = np.max(values)
        
        # 绘制直方图
        n_bins = min(30, len(set(values)))  # 动态调整bins数量
        n, bins, patches = ax.hist(values, bins=n_bins, alpha=0.7, color='skyblue', edgecolor='black')
        
        # 设置标题和标签
        display_name = attribute_names.get(attr, attr)
        ax.set_title(f'{display_name}分布', fontweight='bold')
        ax.set_xlabel(display_name)
        #ax.set_ylabel('频次')
        ax.set_yticks([])
        
        # 添加统计信息
        #stats_text = f'样本数: {len(values)}\n均值: {mean_val:.1f}\n标准差: {std_val:.1f}\n范围: {min_val}-{max_val}'
        #ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
        #        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # 添加均值线
        #ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'均值: {mean_val:.1f}')
        #ax.legend()
        
        # 网格
        ax.grid(True, alpha=0.3)
    
    # 隐藏多余的子图
    for i in range(len(data), len(axes)):
        axes[i].set_visible(False)
    
    # 调整布局
    plt.tight_layout()
    plt.show()

def print_summary_statistics(data):
    """
    打印数据的汇总统计信息
    
    Args:
        data: 包含各属性数据的字典
    """
    print("=" * 60)
    print("数据汇总统计")
    print("=" * 60)
    
    attribute_names = {
        'level': '等级',
        'attack': '攻击力',
        'hp': '生命值',
        'defense': '防御力',
        'crit_rate': '暴击率',
        'combat_power': '战斗力'
    }
    
    for attr, values in data.items():
        display_name = attribute_names.get(attr, attr)
        print(f"\n{display_name} ({attr}):")
        print(f"  样本数量: {len(values)}")
        print(f"  均值: {np.mean(values):.2f}")
        print(f"  中位数: {np.median(values):.2f}")
        print(f"  标准差: {np.std(values):.2f}")
        print(f"  最小值: {np.min(values)}")
        print(f"  最大值: {np.max(values)}")
        print(f"  25%分位数: {np.percentile(values, 25):.2f}")
        print(f"  75%分位数: {np.percentile(values, 75):.2f}")

def main(folder_path="player_data_train"):
    """
    主函数
    
    Args:
        folder_path: JSON文件所在的文件夹路径
    """
    print(f"开始分析文件夹: {folder_path}")
    
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"错误: 文件夹 '{folder_path}' 不存在")
        return
    
    # 加载数据
    data = load_json_data(folder_path)
    
    if not data:
        print("没有找到有效的JSON数据文件")
        return
    
    print(f"成功加载 {len(next(iter(data.values())))} 个玩家数据")
    
    # 打印统计信息
    # print_summary_statistics(data)
    
    # 绘制直方图
    plot_histograms(data, f"玩家属性数据分布 - {folder_path}")

if __name__ == "__main__":
    # 默认使用当前目录下的player_data_train文件夹
    # 你也可以修改这里的路径，或者通过命令行参数传入
    main("player_data_train")
