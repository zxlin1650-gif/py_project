import math


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


def main():
    width = 7
    height = 7

    state = {"x": 0, "y": 0}
    goal = {"x": 3, "y": 2}

    actions = ["RIGHT", "RIGHT", "RIGHT", "UP", "UP"]

    # 轨迹首先记录起点。
    trajectory = [state]
    success = state == goal

    print("二维小车移动实验")
    print(f"起点：{state}")
    print(f"目标：{goal}")

    if not success:
        for step, action in enumerate(actions, start=1):
            state = move(state, action, width, height)
            trajectory.append(state)

            remaining = distance(
                state["x"], state["y"], goal["x"], goal["y"]
            )

            print(
                f"第 {step} 步 | 动作：{action} | "
                f"位置：{state} | 距离：{remaining:.2f}"
            )

            if state == goal:
                success = True
                break

    print(f"是否到达目标：{success}")
    print(f"实际执行步数：{len(trajectory) - 1}")
    print(f"完整轨迹：{trajectory}")


if __name__ == "__main__":
    main()