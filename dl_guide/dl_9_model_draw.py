import os
import matplotlib.pyplot as plt
from matplotlib.patches import Circle


def _ensure_chinese_font():
    plt.rcParams['font.sans-serif'] = [
        'Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'Noto Sans CJK SC', 'Noto Sans CJK'
    ] + plt.rcParams.get('font.sans-serif', [])
    plt.rcParams['axes.unicode_minus'] = False


def _layer_y_positions(num_nodes: int, node_spacing: float, max_visible: int):
    """
    返回：y坐标列表，以及省略号所在y坐标（列表）
    要求：无论节点数是否被折叠显示，整体都以 y=0 为中心对称
    """
    if num_nodes <= max_visible:
        # 完整显示，严格以0为中心
        total = (num_nodes - 1) * node_spacing
        ys = [total / 2 - i * node_spacing for i in range(num_nodes)]
        return ys, []

    # 折叠显示：两头各显示 half 个，中间用“...”表示
    half = max_visible // 2
    gap = 2.0 * node_spacing  # 省略区的可视留白（对称）
    # 上半部分（从高到低），以0为中心对称
    top = [gap / 2 + (half - i - 0.5) * node_spacing for i in range(half)]
    bottom = [-v for v in top]  # 关于0对称
    ys = top + bottom
    return ys, [0.0]


def draw_mlp_schematic(
    layer_sizes, activations, outfile_path=None, *,
    layer_spacing=3.0, node_spacing=0.35, max_visible=12,
    node_radius=0.16, node_color="#F4A259", edge_color="#222222"
):
    _ensure_chinese_font()

    fig_w = layer_spacing * (len(layer_sizes) - 1) + 2.8
    fig_h = max(6, node_spacing * max_visible + 2.8)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    # 每层x坐标
    x_positions = [i * layer_spacing for i in range(len(layer_sizes))]

    # 绘制各层节点（y坐标居中对称）
    layer_node_positions = []
    all_y_values = []
    for li, size in enumerate(layer_sizes):
        ys, ellipsis_y_list = _layer_y_positions(size, node_spacing, max_visible)
        xs = [x_positions[li]] * len(ys)
        layer_node_positions.append(list(zip(xs, ys)))
        all_y_values.extend(ys)
        for (x, y) in layer_node_positions[-1]:
            circ = Circle((x, y), radius=node_radius, facecolor=node_color, edgecolor=edge_color, linewidth=1.2)
            ax.add_patch(circ)
        for ey in ellipsis_y_list:
            ax.text(x_positions[li], ey, '...', ha='center', va='center', fontsize=14, color=edge_color)

    # 连接边
    for li in range(len(layer_sizes) - 1):
        left_nodes = layer_node_positions[li]
        right_nodes = layer_node_positions[li + 1]
        for (x1, y1) in left_nodes:
            for (x2, y2) in right_nodes:
                ax.plot([x1, x2], [y1, y2], color=edge_color, linewidth=0.6, alpha=0.9)

    # 激活函数标注（放在该层顶部略上方）
    for li, act in enumerate(activations):
        if act and li not in (0, len(layer_sizes) - 1) and layer_node_positions[li]:
            top_y = max(y for (_, y) in layer_node_positions[li])
            ax.text(x_positions[li], top_y + 0.9, act, ha='center', va='bottom', fontsize=14)

    # 输入/输出标注，始终在各自层的“可见中线”处
    def _layer_center_y(layer_points):
        if not layer_points:
            return 0.0
        return sum(y for (_, y) in layer_points) / len(layer_points)

    if layer_node_positions[0]:
        y0 = _layer_center_y(layer_node_positions[0])
        ax.annotate('输入', xy=(x_positions[0] - node_radius, y0), xytext=(x_positions[0] - 1.3, y0),
                    textcoords='data', ha='right', va='center', fontsize=13,
                    arrowprops=dict(arrowstyle='->', color=edge_color, lw=1.2))

    if layer_node_positions[-1]:
        yn = _layer_center_y(layer_node_positions[-1])
        ax.text(x_positions[-1] + 0.9, yn, '输出', ha='left', va='center', fontsize=13)

    # 画布范围：基于实际可见节点动态设置，并留安全边距，避免任何元素超出
    ax.set_aspect('equal')
    ax.axis('off')

    y_abs_max = max(0.6, max(abs(y) for y in all_y_values))  # 至少保证一点高度
    y_margin = 1.2
    ax.set_ylim(-y_abs_max - y_margin, y_abs_max + y_margin)

    x_margin_left = 2.0  # 留足“输入”文字与箭头空间
    x_margin_right = 2.0  # 留足“输出”文字空间
    ax.set_xlim(x_positions[0] - x_margin_left, x_positions[-1] + x_margin_right)

    # 不使用 bbox_inches='tight'（防止裁剪注释箭头/文字）
    if outfile_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        outfile_path = os.path.join(base_dir, 'fig_dl_9_model.png')
    plt.tight_layout(pad=0.6)
    # fig.savefig(outfile_path, dpi=300)
    plt.show()
    plt.close(fig)
    return outfile_path


if __name__ == '__main__':
    sizes = [5, 64, 64, 1]
    acts = [None, 'ReLU', 'ReLU', None]
    path = draw_mlp_schematic(sizes, acts)
    print(f'网络结构示意图已保存: {path}')