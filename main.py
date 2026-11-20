import math
import random

def distance(x1, y1, x2, y2):
    """计算两个二维点之间的直线距离。"""
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx * dx + dy * dy)


def move(state, action, width, height):
    """根据动作计算新位置，不修改传入的状态。"""
    changes = {
        "UP": (0, 1),
        "DOWN": (0, -1),
        "LEFT": (-1, 0),
        "RIGHT": (1, 0),
        "STAY": (0, 0),
    }

    if action not in changes:
        raise ValueError(f"不支持的动作：{action}")

    dx, dy = changes[action]

    new_x = state["x"] + dx
    new_y = state["y"] + dy

    # 将坐标限制在地图范围内。
    new_x = max(0, min(width - 1, new_x))
    new_y = max(0, min(height - 1, new_y))

    return {"x": new_x, "y": new_y}

def random_policy(state, goal, rng):
    """随机策略，每次随机选一个动作

    Args:
        state (dict): 当前位置
        goal (dict): 目标位置。随机策略暂时不需要看位置，所以 state 和 goal 没有在函数体内使用。我们仍保留这两个参数，让各种策略采用相同的调用方式。
        rng (random.Random): 随机数生成器，用于随机选择
    """
    actions = ["RIGHT", "LEFT", "DOWN", "UP", "STAY"]
    return rng.choice(actions)

def greedy_policy(state, goal, rng):
    """
    贪心策略，每次都往最近的方向移动
    """
    horizontal = goal["x"] - state["x"]
    vertical = goal["y"] - state["y"]

    if abs(horizontal) >= abs(vertical) and horizontal != 0:
        if horizontal > 0:
            return "RIGHT"
        return "LEFT"

    if vertical != 0:
        if vertical > 0:
            return "UP"
        return "DOWN"

    return "STAY"

def run_episode(start, goal, width, height, policy, seed, max_steps):
    """运行一个回合，返回轨迹和评测结果。

    Args:
        start (dict): 起始位置
        goal (dict): 终点位置
        width (int): 棋盘格宽度
        height (int): 棋盘格高度
        policy (function): 策略名称
        seed (_type_): 随机数生成器的初始起点，若为None默认使用当前系统时间作为种子。可以是任何可哈希（hashable）的对象，通常用 32 位整数
        max_steps (int): 避免程序卡死的最大步数
    """
    if max_steps <1:
        raise ValueError("max_steps必须是正整数")

    rng = random.Random(seed)

    state = start.copy()   #浅拷贝。在内存中开辟一块新的空间，把 start 里的数值原封不动地复制过来，生成一个全新的列表
# 1. 什么时候用浅拷贝（.copy()）？
# 数据结构只有一层（比如你之前的 start = [0, 0] 或者 state = {"x": 1, "y": 2}）。
# 或者内部嵌套的都是不可变对象（如数字、字符串、元组）。
# 追求效率：浅拷贝的速度极快，占用内存小。
# 故意想共享内部资源：比如多个状态共享同一个“静态地图”或“配置字典”，这时候用浅拷贝最合适。
# 2. 什么时候必须用深拷贝（copy.deepcopy()）？
# 数据结构有多层嵌套（比如二维列表 [[0, 0], [1, 1]]、列表里面套字典等）。
# 你希望修改新对象时，绝对不要影响到旧对象。
    trajectory = [state]
    steps = 0

    while state != goal and steps < max_steps:
        action = policy(state, goal, rng)
        state = move(state, action, width, height)
        trajectory.append(state)

        steps += 1

    final_distance = distance(state["x"], state["y"], goal["x"], goal["y"])

    return {
        "policy": policy.__name__,
        "seed": seed,
        "success": state == goal,
        "steps": steps,
        "final_distance": final_distance,
        "trajectory": trajectory,
    }

def run_experiment(
    start,
    goal,
    width,
    height,
    policy,
    episodes,
    seed,
    max_steps,
):
    """使用同一个策略运行多个回合。
        episodes (int): 执行的回合数
    """
    if episodes < 1:
        raise ValueError("episodes 必须是正整数")

    results = []

    for episode_index in range(episodes):
        episode_seed = seed + episode_index      #每个随机策略回合会有不同的随机动作，但整个实验仍然可以重复

        result = run_episode(
            start=start,
            goal=goal,
            width=width,
            height=height,
            policy=policy,
            seed=episode_seed,
            max_steps=max_steps,
        )

        result["episode"] = episode_index
        results.append(result)

    return results

def summarize_results(results):
     """
     根据多个回合的结果计算统计指标。
     """
     if not results:
         raise ValueError("results 不能为空")

     successful_results = [
         result for result in results
         if result["success"]
    ]

     total_episodes = len(results)
     success_count = len(successful_results)

     average_steps = (
         sum(result["steps"] for result in results)
         / total_episodes
     )

     average_final_distance = (
         sum(result["final_distance"] for result in results)
         / total_episodes
     )

     if successful_results:
         successful_average_steps = (
             sum(result["steps"] for result in successful_results)
             / len(successful_results)
         )
     else:
         successful_average_steps = None
 
     return {
         "episodes": total_episodes,
         "successes": success_count,
         "success_rate": success_count / total_episodes,
         "average_steps": average_steps,
         "average_final_distance": average_final_distance,
         "successful_average_steps": successful_average_steps,
         "shortest_steps": min(
             result["steps"] for result in results
         ),
         "longest_steps": max(
             result["steps"] for result in results
         ),
     }
    
def main():
    start = {"x": 0, "y": 0}
    goal = {"x": 3, "y": 2}

    width = 7
    height = 7
    episodes = 20
    seed = 0
    max_steps = 30

    policies = [
        greedy_policy,
        random_policy,
    ]

    for policy in policies:
        results = run_experiment(
            start=start,
            goal=goal,
            width=width,
            height=height,
            policy=policy,
            episodes=episodes,
            seed=seed,
            max_steps=max_steps,
        )

        summary = summarize_results(results)

        print(f"策略：{policy.__name__}")
        print(f"实验回合数：{summary['episodes']}")
        print(f"成功回合数：{summary['successes']}")
        print(f"成功率：{summary['success_rate']:.2%}")
        print(f"平均步数：{summary['average_steps']:.2f}")
        print(
            "成功回合平均步数："
            f"{summary['successful_average_steps']}"
        )
        print(
            "平均最终距离："
            f"{summary['average_final_distance']:.2f}"
        )
        print(f"最短步数：{summary['shortest_steps']}")
        print(f"最长步数：{summary['longest_steps']}")
        print()

if __name__ == "__main__":
    main()