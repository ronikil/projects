from gymnasium.envs.registration import register

register(
    id="SimpleReacher-v0",
    entry_point="robot_arm.custom_reacher_env:KukaReacherEnv",
)