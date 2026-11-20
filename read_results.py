from pathlib import Path

from main import load_experiment
from main import summarize_results


def check_result(output_dir):
    config, results, saved_summary = load_experiment(
        output_dir
    )

    recomputed_summary = summarize_results(results)

    saved_episodes = int(saved_summary["episodes"])
    saved_successes = int(saved_summary["successes"])
    saved_success_rate = float(
        saved_summary["success_rate"]
    )

    same_result = (
        recomputed_summary["episodes"] == saved_episodes
        and recomputed_summary["successes"] == saved_successes
        and abs(
            recomputed_summary["success_rate"]
            - saved_success_rate
        ) < 1e-12
    )

    print(f"读取目录：{output_dir}")
    print(f"策略：{config['policy']}")
    print(f"配置中的回合数：{config['episodes']}")
    print(f"实际读取的回合数：{len(results)}")
    print(
        f"重新计算的成功率："
        f"{recomputed_summary['success_rate']:.2%}"
    )
    print(
        f"CSV 中保存的成功率："
        f"{saved_success_rate:.2%}"
    )
    print(f"读取结果是否一致：{same_result}")
    print()


def main():
    directories = [
        Path("runs") / "greedy_policy_seed0",
        Path("runs") / "random_policy_seed0",
    ]

    for output_dir in directories:
        check_result(output_dir)


if __name__ == "__main__":
    main()