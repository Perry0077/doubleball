import requests

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
    # 'Cookie': 'HMF_CI=ef9011167b916dace70927a86560af5aa3a1ef3bb606ee76a4ca94e0ff5c3e35b5b437859f32f2a9c8b018f42a338d62dd7400c5046268bffd3a5da39d99e092a9; 21_vq=4',
}

params = {
    'name': 'ssq',
    'issueCount': '',
    'issueStart': '',
    'issueEnd': '',
    'dayStart': '',
    'dayEnd': '',
    'pageNo': '64',
    'pageSize': '30',
    'week': '',
    'systemType': 'PC',
}

response = requests.get(
    'https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice',
    params=params,
    headers=headers,
)

print(response.json())