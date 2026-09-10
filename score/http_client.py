"""
战斗模拟器HTTP客户端
"""

import requests
import json
import time
from typing import List, Tuple, Dict, Any, Optional

class BattleSimulatorClient:
    """战斗模拟器HTTP客户端"""
    
    def __init__(self, base_url: str = "http://localhost:5000", timeout: int = 300):
        """
        初始化客户端
        
        Args:
            base_url: API基础URL
            timeout: 请求超时时间
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # 设置请求头
        #self.session.headers.update({
        #    'Content-Type': 'application/json',
        #    'User-Agent': 'BattleSimulator-Client/1.0'
        #})
        
    
    def make_request_2(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        发送HTTP请求的通用方法
        
        Args:
            method: HTTP方法 ('GET', 'POST', etc.)
            endpoint: API端点
            data: 请求数据
            
        Returns:
            响应数据字典
            
        Raises:
            requests.RequestException: 请求失败
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=self.timeout)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            print(f"请求超时: {url}")
            raise
        except requests.exceptions.ConnectionError:
            print(f"连接失败: {url}")
            raise
        except requests.exceptions.HTTPError as e:
            print(f"HTTP错误: {e.response.status_code} - {url}")
            raise
        except json.JSONDecodeError:
            print(f"JSON解析失败: {url}")
            raise


    def make_request(self, method, endpoint, data=None):
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=self.timeout)
            else:  # 默认POST
                response = self.session.post(url, json=data, timeout=self.timeout)
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"请求失败 {url}: {e}")
            raise    
        
    def simulate_single_battle(self, team1_config: List[Tuple[int, int]], 
                              team2_config: List[Tuple[int, int]]) -> Dict[str, Any]:
        """
        模拟单场战斗
        
        Args:
            team1_config: 队伍1配置 [(hero_id, skill_id), ...]
            team2_config: 队伍2配置 [(hero_id, skill_id), ...]
            
        Returns:
            战斗结果字典
        """
        data = {
            "team1_config": team1_config,
            "team2_config": team2_config
        }
        
        response = self.make_request('POST', '/battle/single', data)
        
        if not response.get('success', False):
            raise RuntimeError(f"战斗模拟失败: {response.get('error', '未知错误')}")
        
        return response['data']
    
    def simulate_batch_battles(self, battles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量模拟战斗
        
        Args:
            battles: 战斗配置列表，每个元素包含 team1_config 和 team2_config
            
        Returns:
            战斗结果列表，与输入顺序一致
        """
        # 构造API请求数据
        data = {"battles": []}
        for i, battle in enumerate(battles):
            data["battles"].append({
                "battle_id": i,
                "team1_config": battle['team1_config'],
                "team2_config": battle['team2_config']
            })
        
        response = self.make_request('POST', '/battle/batch', data)
        
        if not response.get('success', False):
            raise RuntimeError(f"批量战斗模拟失败: {response['error']}")
        
        # 注意接口结果是按id从小到大排序
        results = response['data']['results']
        
        # 检查是否有任何战斗失败，如果有则认为全部失败
        successful_battles = response['data']['successful_battles']
        total_battles = response['data']['total_battles']
        if successful_battles != total_battles:
            raise RuntimeError(f"批量战斗中有失败的战斗: {response['error']}")
        
        
        #直接提取data
        results = [result['data'] for result in results]

        return results
    
    def get_heroes_info(self) -> Dict[str, Any]:
        """
        获取英雄和技能信息
        
        Returns:
            英雄和技能信息字典
        """
        response = self.make_request('GET', '/battle/heroes')
        
        if not response.get('success', False):
            raise RuntimeError(f"获取英雄信息失败: {response.get('error', '未知错误')}")
        
        return response['data']
    
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            服务状态信息
        """
        return self.make_request('GET', '/battle/health')
    
    def swap_team_perspective(self, battle_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        交换战斗结果的队伍视角
        
        将战斗结果从一个队伍的视角转换为另一个队伍的视角，
        包括胜负结果和队伍统计数据的交换
        
        Args:
            battle_result: 原始战斗结果
            
        Returns:
            交换视角后的战斗结果副本
        """
        # 创建结果副本避免修改原始数据
        swapped_result = battle_result.copy()
        
        # 交换胜负结果
        if swapped_result['winner'] == 'team1_win':
            swapped_result['winner'] = 'team2_win'
        elif swapped_result['winner'] == 'team2_win':
            swapped_result['winner'] = 'team1_win'
        # 平局保持不变
        
        # 交换队伍统计数据
        swapped_result['team1_stats'], swapped_result['team2_stats'] = \
            swapped_result['team2_stats'], swapped_result['team1_stats']
            
        return swapped_result



    def simulate_single_battle_bidirection(self, team1_config: List[Tuple[int, int]], team2_config: List[Tuple[int, int]]) -> List[Dict[str, Any]]:
        """
        单场双向对战模拟
        
        Args:
            team1_config: 队伍1配置
            team2_config: 队伍2配置
        
        Returns:
            包含两场战斗结果的列表（先手和后手）
        """

        battles = [
            {
                'team1_config': team1_config,
                'team2_config': team2_config
            },
            {
                'team1_config': team2_config,
                'team2_config': team1_config
            }
        ]
        
        
        # 批量模拟战斗
        battle_results = self.simulate_batch_battles(battles)
        # 处理双向对战结果
        # 第一场：team1先手，直接使用结果
        team1_as_first_hand = battle_results[0]
        
        # 第二场：team1后手，需要交换视角恢复team1视角
        team1_as_second_hand_original = battle_results[1]
        team1_as_second_hand = self.swap_team_perspective(team1_as_second_hand_original)
        
        return [team1_as_first_hand, team1_as_second_hand]

    def simulate_batch_battles_bidirection(self, team1_list: List[List[Tuple[int, int]]], team2_list: List[List[Tuple[int, int]]]) -> List[Dict[str, Any]]:
        """
        双向对战批量模拟
        
        Args:
            team1_list: 队伍1列表
            team2_list: 队伍2列表
        
        Returns:
            战斗结果列表
        """
        
        # 构建批量战斗请求
        # 由于先后手顺序有关，需要计算先手和后手两种情况
        battles = []

        for team1 in team1_list:
            for team2 in team2_list:
                # team1作为先手
                battles.append({
                    'team1_config': team1,
                    'team2_config': team2
                })
                # team1作为后手
                battles.append({
                    'team1_config': team2,
                    'team2_config': team1
                })
        
        # 批量模拟战斗
        battle_results = self.simulate_batch_battles(battles)

        # 处理结果
        team2_count = len(team2_list)
        battles_per_team1 = team2_count * 2  # 每个team1对每个team2都打先手和后手
        
        # processed_results结构: 每个team1对应一个列表，包含与所有team2的战斗结果
        # [
        #    [team1_0_vs_team2_0, team1_0_vs_team2_1, ...],  # team1_0的所有战斗结果
        #    [team1_1_vs_team2_0, team1_1_vs_team2_1, ...],  # team1_1的所有战斗结果
        #    ...
        # ]
        
        processed_results = []
        
        for i, team1 in enumerate(team1_list):
            start_idx = i * battles_per_team1
            team1_results = []
            
            for j, team2 in enumerate(team2_list):
                # 计算战斗结果索引
                base_idx = start_idx + j * 2
                first_hand_idx = base_idx      # team1先手战斗结果索引
                second_hand_idx = base_idx + 1 # team1后手战斗结果索引
                
                # 获取先手结果（直接使用）
                first_hand_result = battle_results[first_hand_idx]
                
                # 处理后手结果（需要交换视角）
                second_hand_result = self.swap_team_perspective(battle_results[second_hand_idx])
                
                # 添加到结果列表
                team1_results.extend([first_hand_result, second_hand_result])
            
            processed_results.append(team1_results)
        
        return processed_results


def test_client():
    client = BattleSimulatorClient()
    
    # 获取英雄信息
    print("获取英雄信息...")
    heroes_info = client.get_heroes_info()
    print(f"可用英雄数量: {len(heroes_info['heroes'])}")
    print(f"可用技能数量: {len(heroes_info['skills'])}")
    
    
    # 测试单场战斗
    print("模拟单场战斗...")

    result = client.simulate_single_battle([[1,2],[2,3],[3,4]], [[1,2],[2,3],[3,4]])
    print(result)
    print(f"战斗结果: {result['winner']}")
    print(f"战斗回合数: {result['rounds']}")

    
    # 测试多场战斗
    print("模拟多场战斗...")
    battles = [
        {
            "team1_config": [[1,1],[1,1],[1,1]],
            "team2_config": [[1,1],[1,1],[1,1]]
        },
        {
            "team1_config": [[2,2],[2,2],[2,2]],
            "team2_config": [[3,3],[3,3],[3,3]]
        }
    ]
    result = client.simulate_batch_battles(battles)
    print(result)

    #for i, r in enumerate(result):
    #    print(f"战斗结果: {r['winner']}")
    #    print(f"战斗回合数: {r['rounds']}")
        
    # 测试双向对战
    print("测试双向对战...")
    result = client.simulate_single_battle_bidirection([(7,6),(8,7),(9,8)], [(4,1),(5,2),(6,3)])
    print(result)

    print(f"战斗结果: {result[0]['winner']}")
    print(f"战斗结果: {result[1]['winner']}")
 
    # 测试双向对战批量模拟
    print("测试双向对战批量模拟...")
    result = client.simulate_batch_battles_bidirection([[(1,1),(1,1),(1,1)],[(2,2),(2,2),(2,2)]], [[(1,1),(1,1),(1,1)],[(2,2),(2,2),(2,2)]])
    print(result)
    for i, r in enumerate(result):
        print(f"战斗结果: {r[0]['winner']}")
        print(f"战斗结果: {r[1]['winner']}")

if __name__ == "__main__":
    test_client()
