"""
战斗模拟器API接口
"""

from flask import Flask, request, jsonify
from typing import List, Tuple, Dict, Any
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import time
import os
from battle import BattleSimulator
from enums import BattleResult

app = Flask(__name__)

def simulate_single_battle(team1_config: List[Tuple[int, int]], 
                          team2_config: List[Tuple[int, int]]) -> Dict[str, Any]:
    """
    模拟单场战斗的包装函数，用于多进程调用
    """
    try:
        simulator = BattleSimulator()
        result = simulator.simulate_battle(team1_config, team2_config)
        return {
            "success": True,
            "data": result,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": str(e)
        }

def simulate_battle_batch_worker(battle_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    批量战斗的工作进程函数
    """
    results = []
    for config in battle_configs:
        team1_config = config["team1_config"]
        team2_config = config["team2_config"]
        battle_id = config.get("battle_id", 0)
        
        try:
            simulator = BattleSimulator()
            result = simulator.simulate_battle(team1_config, team2_config)
            results.append({
                "battle_id": battle_id,
                "success": True,
                "data": result,
                "error": None
            })
        except Exception as e:
            results.append({
                "battle_id": battle_id,
                "success": False,
                "data": None,
                "error": str(e)
            })
    
    return results

@app.route('/battle/single', methods=['POST'])
def single_battle():
    """
    单场战斗接口
    
    请求格式:
    {
        "team1_config": [[hero_id, skill_id], [hero_id, skill_id], [hero_id, skill_id]],
        "team2_config": [[hero_id, skill_id], [hero_id, skill_id], [hero_id, skill_id]]
    }
    
    返回格式:
    {
        "success": true,
        "data": {
            "winner": "team1_win|team2_win|draw",
            "rounds": 10,
            "team1_stats": [...],
            "team2_stats": [...]
        },
        "error": null,
        "execution_time": 0.123
    }
    """
    try:
        start_time = time.time()
        
        # 验证请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "data": None,
                "error": "请求数据为空",
                "execution_time": 0
            }), 400
        
        team1_config = data.get("team1_config")
        team2_config = data.get("team2_config")
        
        if not team1_config or not team2_config:
            return jsonify({
                "success": False,
                "data": None,
                "error": "缺少队伍配置参数",
                "execution_time": 0
            }), 400
        
        # 验证队伍配置格式
        if len(team1_config) != 3 or len(team2_config) != 3:
            return jsonify({
                "success": False,
                "data": None,
                "error": "每个队伍必须有3个英雄",
                "execution_time": 0
            }), 400
        
        # 转换为元组格式
        team1_tuples = [(int(hero[0]), int(hero[1])) for hero in team1_config]
        team2_tuples = [(int(hero[0]), int(hero[1])) for hero in team2_config]
        
        # 模拟战斗
        simulator = BattleSimulator()
        result = simulator.simulate_battle(team1_tuples, team2_tuples)
        
        execution_time = time.time() - start_time
        
        return jsonify({
            "success": True,
            "data": result,
            "error": None,
            "execution_time": round(execution_time, 3)
        })
        
    except Exception as e:
        execution_time = time.time() - start_time if 'start_time' in locals() else 0
        return jsonify({
            "success": False,
            "data": None,
            "error": f"服务器错误: {str(e)}",
            "execution_time": round(execution_time, 3)
        }), 500

@app.route('/battle/batch', methods=['POST'])
def batch_battle():
    """
    批量战斗接口（多进程）
    
    请求格式:
    {
        "battles": [
            {
                "battle_id": 1,
                "team1_config": [[hero_id, skill_id], ...],
                "team2_config": [[hero_id, skill_id], ...]
            },
            {
                "battle_id": 2,
                "team1_config": [[hero_id, skill_id], ...],
                "team2_config": [[hero_id, skill_id], ...]
            },
            ...
        ],
    }
    
    返回格式:
    {
        "success": true,
        "data": {
            "total_battles": 100,
            "successful_battles": 98,
            "failed_battles": 2,
            "results": [
                {
                    "battle_id": 1,
                    "success": true,
                    "data": {...},
                    "error": null
                },
                ...
            ]
        },
        "error": null,
        "execution_time": 5.678
    }
    """
    try:
        start_time = time.time()
        
        # 验证请求数据
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "data": None,
                "error": "请求数据为空",
                "execution_time": 0
            }), 400

        battles = data.get("battles", [])
        max_workers = 4 # 当前设置为固定值
        
        if not battles:
            return jsonify({
                "success": False,
                "data": None,
                "error": "没有战斗配置",
                "execution_time": 0
            }), 400
        
        if len(battles) > 10000:  # 限制最大批量数量
            return jsonify({
                "success": False,
                "data": None,
                "error": "批量战斗数量不能超过10000场",
                "execution_time": 0
            }), 400
        
        # 验证并转换战斗配置
        processed_battles = []
        for i, battle in enumerate(battles):
            try:
                team1_config = battle.get("team1_config")
                team2_config = battle.get("team2_config")
                battle_id = battle.get("battle_id", i)
                
                if not team1_config or not team2_config:
                    raise ValueError(f"战斗{battle_id}: 缺少队伍配置")
                
                if len(team1_config) != 3 or len(team2_config) != 3:
                    raise ValueError(f"战斗{battle_id}: 每个队伍必须有3个英雄")
                
                # 转换为元组格式
                team1_tuples = [(int(hero[0]), int(hero[1])) for hero in team1_config]
                team2_tuples = [(int(hero[0]), int(hero[1])) for hero in team2_config]
                
                processed_battles.append({
                    "battle_id": battle_id,
                    "team1_config": team1_tuples,
                    "team2_config": team2_tuples
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "data": None,
                    "error": f"战斗配置验证失败: {str(e)}",
                    "execution_time": 0
                }), 400
        
        # 计算每个进程的工作量
        total_battles = len(processed_battles)
        battles_per_worker = max(1, total_battles // max_workers)
        
        # 分割任务
        battle_chunks = []
        for i in range(0, total_battles, battles_per_worker):
            chunk = processed_battles[i:i + battles_per_worker]
            battle_chunks.append(chunk)
        
        # 使用进程池执行批量战斗
        all_results = []
        successful_battles = 0
        failed_battles = 0
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            futures = [executor.submit(simulate_battle_batch_worker, chunk) 
                      for chunk in battle_chunks]
            
            # 收集结果
            for future in futures:
                try:
                    chunk_results = future.result(timeout=300)  # 5分钟超时
                    for result in chunk_results:
                        all_results.append(result)
                        if result["success"]:
                            successful_battles += 1
                        else:
                            failed_battles += 1
                except Exception as e:
                    # 处理进程异常
                    failed_battles += len(battle_chunks[futures.index(future)])
                    for battle in battle_chunks[futures.index(future)]:
                        all_results.append({
                            "battle_id": battle["battle_id"],
                            "success": False,
                            "data": None,
                            "error": f"进程执行失败: {str(e)}"
                        })
        
        # 按battle_id排序结果
        all_results.sort(key=lambda x: x["battle_id"])
        
        execution_time = time.time() - start_time
        
        return jsonify({
            "success": True,
            "data": {
                "total_battles": total_battles,
                "successful_battles": successful_battles,
                "failed_battles": failed_battles,
                "results": all_results
            },
            "error": None,
            "execution_time": round(execution_time, 3)
        })
        
    except Exception as e:
        execution_time = time.time() - start_time if 'start_time' in locals() else 0
        return jsonify({
            "success": False,
            "data": None,
            "error": f"服务器错误: {str(e)}",
            "execution_time": round(execution_time, 3)
        }), 500

@app.route('/battle/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    """
    return jsonify({
        "status": "healthy",
        "service": "battle_simulator",
        "cpu_count": mp.cpu_count(),
        "version": "1.0.0"
    })

@app.route('/battle/heroes', methods=['GET'])
def get_heroes_info():
    """
    获取英雄和技能信息接口
    """
    try:
        from hero_pool import HERO_POOL
        from skill_pool import SKILL_POOL

        heroes_info = []
        for hero_id, hero_data in HERO_POOL.items():
            heroes_info.append({
                "hero_id": hero_data[0],
                "name": hero_data[1],
                "hero_class": hero_data[2].value,
                "element": hero_data[3].value,
                "attack": hero_data[4],
                "defense": hero_data[5],
                "hp": hero_data[6],
                "speed": hero_data[7],
                "basic_skill_id": hero_data[8]
            })

        skills_info = []
        for skill_id, skill_class in SKILL_POOL.items():
            skill_instance = skill_class()
            skills_info.append({
                "skill_id": skill_id,
                "name": skill_instance.name,
                "description": skill_instance.description,
                "skill_type": skill_instance.skill_type.value,
                "cooldown": skill_instance.cooldown
            })
        
        return jsonify({
            "success": True,
            "data": {
                "heroes": heroes_info,
                "skills": skills_info
            },
            "error": None
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "data": None,
            "error": f"获取信息失败: {str(e)}"
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "data": None,
        "error": "接口不存在"
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "data": None,
        "error": "请求方法不被允许"
    }), 405

if __name__ == '__main__':
    # 开发环境运行
    print(f"战斗模拟器API启动中...")
    print(f"可用CPU核心数: {mp.cpu_count()}")
    print(f"单场战斗接口: POST /battle/single")
    print(f"批量战斗接口: POST /battle/batch")
    print(f"健康检查接口: GET /battle/health")
    print(f"英雄信息接口: GET /battle/heroes")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
