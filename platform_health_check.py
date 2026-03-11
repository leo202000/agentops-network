#!/usr/bin/env python3
"""挖矿平台健康检查"""
import requests
from datetime import datetime

print("=" * 60)
print("挖矿平台健康检查")
print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

platforms = {
    "AgentCoin": {
        "url": "https://agentcoin.site",
        "check": "/api/health"
    },
    "Botcoin.farm": {
        "url": "https://botcoin.farm",
        "check": "/"
    },
    "MBC20": {
        "url": "https://mbc20.xyz",
        "check": "/"
    }
}

results = {}

for name, config in platforms.items():
    print(f"\n{name}")
    try:
        url = config['url'] + config['check']
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            print(f"   ✅ 健康 ({resp.status_code}, {resp.elapsed.total_seconds()*1000:.0f}ms)")
            results[name] = "healthy"
        else:
            print(f"   ⚠️ 异常 ({resp.status_code})")
            results[name] = "degraded"
    except requests.exceptions.ConnectionError:
        print(f"   ❌ 无法连接 (DNS/网络问题)")
        results[name] = "unhealthy"
    except requests.exceptions.Timeout:
        print(f"   ❌ 连接超时")
        results[name] = "unhealthy"
    except Exception as e:
        print(f"   ❌ 错误：{e}")
        results[name] = "unhealthy"

print("\n" + "=" * 60)
print("检查结果汇总:")
for name, status in results.items():
    icon = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
    print(f"   {icon} {name}: {status}")
print("=" * 60)

# 返回结果
import json
print(f"\n📊 JSON 输出:")
print(json.dumps(results, indent=2))
