import gymnasium as gym
from stable_baselines3 import SAC
import robot_arm

env = gym.make("SimpleReacher-v0", render=False)

model = SAC(
    "MlpPolicy",
    env,
    verbose=1,
    device="cuda"
)

model.learn(total_timesteps=300_000)
model.save("sac_simple_reacher")