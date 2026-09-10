import random


board = [
    [0, 1, 2, 3, 4, 0],
    [1, 2, 3, 4, 0, 1],
    [2, 3, 4, 0, 1, 2],
    [3, 4, 0, 1, 2, 3],
    [4, 1, 1, 2, 3, 4],
    [0, 1, 2, 3, 4, 0],
]

board2 = [
    [0, 0, 0, 0, 0, 0],
    [0, 0, 3, 2, 2, 0],
    [3, 3, 0, 0, 0, 2],
    [0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [1, 1, 0, 1, 1, 0],
]



# 整理后的棋盘定义，注意每一行用逗号分隔
board = [
    [1, 4, 1, 4, 2, 4],
    [3, 1, 4, 2, 4, 3],
    [1, 1, 3, 1, 2, 4],
    [1, 3, 3, 1, 4, 3],
    [3, 1, 4, 2, 4, 4],
    [4, 4, 1, 4, 4, 3],
]


def get_radom_board(size=6):
    board = [[random.randint(0, 4) for _ in range(size)] for _ in range(size)]
    return board
        
#board = get_radom_board(6)

# 生成棋盘图片，使用PIL库拼接小图片
from PIL import Image

def gen_board_image(board, img_size=64, img_dir="./"):
    """
    根据board生成棋盘图片，拼接每个格子的图片（0.png~5.png）
    :param board: 6x6的二维数组
    :param img_size: 每个格子的图片大小（像素）
    :param img_dir: 小图片所在目录
    :return: PIL.Image对象
    """
    rows = len(board)
    cols = len(board[0]) if rows > 0 else 0
    board_img = Image.new("RGBA", (cols * img_size, rows * img_size), (255, 255, 255, 0))
    for y in range(rows):
        for x in range(cols):
            v = board[y][x]
            img_path = f"{img_dir}{v}.png"
            try:
                gem_img = Image.open(img_path).resize((img_size, img_size))
            except Exception as e:
                # 如果图片不存在，用纯色代替
                color_map = [
                    (200, 200, 200), # 0
                    (255, 0, 0),     # 1
                    (0, 255, 0),     # 2
                    (0, 0, 255),     # 3
                    (255, 255, 0),   # 4
                    (0, 255, 255),   # 5
                ]
                color = color_map[v % len(color_map)]
                gem_img = Image.new("RGB", (img_size, img_size), color)
            board_img.paste(gem_img, (x * img_size, y * img_size))
    return board_img

# 示例用法：生成图片并保存
if __name__ == "__main__":
    img = gen_board_image(board)
    img.save("board_output.png")
    print("棋盘图片已保存为 board_output.png")
