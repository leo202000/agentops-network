# 智颜社小程序开发计划

**版本**: 1.0  
**开发周期**: 5 天  
**上线时间**: 2026-03-27

---

## 📋 功能清单

### 阶段 1: MVP（3 天）

**核心功能**：
- [ ] 用户注册/登录（微信一键登录）
- [ ] 套餐购买（3 次/10 次/30 次）
- [ ] 支付接口（微信支付）
- [ ] 次数查询
- [ ] 提交订单（上传照片）
- [ ] 订单状态查询
- [ ] 管理员后台

**技术栈**：
- 前端：微信小程序（原生）
- 后端：Python Flask/FastAPI
- 数据库：SQLite（初期）/MySQL（后期）
- 部署：腾讯云/阿里云

---

### 阶段 2: 充值功能（1 天）

- [ ] 充值套餐（充 100 送 20 等）
- [ ] 余额查询
- [ ] 消费记录
- [ ] 积分系统

---

### 阶段 3: 分销系统（1 天）

- [ ] 推广码生成
- [ ] 分享关系绑定
- [ ] 提成计算
- [ ] 提现申请
- [ ] 数据看板

---

## 📁 项目结构

```
zhiyanshe-miniprogram/
├── miniprogram/              # 小程序前端
│   ├── pages/
│   │   ├── index/           # 首页
│   │   ├── shop/            # 套餐购买
│   │   ├── order/           # 订单列表
│   │   ├── submit/          # 提交订单
│   │   ├── profile/         # 个人中心
│   │   └──分销 /            # 分销中心
│   ├── components/          # 组件
│   ├── utils/               # 工具函数
│   └── app.js               # 主程序
│
├── backend/                 # 后端服务
│   ├── app.py              # Flask 应用
│   ├── models/             # 数据模型
│   ├── routes/             # 路由
│   ├── services/           # 业务逻辑
│   └── config.py           # 配置
│
└── database/               # 数据库
    └── zhiyanshe.db
```

---

## 🗄️ 数据库设计

### 用户表（users）

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    openid VARCHAR(64) UNIQUE NOT NULL,
    nickname VARCHAR(64),
    avatar_url VARCHAR(255),
    phone VARCHAR(20),
    balance DECIMAL(10,2) DEFAULT 0,
    total_times INTEGER DEFAULT 0,
    used_times INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 订单表（orders）

```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_no VARCHAR(32) UNIQUE NOT NULL,
    package_type VARCHAR(32) NOT NULL, -- 3 次卡/10 次卡/30 次卡/充值
    amount DECIMAL(10,2) NOT NULL,
    times INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending/paid/completed/refunded
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 服务记录表（services）

```sql
CREATE TABLE services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_id INTEGER,
    original_image VARCHAR(255),
    hairstyle_style VARCHAR(64),
    result_image VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending', -- pending/processing/completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 分销关系表（referrals）

```sql
CREATE TABLE referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    referrer_id INTEGER,
    referral_code VARCHAR(16) UNIQUE,
    commission_rate DECIMAL(5,2) DEFAULT 0.10,
    total_commission DECIMAL(10,2) DEFAULT 0,
    withdrawn_commission DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (referrer_id) REFERENCES users(id)
);
```

---

## 🎨 页面设计

### 首页

```
┌─────────────────────────┐
│   智颜社 AI Beauty Lab   │
│   用 AI，遇见更美的自己    │
├─────────────────────────┤
│  [免费体验] [购买套餐]    │
│  [我的订单] [个人中心]    │
├─────────────────────────┤
│  热门发型推荐            │
│  [对比图轮播]            │
├─────────────────────────┤
│  用户好评                │
│  [评价卡片]              │
└─────────────────────────┘
```

### 套餐购买页

```
┌─────────────────────────┐
│      选择套餐            │
├─────────────────────────┤
│  [3 次卡]  19.9 元        │
│   6.6 元/次              │
│   [立即购买]             │
├─────────────────────────┤
│  [10 次卡] 49.9 元 ⭐推荐  │
│   5 元/次                │
│   [立即购买]             │
├─────────────────────────┤
│  [30 次卡] 99.9 元        │
│   3.3 元/次              │
│   [立即购买]             │
├─────────────────────────┤
│  [充 100 送 20]           │
│  [充 300 送 80] ⭐推荐      │
│  [充 500 送 150]          │
└─────────────────────────┘
```

### 个人中心

```
┌─────────────────────────┐
│  👤 小美                │
│  剩余次数：7 次          │
│  余额：120 元            │
├─────────────────────────┤
│  [我的订单] [服务记录]    │
│  [分销中心] [联系客服]    │
│  [设置]                 │
└─────────────────────────┘
```

---

## 💰 成本估算

### 开发成本

| 项目 | 费用 | 说明 |
|------|------|------|
| 域名 | 50 元/年 | 阿里云/腾讯云 |
| 服务器 | 100 元/月 | 2 核 4G |
| 数据库 | 50 元/月 | 云数据库 |
| 微信小程序认证 | 300 元/年 | 腾讯官方 |
| 微信支付费率 | 0.6% | 交易金额 |
| **合计** | **约 500 元/月** | - |

### 开发时间

| 阶段 | 时间 | 功能 |
|------|------|------|
| 阶段 1 | 3 天 | 核心功能 |
| 阶段 2 | 1 天 | 充值功能 |
| 阶段 3 | 1 天 | 分销系统 |
| 测试 | 1 天 | Bug 修复 |
| **合计** | **6 天** | - |

---

## 🚀 开发计划

### Day 1（3/23）

- [ ] 项目初始化
- [ ] 数据库设计
- [ ] 用户登录接口
- [ ] 小程序首页

### Day 2（3/24）

- [ ] 套餐购买接口
- [ ] 支付接口对接
- [ ] 订单创建
- [ ] 小程序购买页

### Day 3（3/25）

- [ ] 服务提交接口
- [ ] 订单查询
- [ ] 次数扣除
- [ ] 小程序订单页

### Day 4（3/26）

- [ ] 充值功能
- [ ] 分销系统
- [ ] 数据看板
- [ ] 小程序个人中心

### Day 5（3/27）

- [ ] 测试修复
- [ ] 性能优化
- [ ] 提交审核
- [ ] 准备上线

---

## 📞 上线检查清单

- [ ] 域名备案
- [ ] SSL 证书
- [ ] 服务器部署
- [ ] 数据库备份
- [ ] 支付测试
- [ ] 小程序提交审核
- [ ] 客服培训
- [ ] 用户手册

---

*最后更新：2026-03-22*
