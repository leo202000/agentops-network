import requests

MOLT_API_KEY = "moltbook_sk_3Y-R3S8dP291uZ_CuX_R0RVTCbHdNpgN"
AGENT_NAME = "beiassistant"

headers = {
    "Authorization": f"Bearer {MOLT_API_KEY}"
}

# 获取我的帖子
url = f"https://www.moltbook.com/api/v1/agents/profile?name={AGENT_NAME}"

try:
    response = requests.get(url, headers=headers, timeout=10)
    result = response.json()
    print(f"API 响应：{result}")
except Exception as e:
    print(f"错误：{e}")
