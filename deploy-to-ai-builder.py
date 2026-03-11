#!/usr/bin/env python3
"""
AI Builder 部署脚本
用于将 reclaim-feed 项目部署到 ai-builders.space 平台
"""

import requests
import json
import sys
import time

# ============= 配置区域 =============

# API Token (从平台获取)
API_TOKEN = "sk_b32d221f_790a9240c8aef6e990c0b4884402db99d061"

# 代理设置 (如果需要)
PROXIES = {
    'http': 'http://127.0.0.1:7897',
    'https': 'http://127.0.0.1:7897',
}

# 部署信息
DEPLOY_CONFIG = {
    "repo_url": "https://github.com/bor799/reclaim-feed.git",
    "service_name": "reclaim-feed",
    "branch": "main",
}

# 可能的 API endpoints (按优先级排序)
API_ENDPOINTS = [
    "https://www.ai-builders.com/backend/v1/deployments",
    "https://api.ai-builders.com/v1/deployments",
    "https://students-backend.superlinear.academy/v1/deployments",
    "https://www.superlinear.academy/ai-builders/backend/v1/deployments",
]

# ============= 部署函数 =============

def deploy_to_endpoint(endpoint, config, token, proxies=None):
    """尝试向指定 endpoint 部署"""

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print(f"\n🚀 尝试部署到: {endpoint}")
    print(f"   仓库: {config['repo_url']}")
    print(f"   服务名: {config['service_name']}")
    print(f"   分支: {config['branch']}")

    try:
        response = requests.post(
            endpoint,
            headers=headers,
            json=config,
            proxies=proxies,
            timeout=120  # 部署可能需要较长时间
        )

        print(f"   状态码: {response.status_code}")

        if response.status_code in [200, 201, 202]:
            result = response.json()
            print(f"\n✅ 部署请求已成功提交!")
            print("=" * 60)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("=" * 60)

            # 显示部署信息
            if 'service_name' in result:
                print(f"\n📦 服务名称: {result['service_name']}")
                print(f"🌐 访问地址: https://{result['service_name']}.ai-builders.space")

            if 'status' in result:
                print(f"📊 当前状态: {result['status']}")

            if 'streaming_logs' in result and result['streaming_logs']:
                print(f"\n📋 构建日志:\n{result['streaming_logs']}")

            return True, result

        elif response.status_code == 401:
            print(f"   ❌ 认证失败 - Token 无效或已过期")
            return False, "认证失败"

        elif response.status_code == 409:
            print(f"   ⚠️  服务名冲突 - 可能需要先删除旧部署")
            return False, "服务名冲突"

        else:
            print(f"   ❌ 部署失败")
            try:
                error = response.json()
                print(f"   错误详情: {json.dumps(error, indent=2, ensure_ascii=False)}")
            except:
                print(f"   响应: {response.text[:500]}")
            return False, response.text

    except requests.exceptions.SSLError as e:
        print(f"   ❌ SSL 连接错误")
        return False, "SSL错误"

    except requests.exceptions.Timeout:
        print(f"   ❌ 请求超时")
        return False, "超时"

    except Exception as e:
        print(f"   ❌ 错误: {str(e)}")
        return False, str(e)

def main():
    """主函数"""

    print("=" * 60)
    print("🔥 AI Builder 部署脚本")
    print("   项目: 100X 知识萃取系统 (Reclaim Feed)")
    print("=" * 60)

    # 尝试所有可能的 endpoints
    for endpoint in API_ENDPOINTS:
        success, result = deploy_to_endpoint(
            endpoint,
            DEPLOY_CONFIG,
            API_TOKEN,
            PROXIES
        )

        if success:
            print(f"\n🎉 部署成功!")
            print(f"\n⏱️  部署通常需要 5-10 分钟完成")
            print(f"📌 你可以通过以下方式检查部署状态:")
            print(f"   - 访问 https://www.superlinear.academy/ai-builders")
            print(f"   - 或使用 GET 请求查询部署状态")
            return 0

    # 所有尝试都失败
    print("\n" + "=" * 60)
    print("❌ 所有 API endpoints 都无法访问")
    print("=" * 60)

    print("\n建议:")
    print("1. 访问 AI Builder 平台查看部署门户:")
    print("   https://www.superlinear.academy/ai-builders")
    print("\n2. 联系导师确认:")
    print("   - 正确的 API endpoint URL")
    print("   - API Token 是否有效")
    print("\n3. 或通过 Web 界面手动部署:")
    print("   - 在平台上找到部署入口")
    print("   - 填写以下信息:")
    print(f"     * 仓库: {DEPLOY_CONFIG['repo_url']}")
    print(f"     * 服务名: {DEPLOY_CONFIG['service_name']}")
    print(f"     * 分支: {DEPLOY_CONFIG['branch']}")

    return 1

if __name__ == "__main__":
    sys.exit(main())
