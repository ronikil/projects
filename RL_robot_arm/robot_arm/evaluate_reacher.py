import gymnasium as gym
from stable_baselines3 import SAC
import robot_arm

env = gym.make("SimpleReacher-v0", render=True)


model = SAC.load("sac_simple_reacher", env=env)

obs, _ = env.reset()
episode_reward = 0
episode_count = 0

while True:

    action, _states = model.predict(obs, deterministic=True)
    
    obs, reward, terminated, truncated, info = env.step(action)
    episode_reward += reward
    
    if terminated or truncated:
        episode_count += 1
        print(f"Episode {episode_count} reward: {episode_reward:.2f}")
        episode_reward = 0
        obs, _ = env.reset()
