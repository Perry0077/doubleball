#!/usr/bin/env python3
"""
抓取最新双色球数据并增量更新 HTML 文件
- 首次运行：抓取全部数据
- 后续运行：只抓取第一页，增量添加新记录
"""
import json
import re
import os
from datetime import datetime

# 设置工作目录为脚本所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from extract_doubleball import fetch_all_data, fetch_latest_page, extract_fields

HTML_PATH = 'html/index.html'


def get_existing_data(html):
    """从 HTML 中提取现有的 historyData"""
    pattern = r'const historyData = (\[.*?\]);'
    match = re.search(pattern, html, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return []
    return []


def merge_data(existing, new_records):
    """合并数据，只添加不存在的新记录"""
    existing_codes = {item['code'] for item in existing}
    new_items = [item for item in new_records if item['code'] not in existing_codes]
    # 新数据在前，保持按期号降序
    return new_items + existing


def update_html(full_refresh=False):
    # 1. 读取 HTML
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # 2. 获取现有数据
    existing_data = get_existing_data(html)

    # 3. 决定抓取策略
    if full_refresh or not existing_data:
        print("执行全量抓取...")
        records = fetch_all_data()
        data = extract_fields(records)
        new_count = len(data)
    else:
        print("执行增量更新...")
        latest_records = fetch_latest_page()
        new_records = extract_fields(latest_records)
        data = merge_data(existing_data, new_records)
        new_count = len(data) - len(existing_data)

    # 4. 生成元数据
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    latest_issue = data[0]['code'] if data else ''
    latest_date = data[0]['date'] if data else ''
    total_count = len(data)

    # 5. 更新 historyData
    json_data = json.dumps(data, ensure_ascii=False)
    pattern = r'const historyData = \[.*?\];'
    replacement = f'const historyData = {json_data};'
    html = re.sub(pattern, replacement, html, flags=re.DOTALL)

    # 6. 更新元数据
    meta_info = {
        'updateTime': update_time,
        'latestIssue': latest_issue,
        'latestDate': latest_date,
        'totalCount': total_count
    }
    meta_json = json.dumps(meta_info, ensure_ascii=False)

    # 替换或插入 dataInfo
    if 'const dataInfo = ' in html:
        pattern = r'const dataInfo = \{.*?\};'
        replacement = f'const dataInfo = {meta_json};'
        html = re.sub(pattern, replacement, html, flags=re.DOTALL)
    else:
        # 在 historyData 后插入
        html = html.replace(
            f'const historyData = {json_data};',
            f'const historyData = {json_data};\n    const dataInfo = {meta_json};'
        )

    # 7. 写回 HTML
    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'✅ 更新完成！新增 {new_count} 条，共 {total_count} 条')
    print(f'   最新期号: {latest_issue} ({latest_date})')
    print(f'   更新时间: {update_time}')


if __name__ == '__main__':
    import sys
    full_refresh = '--full' in sys.argv
    update_html(full_refresh)
