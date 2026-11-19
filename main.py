import math

def distance(x1, y1, x2, y2):
    """计算两个二维点之间的直线距离。"""
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx * dx + dy * dy)


def main():
    start_x = 3
    start_y = 2
    goal_x = 6
    goal_y = 6

    result = distance(start_x, start_y, goal_x, goal_y)

    print("二维点质量轨迹仿真项目")
    print(f"起点: ({start_x}, {start_y})")
    print(f"目标点: ({goal_x}, {goal_y})")
    print(f"起点到目标点的距离: {result:.2f}")


if __name__ == "__main__":
    main()