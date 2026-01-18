#!/usr/bin/env python3
"""
双色球号码重复检查工具
检查用户输入的号码是否与历史开奖数据重复
"""

import csv
import sys
from pathlib import Path


def load_history(csv_file):
    """
    加载历史数据
    返回: dict，key 为 (排序后的红球元组, 蓝球)，value 为 (期号, 日期)
    """
    history = {}
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row['code']
            date = row['date']
            # 解析红球，去掉引号并排序
            red_balls = tuple(sorted(row['red'].split(',')))
            blue_ball = row['blue']
            history[(red_balls, blue_ball)] = (code, date)
    return history


def parse_input(red_input, blue_input):
    """
    解析并验证用户输入
    返回: (排序后的红球元组, 蓝球字符串)
    抛出: ValueError 如果输入无效
    """
    # 解析红球
    red_parts = [r.strip() for r in red_input.split(',')]
    if len(red_parts) != 6:
        raise ValueError("红球必须是6个数字")

    red_balls = []
    for r in red_parts:
        try:
            num = int(r)
        except ValueError:
            raise ValueError(f"无效的红球号码: {r}")
        if num < 1 or num > 33:
            raise ValueError(f"红球号码必须在1-33之间: {num}")
        # 格式化为两位数字符串
        red_balls.append(f"{num:02d}")

    # 检查红球是否有重复
    if len(set(red_balls)) != 6:
        raise ValueError("红球号码不能重复")

    # 解析蓝球
    try:
        blue_num = int(blue_input.strip())
    except ValueError:
        raise ValueError(f"无效的蓝球号码: {blue_input}")
    if blue_num < 1 or blue_num > 16:
        raise ValueError(f"蓝球号码必须在1-16之间: {blue_num}")
    blue_ball = f"{blue_num:02d}"

    return tuple(sorted(red_balls)), blue_ball


def check_duplicate(red_balls, blue_ball, history):
    """
    检查号码是否与历史重复
    返回: None 如果未重复，否则返回 (期号, 日期)
    """
    key = (red_balls, blue_ball)
    return history.get(key)


def main():
    """主程序: 支持命令行参数或交互式输入"""
    # 获取 CSV 文件路径
    script_dir = Path(__file__).parent
    csv_file = script_dir / 'doubleball_data.csv'

    if not csv_file.exists():
        print(f"错误: 找不到历史数据文件 {csv_file}")
        sys.exit(1)

    # 加载历史数据
    print("正在加载历史数据...")
    history = load_history(csv_file)
    print(f"已加载 {len(history)} 条历史记录")
    print()

    # 获取输入
    if len(sys.argv) == 3:
        # 命令行参数模式
        red_input = sys.argv[1]
        blue_input = sys.argv[2]
    elif len(sys.argv) == 1:
        # 交互式输入模式
        red_input = input("请输入红球号码 (6个，用逗号分隔): ")
        blue_input = input("请输入蓝球号码: ")
    else:
        print("用法:")
        print(f"  {sys.argv[0]} <红球> <蓝球>")
        print(f"  例如: {sys.argv[0]} 01,02,03,04,05,06 07")
        print(f"  或直接运行进入交互模式: {sys.argv[0]}")
        sys.exit(1)

    # 解析输入
    try:
        red_balls, blue_ball = parse_input(red_input, blue_input)
    except ValueError as e:
        print(f"输入错误: {e}")
        sys.exit(1)

    # 检查重复
    result = check_duplicate(red_balls, blue_ball, history)

    # 格式化显示的号码
    display_red = ','.join(red_balls)

    print()
    if result is None:
        print("✓ 恭喜！您选择的号码未在历史中出现过")
        print(f"  红球: {display_red}")
        print(f"  蓝球: {blue_ball}")
    else:
        code, date = result
        print("✗ 注意！您选择的号码与历史开奖重复")
        print(f"  红球: {display_red}")
        print(f"  蓝球: {blue_ball}")
        print(f"  重复期号: {code} ({date})")


if __name__ == '__main__':
    main()
