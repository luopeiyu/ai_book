
from stable_baselines3 import PPO
from grid_game import GridGame
import time
from grid_game_ppo_3 import GridWorldEnv
import numpy as np
def get_observation_from_game(game: GridGame) -> np.ndarray:
    gameenv = GridWorldEnv()
    gameenv.game = game
    return gameenv.get_observation()


def main():
    model = PPO.load("models/ppo_grid_model_2")
    game = GridGame()
    
    
    
    game.reset()
    while True:
        obs = get_observation_from_game(game)
        action, _state = model.predict(obs)
        action_value = action.item()
        print(f"action: {action_value}")
        win, hit_wall, time_up = game.action(action_value)
        game.render()
        if win:
            print("YOU WIN")
            break
        elif hit_wall:
            print("HIT WALL")
        elif time_up:
            print("GAME OVER")
            break
        time.sleep(1)


if __name__ == "__main__":
    main()

