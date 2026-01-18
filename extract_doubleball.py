import requests
import csv

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


def fetch_page(page_no, page_size=30):
    """获取指定页码的数据"""
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
    response = requests.get(API_URL, params=params, headers=headers)
    return response.json()


def fetch_latest_page():
    """只获取第一页（最新数据）"""
    print("正在获取最新数据...")
    data = fetch_page(1)
    if data.get('state') == 0:
        return data.get('result', [])
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
