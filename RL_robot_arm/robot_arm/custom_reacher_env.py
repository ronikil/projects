import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pybullet as p
import pybullet_data
import time


class KukaReacherEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self, render=False):
        super().__init__()
        self.render = render

        if render:
            p.connect(p.GUI)
        else:
            p.connect(p.DIRECT)

        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.8)

        # Control only first 2 joints
        self.control_joints = [0, 1]
        self.ee_link = 6  # KUKA iiwa end effector link

        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(2,), dtype=np.float32
        )

        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(10,), dtype=np.float32
        )

        self.max_steps = 200
        self.step_count = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.step_count = 0
        p.resetSimulation()

        p.loadURDF("plane.urdf")

        self.robot = p.loadURDF(
            "kuka_iiwa/model.urdf",
            useFixedBase=True
        )

        # Random reachable target
        min_dist = 0.70
        while True:
            target = np.random.uniform(low=[-0.9, -0.9, 0.3],
                                       high=[0.9, 0.9, 0.5])
            if np.linalg.norm(target[:2]) >= min_dist:
                break

        self.target_pos = target    

        self.target_id = p.loadURDF(
            "sphere_small.urdf",
            self.target_pos,
            globalScaling=1.5
        )

        return self._get_obs(), {}

    def step(self, action):
        self.step_count += 1

        # Scale action to joint range
        target_positions = action * 1.5

        p.setJointMotorControlArray(
            bodyUniqueId=self.robot,
            jointIndices=self.control_joints,
            controlMode=p.POSITION_CONTROL,
            targetPositions=target_positions,
            forces=[50, 50]
        )

        p.stepSimulation()
        if self.render:
            time.sleep(1 / 240)

        obs = self._get_obs()

        ee_pos = np.array(p.getLinkState(self.robot, self.ee_link)[0])
        dist = np.linalg.norm(ee_pos - self.target_pos)

        reward = -dist
        reward -= 0.01 * np.sum(np.square(action))

        terminated = dist < 0.05
        truncated = self.step_count >= self.max_steps

        if terminated:
            reward += 5.0

        return obs, reward, terminated, truncated, {}

    def _get_obs(self):
        joint_states = [p.getJointState(self.robot, i) for i in self.control_joints]

        joint_angles = np.array([s[0] for s in joint_states])
        joint_vels = np.array([s[1] for s in joint_states])

        ee_pos = np.array(p.getLinkState(self.robot, self.ee_link)[0])

        obs = np.concatenate([
            joint_angles,
            joint_vels,
            ee_pos,
            self.target_pos
        ])

        return obs.astype(np.float32)
