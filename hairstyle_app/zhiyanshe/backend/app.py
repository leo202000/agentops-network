#!/usr/bin/env python3
"""
智颜社后端服务
Flask API for 智颜社 AI Beauty Lab
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# 配置
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'zhiyanshe_secret_key_2026')
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'database', 'zhiyanshe.db')

# 内存数据库（临时用，后续改 SQLite）
users = {}  # user_id -> user_data
orders = {}  # order_id -> order_data
services = {}  # service_id -> service_data


# ============== 健康检查 ==============

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': '智颜社后端'
    })


# ============== 用户认证 ==============

@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录（微信登录）"""
    data = request.json
    code = data.get('code')  # 微信登录 code
    
    # TODO: 调用微信 API 获取 openid
    # 临时实现：生成测试用户
    user_id = f"user_{len(users) + 1}"
    
    if user_id not in users:
        users[user_id] = {
            'id': user_id,
            'openid': f"openid_{user_id}",
            'nickname': f"用户{user_id}",
            'avatar_url': '',
            'balance': 0,
            'total_times': 0,
            'used_times': 0,
            'created_at': datetime.now().isoformat()
        }
    
    return jsonify({
        'success': True,
        'user': users[user_id],
        'token': f"token_{user_id}"
    })


@app.route('/api/user/profile', methods=['GET'])
def get_profile():
    """获取用户信息"""
    user_id = request.headers.get('X-User-ID', 'user_1')
    
    if user_id not in users:
        return jsonify({'success': False, 'error': '用户不存在'}), 404
    
    user = users[user_id]
    return jsonify({
        'success': True,
        'user': {
            **user,
            'remaining_times': user['total_times'] - user['used_times']
        }
    })


# ============== 套餐购买 ==============

@app.route('/api/shop/packages', methods=['GET'])
def get_packages():
    """获取套餐列表"""
    packages = [
        {
            'id': 'package_3times',
            'name': '3 次卡',
            'price': 19.9,
            'times': 3,
            'unit_price': 6.6,
            'validity_days': 30,
            'recommended': False
        },
        {
            'id': 'package_10times',
            'name': '10 次卡',
            'price': 49.9,
            'times': 10,
            'unit_price': 5.0,
            'validity_days': 30,
            'recommended': True
        },
        {
            'id': 'package_30times',
            'name': '30 次卡',
            'price': 99.9,
            'times': 30,
            'unit_price': 3.3,
            'validity_days': 30,
            'recommended': False
        },
        {
            'id': 'recharge_100',
            'name': '充 100 送 20',
            'price': 100,
            'balance': 120,
            'validity_days': -1,  # 永久
            'recommended': False
        },
        {
            'id': 'recharge_300',
            'name': '充 300 送 80',
            'price': 300,
            'balance': 380,
            'validity_days': -1,
            'recommended': True
        },
        {
            'id': 'recharge_500',
            'name': '充 500 送 150',
            'price': 500,
            'balance': 650,
            'validity_days': -1,
            'recommended': False
        }
    ]
    
    return jsonify({
        'success': True,
        'packages': packages
    })


@app.route('/api/order/create', methods=['POST'])
def create_order():
    """创建订单"""
    data = request.json
    user_id = request.headers.get('X-User-ID', 'user_1')
    package_id = data.get('package_id')
    
    if not package_id:
        return jsonify({'success': False, 'error': '请选择套餐'}), 400
    
    # 生成订单号
    order_id = f"order_{len(orders) + 1}"
    
    # 临时实现：直接完成支付
    orders[order_id] = {
        'id': order_id,
        'user_id': user_id,
        'package_id': package_id,
        'status': 'paid',
        'created_at': datetime.now().isoformat(),
        'paid_at': datetime.now().isoformat()
    }
    
    # TODO: 调用支付接口
    
    return jsonify({
        'success': True,
        'order': orders[order_id]
    })


# ============== 服务提交 ==============

@app.route('/api/service/submit', methods=['POST'])
def submit_service():
    """提交发型设计请求"""
    data = request.json
    user_id = request.headers.get('X-User-ID', 'user_1')
    hairstyle_style = data.get('hairstyle_style')
    photo_url = data.get('photo_url')
    
    if not hairstyle_style or not photo_url:
        return jsonify({'success': False, 'error': '请提供发型风格和照片'}), 400
    
    # 检查用户次数
    user = users.get(user_id, {})
    remaining = user.get('total_times', 0) - user.get('used_times', 0)
    
    if remaining <= 0:
        return jsonify({
            'success': False,
            'error': '次数不足，请购买套餐'
        }), 403
    
    # 创建服务记录
    service_id = f"service_{len(services) + 1}"
    services[service_id] = {
        'id': service_id,
        'user_id': user_id,
        'hairstyle_style': hairstyle_style,
        'original_image': photo_url,
        'result_image': '',
        'status': 'pending',
        'created_at': datetime.now().isoformat()
    }
    
    # 扣除次数
    user['used_times'] = user.get('used_times', 0) + 1
    
    return jsonify({
        'success': True,
        'service': services[service_id]
    })


@app.route('/api/service/list', methods=['GET'])
def list_services():
    """获取服务记录列表"""
    user_id = request.headers.get('X-User-ID', 'user_1')
    
    user_services = [s for s in services.values() if s['user_id'] == user_id]
    
    return jsonify({
        'success': True,
        'services': user_services
    })


# ============== 分销系统 ==============

@app.route('/api/referral/code', methods=['GET'])
def get_referral_code():
    """获取推广码"""
    user_id = request.headers.get('X-User-ID', 'user_1')
    
    # 生成推广码
    referral_code = f"CODE{user_id}"
    
    return jsonify({
        'success': True,
        'referral_code': referral_code,
        'referral_url': f"https://zhiyanshe.com/?code={referral_code}"
    })


@app.route('/api/referral/stats', methods=['GET'])
def get_referral_stats():
    """获取分销统计"""
    user_id = request.headers.get('X-User-ID', 'user_1')
    
    # 临时数据
    stats = {
        'total_referrals': 0,
        'total_commission': 0,
        'withdrawn_commission': 0,
        'available_commission': 0
    }
    
    return jsonify({
        'success': True,
        'stats': stats
    })


# ============== 管理员接口 ==============

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    """管理员统计"""
    stats = {
        'total_users': len(users),
        'total_orders': len(orders),
        'total_services': len(services),
        'today_orders': 0,
        'today_revenue': 0
    }
    
    return jsonify({
        'success': True,
        'stats': stats
    })


# ============== 启动服务 ==============

if __name__ == '__main__':
    print("=" * 60)
    print("智颜社后端服务启动")
    print("=" * 60)
    print(f"服务地址：http://localhost:5000")
    print(f"健康检查：http://localhost:5000/health")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
