import math
import random
import json    #保存完整实验数据
import csv     #保存表格形式的统计结果
from pathlib import Path   #跨平台处理文件夹和文件路径
import argparse         #Python 标准库中专门读取命令行参数的模块  #arg表示argument，是实参。而parameter是实参  #parse是解析的意思，parser解析器

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

def save_experiment(output_dir, config, results, summary):
    """
    保存一次实验的配置、每回合结果和汇总指标。
    output_dir(str): 保存结果的文件夹路径（字符串或 Path 对象）
    config:实验的配置信息
    """
    output_path = Path(output_dir)      #使用 pathlib 库中的 Path 将传入的字符串路径转化为路径对象。这样做的好处是跨平台兼容性更好，并且可以使用 / 符号来拼接路径（比直接字符串拼接更优雅、更安全）。

    # 如果文件夹不存在，就自动创建
    output_path.mkdir(parents=True, exist_ok=True)
    #parents=True：如果父目录不存在，会自动递归创建（比如 output_dir="results/run_1"，如果 results 也没有，会一并创建）。
    #exist_ok=True：如果文件夹已经存在，不要报错，直接跳过。
    
    # 保存实验配置(使用 / 符号拼接路径)
    experiment_path = output_path / "experiment.json"

    with experiment_path.open("w", encoding="utf-8") as file:
        json.dump(
            config,
            file,   #就是with ... as file中的file
            ensure_ascii=False,
            indent=2,
        )
    # with ... as file:：使用上下文管理器打开文件。这样在缩进块执行完毕后，文件会自动关闭，不用担心忘记关文件导致内存泄漏。
    # "w"：写入模式（Write）。如果文件存在会被覆盖。
    # encoding="utf-8"：指定编码为 utf-8，防止中文（如果 config 里有中文）乱码。
    # json.dump()：将 Python 字典（config）序列化为 JSON 字符串并写入 file。
    # ensure_ascii=False：非常重要！如果不加这个，中文会被转成 \uXXXX 的 Unicode 编码，加上之后就能原样保留中文，方便人直接阅读。
    # indent=2：让生成的 JSON 文件有 2 个空格的缩进，排版美观，方便人类阅读。

    # 保存每个回合的完整结果
    episodes_path = output_path / "episodes.json"

    with episodes_path.open("w", encoding="utf-8") as file:
        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=2,
        )

    # 保存汇总统计
    summary_path = output_path / "summary.csv"

    #定义表头（summary 字典里的键必须和这些列名对应）
    fieldnames = [
        "episodes",
        "successes",
        "success_rate",
        "average_steps",
        "average_final_distance",
        "successful_average_steps",
        "shortest_steps",
        "longest_steps",
    ]

    with summary_path.open(
        "w",
        newline="",     #在写入 CSV 时，必须加上这个参数。否则在 Windows 系统上，CSV 的每一行之间会多出一个空行。
        encoding="utf-8-sig",    #加上 -sig，Excel 就能完美识别中文
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )  #创建一个 CSV 写入器。csv.DictWriter：专门用于写入字典格式的数据。它会自动按照 fieldnames 的顺序，把字典里的值填入对应的列中。

        writer.writeheader()    #把前面定义的 fieldnames 作为第一行写入文件
        writer.writerow(summary)   #把 summary 字典里的值，按照表头的顺序，作为第二行写入

    print(f"实验结果已保存到：{output_path}")

def load_experiment(output_dir):
    """
    从文件中读取一次已经保存的实验。
    """
    output_path = Path(output_dir)

    experiment_path = output_path / "experiment.json"
    episodes_path = output_path / "episodes.json"
    summary_path = output_path / "summary.csv"

    with experiment_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        config = json.load(file)

    with episodes_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        results = json.load(file)

    with summary_path.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        reader = csv.DictReader(file)   #reader读了第一行，即表头 #csv.DictReader 会自动把 CSV 文件的第一行（也就是表头）作为字典的“键（Key）”，把后续每一行的数据作为“值（Value）”
        saved_summary = next(reader)    #让读取器往下读一行数据，并把它变成一个 Python 字典，赋值给 saved_summary
    # json.load(file) 将 JSON 文件恢复成 Python 字典或列表；
    # csv.DictReader(file) 将 CSV 的一行读取成字典；
    # CSV 中的数据默认都是字符串，所以后面需要用 int() 或 float() 转换

    return config, results, saved_summary

def parse_args():
    parser = argparse.ArgumentParser(     #ArgumentParser 是模块里的一个类
        description="二维点质量轨迹仿真与实验分析工具"
    )

    parser.add_argument(
        "--episodes",  #参数名
        type=int,      #可选关键字参数  #键入默认str，这里转成int
        default=20,
        help="实验回合数，默认是 20",  #帮助说明
    )

    parser.add_argument(
        "--policy",
        choices=["greedy", "random", "both"],
        default="both",
        help="选择策略，默认运行两种策略",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="随机种子，默认是 0",
    )

    parser.add_argument(
        "--max-steps",
        dest="max_steps",    #参数名带连字符，要手动指定变量名
        type=int,
        default=30,
        help="每个回合的最大步数，默认是 30",
    )

    parser.add_argument(
        "--output",
        default="runs",
        help="实验结果保存目录，默认是 runs",
    )

    return parser.parse_args()   #parse_args()是ArgumentParser实例的方法，作用：读取命令行参数，按 add_argument 登记的规则，把字符串校验、转换，生成并返回一个 Namespace 对象，如Namespace(episodes=50, policy='greedy', seed=0, max_steps=30, output='runs')

def main():
    args = parse_args()

    start = {"x": 0, "y": 0}
    goal = {"x": 3, "y": 2}

    width = 7
    height = 7

    if args.policy == "greedy":
        policies = [greedy_policy]
    elif args.policy == "random":
        policies = [random_policy]
    else:
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
            episodes=args.episodes,
            seed=args.seed,
            max_steps=args.max_steps,
        )

        summary = summarize_results(results)

        config = {
            "start": start,
            "goal": goal,
            "width": width,
            "height": height,
            "policy": policy.__name__,
            "episodes": args.episodes,
            "seed": args.seed,
            "max_steps": args.max_steps,
        }

        if args.policy == "both":
            output_dir = (
                Path(args.output)
                / f"{policy.__name__}_seed{args.seed}"
            )
        else:
            output_dir = Path(args.output)

        save_experiment(
            output_dir=output_dir,
            config=config,
            results=results,
            summary=summary,
        )

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