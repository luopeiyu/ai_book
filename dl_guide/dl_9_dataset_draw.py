import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Rectangle
import numpy as np
import random


def _ensure_chinese_font():
    plt.rcParams['font.sans-serif'] = [
        'Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'Noto Sans CJK SC', 'Noto Sans CJK'
    ] + plt.rcParams.get('font.sans-serif', [])
    plt.rcParams['axes.unicode_minus'] = False


def draw_dataloader_concept(outfile_path=None, *, 
                           batch_size=10, num_batches=3, 
                           total_samples=100):
    """绘制DataLoader批处理概念示意图"""
    _ensure_chinese_font()
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # 设置颜色
    sample_color = "#3498db"  # 蓝色代表样本
    batch_color = "#e74c3c"  # 红色代表批次边框
    text_color = "#2c3e50"   # 深色文字
    
    # 绘制完整数据集区域
    dataset_x, dataset_y = 1, 7
    dataset_width, dataset_height = 12, 2.5
    
    # 数据集背景框
    dataset_rect = Rectangle((dataset_x, dataset_y), dataset_width, dataset_height,
                           linewidth=2, edgecolor="#34495e", facecolor="#ecf0f1", alpha=0.3)
    ax.add_patch(dataset_rect)
    
    # 在数据集中绘制所有样本的小点
    samples_per_row = 20
    sample_radius = 0.05
    for i in range(total_samples):
        row = i // samples_per_row
        col = i % samples_per_row
        x = dataset_x + 0.3 + col * 0.55
        y = dataset_y + 0.3 + row * 0.4
        if x < dataset_x + dataset_width - 0.3 and y < dataset_y + dataset_height - 0.3:
            sample = Circle((x, y), radius=sample_radius, 
                          facecolor=sample_color, edgecolor="none", alpha=0.7)
            ax.add_patch(sample)
    
    # 数据集标题
    ax.text(dataset_x + dataset_width/2, dataset_y + dataset_height + 0.3, 
            f'完整数据集 ({total_samples}个样本)', 
            ha='center', va='bottom', fontsize=16, fontweight='bold', color=text_color)
    
    # 绘制箭头指向批次处理
    arrow_start_y = dataset_y - 0.3
    arrow_end_y = 5.5
    ax.annotate('', xy=(7, arrow_end_y), xytext=(7, arrow_start_y),
                arrowprops=dict(arrowstyle='->', lw=2, color=text_color))
    
    # DataLoader处理说明
    ax.text(7, (arrow_start_y + arrow_end_y)/2 + 0.3, 'DataLoader\n批量处理', 
            ha='center', va='center', fontsize=14, fontweight='bold', color=text_color,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=text_color))
    
    # 绘制批次
    batch_y = 3.5
    batch_width = 3.5
    batch_height = 1.8
    batch_spacing = 4.2
    
    for batch_idx in range(num_batches):
        batch_x = 1 + batch_idx * batch_spacing
        
        # 批次边框
        batch_rect = Rectangle((batch_x, batch_y), batch_width, batch_height,
                             linewidth=3, edgecolor=batch_color, facecolor="white", alpha=0.9)
        ax.add_patch(batch_rect)
        
        # 批次标题
        ax.text(batch_x + batch_width/2, batch_y + batch_height + 0.2, 
                f'Batch {batch_idx + 1}', 
                ha='center', va='bottom', fontsize=14, fontweight='bold', color=batch_color)
        
        # 在批次中绘制样本
        samples_in_batch = []
        for i in range(batch_size):
            row = i // 5  # 每行5个样本
            col = i % 5
            x = batch_x + 0.3 + col * 0.6
            y = batch_y + 0.3 + row * 0.6
            
            # 随机生成样本ID
            sample_id = random.randint(1, total_samples)
            samples_in_batch.append(sample_id)
            
            # 绘制样本圆圈
            sample = Circle((x, y), radius=0.15, 
                          facecolor=sample_color, edgecolor="white", linewidth=1.5)
            ax.add_patch(sample)
            
            # 在圆圈中显示样本编号
            ax.text(x, y, str(sample_id), ha='center', va='center', 
                   fontsize=8, color="white", fontweight='bold')
        
        # 批次大小说明
        ax.text(batch_x + batch_width/2, batch_y - 0.3, 
                f'batch_size={batch_size}', 
                ha='center', va='top', fontsize=12, color=text_color)
    
    # 添加特征说明区域
    feature_y = 1.5
    ax.text(7, feature_y + 0.8, '每个样本包含的特征:', 
            ha='center', va='center', fontsize=14, fontweight='bold', color=text_color)
    
    # 特征列表
    features = ['等级 (level)', '攻击力 (attack)', '生命值 (hp)', 
                '防御力 (defense)', '暴击率 (crit_rate)']
    
    for i, feature in enumerate(features):
        ax.text(4 + (i % 3) * 3, feature_y - 0.3 - (i // 3) * 0.4, 
                f'• {feature}', ha='left', va='center', fontsize=11, color=text_color)
    
    # 添加说明文字
    explanation_text = """DataLoader的作用：
1. 将大型数据集分割成小批次(batches)
2. 每个批次包含固定数量的样本
3. 支持数据混洗(shuffle)提高训练效果
4. 充分利用GPU并行计算能力"""
    
    ax.text(1, 0.5, explanation_text, ha='left', va='top', fontsize=12, color=text_color,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8f9fa", edgecolor="#dee2e6"))
    
    # 设置图形属性
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10.5)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # 添加标题
    plt.suptitle('PyTorch DataLoader 批处理机制示意图', 
                fontsize=18, fontweight='bold', color=text_color, y=0.95)
    
    # 保存图片
    if outfile_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        outfile_path = os.path.join(base_dir, 'fig_dl_9_dataloader.png')
    
    plt.tight_layout()
    # plt.savefig(outfile_path, dpi=300, bbox_inches='tight')
    plt.show()
    plt.close(fig)
    return outfile_path


def draw_batch_processing_flow(outfile_path=None):
    """绘制批处理训练流程图"""
    _ensure_chinese_font()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 颜色定义
    input_color = "#3498db"
    process_color = "#e67e22" 
    output_color = "#27ae60"
    text_color = "#2c3e50"
    
    # 绘制流程步骤
    steps = [
        ("输入批次\n[batch_size, 5]", input_color, 2, 6),
        ("神经网络\n前向传播", process_color, 6, 6),
        ("预测输出\n[batch_size, 1]", output_color, 10, 6),
        ("计算损失\nMSE Loss", process_color, 6, 4),
        ("反向传播\n计算梯度", process_color, 6, 2),
        ("更新参数\nOptimizer", process_color, 10, 2)
    ]
    
    # 绘制步骤框和文字
    for text, color, x, y in steps:
        rect = Rectangle((x-0.8, y-0.5), 1.6, 1, 
                        linewidth=2, edgecolor=color, facecolor="white")
        ax.add_patch(rect)
        ax.text(x, y, text, ha='center', va='center', 
               fontsize=11, fontweight='bold', color=text_color)
    
    # 绘制箭头连接
    arrows = [
        ((2.8, 6), (5.2, 6)),    # 输入到网络
        ((6.8, 6), (9.2, 6)),    # 网络到输出
        ((6, 5.5), (6, 4.5)),    # 输出到损失
        ((6, 3.5), (6, 2.5)),    # 损失到反向传播
        ((6.8, 2), (9.2, 2)),    # 反向传播到更新
    ]
    
    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='->', lw=2, color=text_color))
    
    # 添加批次大小说明
    batch_info = """批次处理的优势：
• 并行计算：GPU可同时处理多个样本
• 梯度稳定：基于多样本的平均梯度更新
• 内存效率：避免一次加载全部数据
• 训练稳定：减少单样本噪声影响"""
    
    ax.text(1, 1, batch_info, ha='left', va='top', fontsize=11, color=text_color,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor="#dee2e6"))
    
    # 设置图形属性
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.suptitle('批处理训练流程', fontsize=16, fontweight='bold', color=text_color)
    
    # 保存图片
    if outfile_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        outfile_path = os.path.join(base_dir, 'fig_dl_9_batch_flow.png')
    
    plt.tight_layout()
    # plt.savefig(outfile_path, dpi=300, bbox_inches='tight')
    plt.show()
    plt.close(fig)
    return outfile_path


if __name__ == '__main__':
    # 绘制DataLoader概念图
    path1 = draw_dataloader_concept()
    print(f'DataLoader概念图已保存: {path1}')
    
    # 绘制批处理流程图
    path2 = draw_batch_processing_flow()
    print(f'批处理流程图已保存: {path2}')
