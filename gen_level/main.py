"""
三消游戏关卡设计系统主程序
整合游戏模拟器、关卡生成器和强化学习系统
"""

import argparse
import os
import sys
import json
from typing import List, Dict, Any
import random
import numpy as np

from match3_game import Match3Game, Move
from level_generator import LevelGenerator, DifficultyLevel, LevelType, LevelConfig
from rl_level_designer import RLLevelDesigner
from match3_env import LevelDesignEnv


class Match3LevelDesignSystem:
    """三消游戏关卡设计系统"""
    
    def __init__(self):
        self.generator = LevelGenerator()
        self.rl_designer = None
        self.current_game = None
        
        print("=== 三消游戏关卡设计系统 ===")
        print("支持功能：")
        print("1. 传统关卡生成")
        print("2. 强化学习关卡设计")
        print("3. 关卡测试和验证")
        print("4. 游戏模拟器")
    
    def demo_game_simulator(self):
        """演示游戏模拟器"""
        print("\n=== 游戏模拟器演示 ===")
        
        game = Match3Game(width=8, height=8, gem_types=6)
        game.set_level_config(target_score=1500, moves_limit=25)
        
        print("初始游戏状态:")
        print(game.get_board_visual())
        
        # 进行几步游戏
        moves_made = 0
        while not game.is_game_over and moves_made < 5:
            valid_moves = game.get_valid_moves()
            if not valid_moves:
                print("没有有效移动，游戏结束")
                break
            
            # 随机选择一个移动
            move = random.choice(valid_moves)
            print(f"\n执行移动: {move.from_pos} -> {move.to_pos}")
            
            state, score_gained, done = game.make_move(move)
            print(f"获得分数: {score_gained}")
            print("游戏状态:")
            print(game.get_board_visual())
            
            moves_made += 1
        
        if game.is_level_completed():
            print("🎉 关卡完成！")
        elif game.moves_left <= 0:
            print("❌ 移动次数用完")
        else:
            print("⏸️ 演示结束")
    
    def demo_traditional_generation(self):
        """演示传统关卡生成"""
        print("\n=== 传统关卡生成演示 ===")
        
        # 生成不同难度的关卡
        difficulties = [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]
        templates = ['standard', 'corner_challenge', 'center_burst']
        
        generated_levels = []
        
        for i, (difficulty, template) in enumerate(zip(difficulties, templates)):
            print(f"\n生成关卡 {i+1}: {difficulty.value} 难度, {template} 模板")
            
            level = self.generator.generate_level(
                difficulty=difficulty,
                template=template,
                level_id=i+1
            )
            
            generated_levels.append(level)
            
            print(f"关卡ID: {level.level_id}")
            print(f"目标分数: {level.target_score}")
            print(f"移动限制: {level.moves_limit}")
            
            # 显示棋盘的一部分
            gem_chars = {0: '.', 1: 'R', 2: 'B', 3: 'G', 4: 'Y', 5: 'P', 6: 'O'}
            print("棋盘预览 (前4行):")
            for row in level.board[:4]:
                print(' '.join(gem_chars.get(gem, '?') for gem in row))
        
        # 保存生成的关卡
        filename = "demo_traditional_levels.json"
        self.generator.save_levels(generated_levels, filename)
        print(f"\n关卡已保存到: {filename}")
        
        return generated_levels
    
    def demo_rl_generation(self, quick_training: bool = True):
        """演示强化学习关卡生成"""
        print("\n=== 强化学习关卡生成演示 ===")
        
        self.rl_designer = RLLevelDesigner(
            log_dir="logs/demo_rl_designer"
        )
        
        # 设置训练参数
        if quick_training:
            total_timesteps = 20000  # 快速演示
            print("🚀 快速训练模式 (20k steps)")
        else:
            total_timesteps = 100000  # 完整训练
            print("🏃 完整训练模式 (100k steps)")
        
        print("开始训练强化学习智能体...")
        
        try:
            # 训练模型
            model = self.rl_designer.train(
                total_timesteps=total_timesteps,
                save_freq=5000,
                eval_freq=2000
            )
            
            print("✅ 训练完成！")
            
            # 评估模型
            print("\n评估模型性能...")
            evaluation = self.rl_designer.evaluate_model(num_episodes=10)
            
            # 生成关卡
            print("\n生成高质量关卡...")
            levels = self.rl_designer.generate_levels(
                num_levels=3,
                quality_threshold=0.5,
                max_attempts=20
            )
            
            if levels:
                print(f"成功生成 {len(levels)} 个关卡")
                
                # 保存关卡
                self.rl_designer.save_generated_levels(levels, "demo_rl_levels.json")
                
                # 显示关卡信息
                for i, level in enumerate(levels):
                    print(f"\nRL关卡 {i+1}:")
                    print(f"  目标分数: {level['target_score']}")
                    print(f"  移动限制: {level['moves_limit']}")
                    print(f"  质量评分: {level['quality_score']:.3f}")
                
                return levels
            else:
                print("❌ 未能生成符合质量要求的关卡")
                return []
                
        except Exception as e:
            print(f"❌ 强化学习训练失败: {e}")
            return []
    
    def test_level(self, level_config: Dict[str, Any], num_tests: int = 5):
        """测试关卡可玩性"""
        print(f"\n=== 测试关卡 (ID: {level_config.get('level_id', 'Unknown')}) ===")
        
        # 创建游戏实例
        board = np.array(level_config['board'])
        target_score = level_config['target_score']
        moves_limit = level_config['moves_limit']
        
        test_results = []
        
        for test_num in range(num_tests):
            game = Match3Game(board.shape[1], board.shape[0], gem_types=6)
            game.board = board.copy()
            game.set_level_config(target_score, moves_limit)
            
            # 随机游戏模拟
            moves_made = 0
            while not game.is_game_over and moves_made < 100:
                valid_moves = game.get_valid_moves()
                if not valid_moves:
                    break
                
                move = random.choice(valid_moves)
                game.make_move(move)
                moves_made += 1
            
            # 记录结果
            test_results.append({
                'completed': game.is_level_completed(),
                'final_score': game.score,
                'moves_used': moves_limit - game.moves_left,
                'progress': game.get_level_progress()
            })
        
        # 分析结果
        completion_rate = sum(1 for r in test_results if r['completed']) / len(test_results)
        avg_score = sum(r['final_score'] for r in test_results) / len(test_results)
        avg_progress = sum(r['progress'] for r in test_results) / len(test_results)
        
        print(f"测试结果 ({num_tests} 次模拟):")
        print(f"  完成率: {completion_rate:.1%}")
        print(f"  平均分数: {avg_score:.0f} / {target_score}")
        print(f"  平均进度: {avg_progress:.1%}")
        
        # 判断关卡质量
        if completion_rate < 0.2:
            quality = "太难"
        elif completion_rate > 0.8:
            quality = "太容易"
        elif 0.3 <= completion_rate <= 0.7:
            quality = "平衡良好"
        else:
            quality = "可接受"
        
        print(f"  关卡评价: {quality}")
        
        return {
            'completion_rate': completion_rate,
            'avg_score': avg_score,
            'avg_progress': avg_progress,
            'quality_assessment': quality
        }
    
    def interactive_game(self):
        """交互式游戏模式"""
        print("\n=== 交互式游戏模式 ===")
        print("你可以手动玩三消游戏！")
        
        # 生成一个简单关卡
        level = self.generator.generate_level(DifficultyLevel.EASY)
        
        game = Match3Game(level.board.shape[1], level.board.shape[0], gem_types=6)
        game.board = level.board.copy()
        game.set_level_config(level.target_score, level.moves_limit)
        
        print(f"关卡目标: {level.target_score} 分")
        print(f"移动限制: {level.moves_limit} 步")
        print("\n当前游戏状态:")
        print(game.get_board_visual())
        
        while not game.is_game_over:
            valid_moves = game.get_valid_moves()
            if not valid_moves:
                print("没有有效移动，游戏结束")
                break
            
            print(f"\n可用移动数: {len(valid_moves)}")
            print("输入移动 (格式: 行1,列1 行2,列2) 或 'q' 退出:")
            print("例如: 2,3 2,4")
            
            user_input = input("> ").strip()
            
            if user_input.lower() == 'q':
                print("退出游戏")
                break
            
            try:
                # 解析用户输入
                parts = user_input.split()
                if len(parts) != 2:
                    print("输入格式错误，请使用: 行1,列1 行2,列2")
                    continue
                
                from_pos = tuple(map(int, parts[0].split(',')))
                to_pos = tuple(map(int, parts[1].split(',')))
                
                move = Move(from_pos, to_pos)
                
                # 检查移动是否有效
                if move not in valid_moves:
                    print("无效移动，请选择有效的移动")
                    continue
                
                # 执行移动
                state, score_gained, done = game.make_move(move)
                
                print(f"获得分数: {score_gained}")
                print("游戏状态:")
                print(game.get_board_visual())
                
            except (ValueError, IndexError):
                print("输入格式错误，请使用: 行1,列1 行2,列2")
                continue
        
        # 游戏结束
        if game.is_level_completed():
            print("🎉 恭喜！你完成了关卡！")
        else:
            print(f"游戏结束。最终分数: {game.score}/{game.target_score}")
    
    def compare_generation_methods(self):
        """比较不同生成方法"""
        print("\n=== 生成方法比较 ===")
        
        # 传统生成
        print("1. 传统算法生成关卡...")
        traditional_levels = []
        for difficulty in [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]:
            level = self.generator.generate_level(difficulty)
            traditional_levels.append(level.to_dict())
        
        # 测试传统关卡
        print("\n传统关卡测试结果:")
        traditional_results = []
        for i, level in enumerate(traditional_levels):
            result = self.test_level(level, num_tests=3)
            traditional_results.append(result)
            print(f"  关卡 {i+1}: {result['quality_assessment']}")
        
        # 如果有RL模型，也进行比较
        if self.rl_designer and os.path.exists("logs/demo_rl_designer/final_model.zip"):
            print("\n2. 强化学习生成关卡...")
            try:
                self.rl_designer.load_model("logs/demo_rl_designer/final_model.zip")
                rl_levels = self.rl_designer.generate_levels(num_levels=3, quality_threshold=0.3)
                
                if rl_levels:
                    print("\n强化学习关卡测试结果:")
                    rl_results = []
                    for i, level in enumerate(rl_levels):
                        result = self.test_level(level, num_tests=3)
                        rl_results.append(result)
                        print(f"  关卡 {i+1}: {result['quality_assessment']}")
                    
                    # 比较结果
                    print("\n=== 方法比较总结 ===")
                    trad_avg_completion = sum(r['completion_rate'] for r in traditional_results) / len(traditional_results)
                    rl_avg_completion = sum(r['completion_rate'] for r in rl_results) / len(rl_results)
                    
                    print(f"传统算法平均完成率: {trad_avg_completion:.1%}")
                    print(f"强化学习平均完成率: {rl_avg_completion:.1%}")
                    
                    if abs(trad_avg_completion - rl_avg_completion) < 0.1:
                        print("两种方法的平衡性相似")
                    elif rl_avg_completion > trad_avg_completion:
                        print("强化学习生成的关卡更加平衡")
                    else:
                        print("传统算法生成的关卡更加平衡")
                else:
                    print("强化学习未能生成关卡")
            except Exception as e:
                print(f"强化学习比较失败: {e}")
        else:
            print("没有可用的强化学习模型进行比较")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="三消游戏关卡设计系统")
    parser.add_argument("--mode", type=str, default="demo",
                       choices=["demo", "train", "generate", "test", "interactive", "compare"],
                       help="运行模式")
    parser.add_argument("--quick", action="store_true",
                       help="快速模式（用于演示）")
    parser.add_argument("--level-file", type=str,
                       help="关卡文件路径")
    
    args = parser.parse_args()
    
    # 设置随机种子
    random.seed(42)
    np.random.seed(42)
    
    system = Match3LevelDesignSystem()
    
    if args.mode == "demo":
        # 完整演示
        print("\n🎮 开始完整系统演示...")
        
        # 1. 游戏模拟器演示
        system.demo_game_simulator()
        
        # 2. 传统生成演示
        traditional_levels = system.demo_traditional_generation()
        
        # 3. 测试传统生成的关卡
        if traditional_levels:
            system.test_level(traditional_levels[0].to_dict())
        
        # 4. 强化学习演示（可选）
        if not args.quick:
            rl_levels = system.demo_rl_generation(quick_training=False)
        else:
            print("\n⚡ 跳过强化学习演示（使用 --quick 模式）")
            print("如需完整演示，请运行: python main.py --mode demo")
    
    elif args.mode == "train":
        # 仅训练强化学习模型
        print("\n🤖 训练强化学习模型...")
        system.demo_rl_generation(quick_training=not args.quick)
    
    elif args.mode == "generate":
        # 仅生成关卡
        print("\n🎯 生成关卡...")
        levels = system.demo_traditional_generation()
        print(f"生成了 {len(levels)} 个关卡")
    
    elif args.mode == "test":
        # 测试关卡
        if args.level_file and os.path.exists(args.level_file):
            print(f"\n🔍 测试关卡文件: {args.level_file}")
            try:
                with open(args.level_file, 'r', encoding='utf-8') as f:
                    levels_data = json.load(f)
                
                if isinstance(levels_data, list):
                    for i, level_data in enumerate(levels_data[:3]):  # 最多测试前3个
                        system.test_level(level_data)
                else:
                    system.test_level(levels_data)
            except Exception as e:
                print(f"❌ 测试失败: {e}")
        else:
            print("❌ 请提供有效的关卡文件路径: --level-file <path>")
    
    elif args.mode == "interactive":
        # 交互式游戏
        system.interactive_game()
    
    elif args.mode == "compare":
        # 比较生成方法
        system.compare_generation_methods()
    
    print("\n✨ 程序运行完毕！")


if __name__ == "__main__":
    main()
