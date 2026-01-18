import requests
import csv
import time
import re
import json

# API 请求配置 (复用 scrape_doubleball.py 的配置)
cookies = {
    'HMF_CI': 'ef9011167b916dace70927a86560af5aa3a1ef3bb606ee76a4ca94e0ff5c3e35b5b437859f32f2a9c8b018f42a338d62dd7400c5046268bffd3a5da39d99e092a9',
    '21_vq': '4',
}

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Connection': 'keep-alive',
    'Referer': 'https://www.cwl.gov.cn/ygkj/wqkjgg/ssq/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
}

API_URL = 'https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice'

# 备用 API 配置 (zhcw.com - 中国福利彩票网)
BACKUP_API_URL = 'https://jc.zhcw.com/port/client_json.php'
backup_headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Connection': 'keep-alive',
    'Referer': 'https://www.zhcw.com/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
}


def parse_jsonp(jsonp_str):
    """解析 JSONP 响应，提取 JSON 数据"""
    match = re.search(r'\((\{.*\})\)$', jsonp_str, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    raise Exception("无法解析 JSONP 响应")


def convert_backup_record(record):
    """将备用 API 的数据格式转换为标准格式"""
    return {
        'code': record.get('issue', ''),
        'date': record.get('openTime', ''),
        'red': record.get('frontWinningNum', '').replace(' ', ','),
        'blue': record.get('backWinningNum', ''),
    }


def fetch_page_backup(page_no, page_size=30, max_retries=3):
    """从备用 API 获取数据"""
    params = {
        'callback': 'jQuery_callback',
        'transactionType': '10001001',
        'lotteryId': '1',  # 双色球
        'issueCount': str(page_size),
        'startIssue': '',
        'endIssue': '',
        'startDate': '',
        'endDate': '',
        'pageNum': str(page_no),
        'pageSize': str(page_size),
        'type': '0',
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(
                BACKUP_API_URL,
                params=params,
                headers=backup_headers,
                timeout=30
            )

            if response.status_code != 200:
                print(f"备用 API HTTP 错误: {response.status_code}")
                raise Exception(f"HTTP {response.status_code}")

            if not response.text.strip():
                print("备用 API 响应内容为空")
                raise Exception("空响应")

            # 解析 JSONP
            data = parse_jsonp(response.text)

            # 转换数据格式
            records = data.get('data', [])
            return [convert_backup_record(r) for r in records]

        except Exception as e:
            print(f"备用 API 第 {attempt + 1} 次请求失败: {e}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                print("备用 API 已达最大重试次数")
                raise

    return []


def fetch_page(page_no, page_size=30, max_retries=3):
    """获取指定页码的数据，带重试机制"""
    params = {
        'name': 'ssq',
        'issueCount': '',
        'issueStart': '',
        'issueEnd': '',
        'dayStart': '',
        'dayEnd': '',
        'pageNo': str(page_no),
        'pageSize': str(page_size),
        'week': '',
        'systemType': 'PC',
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(
                API_URL,
                params=params,
                headers=headers,
                timeout=30
            )

            # 检查状态码
            if response.status_code != 200:
                print(f"HTTP 错误: {response.status_code}")
                raise Exception(f"HTTP {response.status_code}")

            # 检查响应内容是否为空
            if not response.text.strip():
                print("响应内容为空")
                raise Exception("空响应")

            # 检查是否为 JSON
            content_type = response.headers.get('Content-Type', '')
            if 'json' not in content_type.lower() and 'javascript' not in content_type.lower():
                print(f"响应类型异常: {content_type}")
                print(f"响应内容: {response.text[:500]}")
                raise Exception("非 JSON 响应")

            return response.json()

        except Exception as e:
            print(f"第 {attempt + 1} 次请求失败: {e}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                print("已达最大重试次数")
                raise

    return None


def fetch_latest_page():
    """只获取第一页（最新数据），优先使用 zhcw.com，失败后回退到 cwl.gov.cn"""
    print("正在获取最新数据...")

    # 优先使用 zhcw.com (GitHub Actions 可访问)
    try:
        records = fetch_page_backup(1)
        if records:
            print("使用数据源: zhcw.com")
            return records
        print("zhcw.com 返回空数据")
    except Exception as e:
        print(f"zhcw.com 失败: {e}")

    # 回退到 cwl.gov.cn
    print("切换到备用数据源 (cwl.gov.cn)...")
    try:
        data = fetch_page(1)
        if data.get('state') == 0:
            return data.get('result', [])
        print(f"cwl.gov.cn 返回错误状态: {data.get('state')}")
    except Exception as e:
        print(f"cwl.gov.cn 也失败: {e}")

    return []


def fetch_all_data():
    """遍历所有页面获取完整数据"""
    all_records = []
    page_no = 1

    while True:
        print(f"正在获取第 {page_no} 页...")
        data = fetch_page(page_no)

        if data.get('state') != 0:
            print(f"API 返回错误: {data}")
            break

        result = data.get('result', [])
        if not result:
            print("没有更多数据")
            break

        all_records.extend(result)

        # 检查是否还有更多页
        total = data.get('total', 0)
        page_size = data.get('pageSize', 30)
        if page_no * page_size >= total:
            print(f"已获取全部 {total} 条记录")
            break

        page_no += 1

    return all_records


def extract_fields(records):
    """提取指定字段: code, date, red, blue"""
    extracted = []
    for record in records:
        extracted.append({
            'code': record.get('code', ''),
            'date': record.get('date', ''),
            'red': record.get('red', ''),
            'blue': record.get('blue', ''),
        })
    return extracted


def print_table(data):
    """格式化输出到控制台"""
    print("\n" + "=" * 70)
    print(f"{'期号':<12}{'日期':<18}{'红球':<22}{'蓝球'}")
    print("=" * 70)
    for row in data:
        print(f"{row['code']:<12}{row['date']:<18}{row['red']:<22}{row['blue']}")
    print("=" * 70)
    print(f"共 {len(data)} 条记录\n")


def save_to_csv(data, filename='doubleball_data.csv'):
    """保存数据到 CSV 文件"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['code', 'date', 'red', 'blue'])
        writer.writeheader()
        writer.writerows(data)
    print(f"数据已保存到 {filename}")


def main():
    print("开始获取双色球开奖数据...")

    # 获取所有数据
    all_records = fetch_all_data()

    if not all_records:
        print("未获取到任何数据")
        return

    # 提取字段
    extracted_data = extract_fields(all_records)

    # 输出到控制台 (只显示前 20 条)
    print_table(extracted_data[:20])
    if len(extracted_data) > 20:
        print(f"(仅显示前 20 条，共 {len(extracted_data)} 条)")

    # 保存到 CSV
    save_to_csv(extracted_data)


if __name__ == '__main__':
    main()
