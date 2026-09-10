import requests
from typing import Dict, List

class Simulator:
    def __init__(self, url="http://localhost:8080/face"):
        self.url = url

    def get_landmarks(self, params: Dict[str, int]) -> List[Dict[str, int]]:
        response = requests.get(self.url, params=params, timeout=5)
        if response.status_code == 200:
            landmarks = response.json()
            return landmarks
        else:
            print(f"HTTP请求失败: {response.status_code}")
            return None