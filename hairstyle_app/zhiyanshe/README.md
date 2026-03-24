# 智颜社小程序 - 项目说明

**项目名称**: 智颜社 AI Beauty Lab  
**版本**: 1.0.0  
**开发启动**: 2026-03-22  
**预计上线**: 2026-03-27

---

## 📁 项目结构

```
zhiyanshe/
├── README.md                    # 本文件
├── requirements.txt             # Python 依赖
├── .env                         # 环境配置
│
├── backend/                     # 后端服务
│   ├── app.py                  # Flask 主应用
│   ├── config.py               # 配置文件
│   ├── extensions.py           # 扩展初始化
│   │
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py             # 用户模型
│   │   ├── order.py            # 订单模型
│   │   ├── service.py          # 服务记录
│   │   └── referral.py         # 分销关系
│   │
│   ├── routes/                 # 路由
│   │   ├── __init__.py
│   │   ├── auth.py             # 认证路由
│   │   ├── shop.py             # 购买路由
│   │   ├── order.py            # 订单路由
│   │   ├── service.py          # 服务路由
│   │   └── referral.py         # 分销路由
│   │
│   ├── services/               # 业务逻辑
│   │   ├── __init__.py
│   │   ├── payment.py          # 支付服务
│   │   ├── hairstyle.py        # 发型生成
│   │   └── commission.py       # 提成计算
│   │
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       ├── wechat.py           # 微信工具
│       └── helpers.py          # 辅助函数
│
├── miniprogram/                # 小程序前端
│   ├── app.js                  # 小程序主程序
│   ├── app.json                # 小程序配置
│   ├── app.wxss                # 全局样式
│   │
│   ├── pages/                  # 页面
│   │   ├── index/              # 首页
│   │   ├── shop/               # 套餐购买
│   │   ├── order/              # 订单列表
│   │   ├── submit/             # 提交订单
│   │   ├── profile/            # 个人中心
│   │   └── referral/           # 分销中心
│   │
│   ├── components/             # 组件
│   │   ├── package-card/       # 套餐卡片
│   │   ├── order-item/         # 订单项
│   │   └── hairstyle-card/     # 发型卡片
│   │
│   └── utils/                  # 工具函数
│       ├── api.js              # API 请求
│       └── util.js             # 辅助函数
│
└── database/                   # 数据库
    └── zhiyanshe.db
```

---

## 🚀 快速开始

### 1. 后端启动

```bash
cd backend
pip install -r requirements.txt
python app.py
```

访问：http://localhost:5000

### 2. 小程序开发

```bash
# 使用微信开发者工具
# 导入 miniprogram 目录
# 配置 AppID
# 编译运行
```

---

## 📋 开发进度

| 模块 | 状态 | 完成度 |
|------|------|--------|
| 项目初始化 | ⏳ 待开始 | 0% |
| 数据库设计 | ⏳ 待开始 | 0% |
| 用户认证 | ⏳ 待开始 | 0% |
| 套餐购买 | ⏳ 待开始 | 0% |
| 支付接口 | ⏳ 待开始 | 0% |
| 订单管理 | ⏳ 待开始 | 0% |
| 分销系统 | ⏳ 待开始 | 0% |
| 小程序前端 | ⏳ 待开始 | 0% |
| 测试部署 | ⏳ 待开始 | 0% |

**预计完成**: 2026-03-27

---

## 📞 联系方式

**开发文档**: 查看各模块 README  
**问题反馈**: 在 GitHub 提 Issue

---

*最后更新：2026-03-22*
