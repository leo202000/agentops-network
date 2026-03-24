# 全链路数据安全保障方案

**项目**: AI 发型生成系统  
**版本**: 1.0.0  
**日期**: 2026-03-22  
**密级**: 内部保密

---

## 📊 数据流转全景图

```
┌─────────────┐      HTTPS      ┌─────────────┐      HTTPS      ┌─────────────┐
│   用户设备   │ ──────────────→ │  平台服务器  │ ──────────────→ │ 火山 API    │
│             │   TLS 1.3 加密   │             │   TLS 1.3 加密   │             │
└─────────────┘                 └─────────────┘                 └─────────────┘
     │                               │                                  │
     │ 本地加密                      │ 内存处理                         │ 24 小时自动删除
     │                               │                                  │
     ↓                               ↓                                  ↓
┌─────────────┐                 ┌─────────────┐                 ┌─────────────┐
│  用户存储    │                 │  TOS 存储     │                 │  结果存储    │
│             │                 │             │                 │             │
│ 原图 (私有)  │                 │ 原图 (24h)   │                 │ 结果 (永久)  │
└─────────────┘                 └─────────────┘                 └─────────────┘
```

---

## 一、传输安全（端到端加密）

### 1.1 传输链路分析

| 链路 | 协议 | 加密方式 | 风险等级 |
|------|------|---------|---------|
| 用户 → 平台 | HTTPS | TLS 1.3 | ✅ 低 |
| 平台 → TOS | HTTPS | TLS 1.3 | ✅ 低 |
| TOS → 火山 API | HTTPS | TLS 1.3 | ✅ 低 |
| 火山 API → 平台 | HTTPS | TLS 1.3 | ✅ 低 |

### 1.2 技术实现

**强制 HTTPS 传输**：
```python
import requests
import ssl

# 配置 SSL 验证
session = requests.Session()
session.verify = True  # 验证服务器证书
session.mount('https://', requests.adapters.HTTPAdapter(
    ssl_context=ssl.create_default_context()
))

# 所有请求必须 HTTPS
def upload_to_tos(image_path: str) -> str:
    response = session.post(
        'https://tos-cn-beijing.volces.com/...',  # 强制 HTTPS
        files={'file': open(image_path, 'rb')},
        timeout=30
    )
    response.raise_for_status()
    return response.json()['url']
```

**证书绑定**（防止中间人攻击）：
```python
# 绑定火山引擎证书指纹
VOLCENGINE_CERT_FINGERPRINT = "SHA256:xx:xx:xx:..."

def verify_certificate(cert):
    fingerprint = ssl.get_server_certificate(('ark.cn-beijing.volces.com', 443))
    if fingerprint not in VOLCENGINE_CERT_FINGERPRINT:
        raise SecurityError("证书指纹不匹配，可能存在中间人攻击")
```

### 1.3 传输监控

**异常检测**：
```python
# 监控传输异常
def monitor_transfer():
    metrics = {
        'failed_transfers': 0,
        'timeout_count': 0,
        'cert_errors': 0,
    }
    
    # 告警阈值
    if metrics['failed_transfers'] > 10:  # 连续失败 10 次
        send_alert("传输失败率异常")
    
    if metrics['cert_errors'] > 0:  # 证书错误
        send_alert("证书验证失败，可能存在攻击", level='CRITICAL')
```

---

## 二、火山引擎临时存储安全

### 2.1 存储机制分析

**火山引擎数据处理流程**：
```
接收图片 → 内存加载 → GPU 处理 → 生成结果 → 返回 → 清理内存
     ↓                                              ↓
  临时缓存 (可选)                              24 小时自动删除
```

### 2.2 风险评估

| 风险点 | 可能性 | 影响程度 | 缓解措施 |
|--------|--------|---------|---------|
| 数据用于训练 | 低 | 高 | DPA 协议 + 法律约束 |
| 内部人员访问 | 低 | 高 | 审计日志 + 追溯机制 |
| 第三方泄露 | 低 | 高 | 保险 + 合同约束 |
| 未及时删除 | 中 | 中 | 定期审计 + 对账 |

### 2.3 技术保障

**方案 A：数字水印追溯**
```python
from stegano import lsb
import hashlib

def add_invisible_watermark(image_path: str, user_id: str) -> str:
    """
    添加不可见数字水印
    用于数据泄露时的来源追溯
    """
    # 生成追溯信息
    trace_info = f"user:{user_id}|time:{timestamp}|session:{session_id}"
    
    # 使用 LSB 算法嵌入水印（不影响视觉效果）
    secret = lsb.hide(image_path, trace_info)
    
    # 保存水印图片
    watermarked_path = f"/tmp/watermarked_{user_id}.jpg"
    secret.save(watermarked_path)
    
    # 记录水印信息（用于后续验证）
    watermark_record = {
        'user_id': user_id,
        'timestamp': timestamp,
        'hash': hashlib.sha256(trace_info.encode()).hexdigest(),
        'image_path': watermarked_path
    }
    
    # 存储到安全数据库（保留 90 天）
    db.watermark_records.insert_one(watermark_record)
    
    return watermarked_path

# 泄露追溯
def trace_leaked_image(leaked_image_path: str) -> dict:
    """从泄露图片中提取水印信息"""
    secret = lsb.reveal(leaked_image_path)
    # 解析 trace_info，定位泄露源
    return parse_trace_info(secret)
```

**方案 B：图片脱敏处理**
```python
import cv2
import numpy as np

def crop_to_face_only(image_path: str) -> str:
    """
    裁剪为仅人脸区域
    减少身体特征等敏感信息暴露
    """
    img = cv2.imread(image_path)
    
    # 人脸检测
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    faces = face_cascade.detectMultiScale(img, 1.3, 5)
    
    if len(faces) > 0:
        x, y, w, h = faces[0]
        # 保留头发区域（发型生成需要）
        margin = 150  # 向上扩展 150px 保留头发
        face_only = img[max(0, y-margin):y+h, x:x+w]
        
        # 保存裁剪后的图片
        cropped_path = f"/tmp/cropped_{user_id}.jpg"
        cv2.imwrite(cropped_path, face_only)
        
        return cropped_path
    
    return image_path  # 检测失败返回原图
```

**方案 C：元数据清除**
```python
from PIL import Image
from PIL.ExifTags import TAGS

def strip_metadata(image_path: str) -> str:
    """
    清除 EXIF 元数据（包含拍摄时间、地点、设备等信息）
    """
    image = Image.open(image_path)
    
    # 保存为无元数据的新文件
    clean_path = f"/tmp/clean_{user_id}.jpg"
    
    # 提取图像数据
    data = list(image.getdata())
    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(data)
    
    # 保存（不保留 EXIF）
    image_without_exif.save(clean_path, "JPEG")
    
    return clean_path
```

### 2.4 火山引擎对账机制

**每日对账脚本**：
```python
#!/usr/bin/env python3
"""
火山引擎 API 调用对账
确保所有调用都有对应记录，无异常调用
"""

def daily_reconciliation():
    """每日对账"""
    
    # 1. 获取本地调用记录
    local_logs = db.api_calls.find({
        'date': yesterday
    })
    
    # 2. 获取火山引擎账单/使用记录
    volc_usage = get_volcengine_usage(yesterday)
    
    # 3. 对比
    local_count = len(local_logs)
    volc_count = volc_usage['total_calls']
    
    if abs(local_count - volc_count) > 5:  # 允许 5 次误差
        send_alert(
            f"API 调用对账失败：本地{local_count} vs 火山{volc_count}",
            level='WARNING'
        )
    
    # 4. 检查异常调用
    for call in volc_usage['details']:
        if call['image_hash'] not in local_hashes:
            send_alert(
                f"发现未授权的 API 调用：{call['image_hash']}",
                level='CRITICAL'
            )
```

---

## 三、TOS 存储安全

### 3.1 存储架构

```
TOS Bucket: hairfashon (私有)
│
├── hairstyle/                    # 用户原图（24 小时删除）
│   ├── 20260322/user123_photo.jpg
│   │   └── ACL: 私有（仅服务账号可访问）
│   └── ...
│
└── hairstyle/results/            # 生成结果（用户所有）
    ├── 20260322/user123_result.jpg
    │   └── ACL: 公共读（仅持有人可访问链接）
    └── ...
```

### 3.2 访问控制

**Bucket 策略**：
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowServiceAccount",
      "Effect": "Allow",
      "Principal": {
        "AWS": ["arn:tos:iam::123456:user/hairstyle-service"]
      },
      "Action": [
        "tos:PutObject",
        "tos:GetObject",
        "tos:DeleteObject"
      ],
      "Resource": ["arn:tos:*:*:hairfashon/hairstyle/*"]
    },
    {
      "Sid": "PublicReadForResults",
      "Effect": "Allow",
      "Principal": {"AWS": ["*"]},
      "Action": ["tos:GetObject"],
      "Resource": ["arn:tos:*:*:hairfashon/hairstyle/results/*"],
      "Condition": {
        "StringLike": {"tos:prefix": "hairstyle/results/*"}
      }
    }
  ]
}
```

**访问日志审计**：
```python
def audit_tos_access():
    """审计 TOS 访问日志"""
    
    # 获取访问日志
    logs = get_tos_access_logs(bucket='hairfashon', hours=24)
    
    # 检查异常访问
    anomalies = []
    
    for log in logs:
        # 非服务账号访问原图目录
        if log['principal'] != 'hairstyle-service':
            if 'hairstyle/' in log['key'] and 'results/' not in log['key']:
                anomalies.append({
                    'type': 'unauthorized_access',
                    'principal': log['principal'],
                    'key': log['key'],
                    'time': log['time']
                })
        
        # 高频访问
        if log['request_count'] > 1000:
            anomalies.append({
                'type': 'high_frequency_access',
                'principal': log['principal'],
                'count': log['request_count']
            })
    
    # 告警
    if anomalies:
        send_alert(f"发现 {len(anomalies)} 起异常访问", anomalies)
```

### 3.3 加密存储

**服务端加密**（SSE）：
```python
from tos import TosClientV2, ServerSideEncryption

client = TosClientV2(
    ak=TOS_ACCESS_KEY,
    sk=TOS_SECRET_KEY,
    region=TOS_REGION
)

# 启用服务端加密
client.put_bucket_encryption(
    bucket=TOS_BUCKET,
    server_side_encryption=ServerSideEncryption(
        sse_algorithm='AES256'  # AES-256 加密
    )
)
```

**客户端加密**（可选，更高安全）：
```python
from cryptography.fernet import Fernet

class EncryptedUploader:
    def __init__(self, encryption_key: str):
        self.cipher = Fernet(encryption_key)
    
    def upload_encrypted(self, image_path: str, tos_key: str):
        """加密后上传"""
        
        # 读取并加密
        with open(image_path, 'rb') as f:
            data = f.read()
        
        encrypted_data = self.cipher.encrypt(data)
        
        # 上传加密数据
        client.put_object(
            bucket=TOS_BUCKET,
            key=tos_key,
            content=encrypted_data
        )
        
        # 密钥单独存储（HSM 或密钥管理服务）
        store_key_reference(tos_key, self.cipher)
```

### 3.4 自动删除验证

**删除确认机制**：
```python
def verify_deletion():
    """验证 24 小时前的文件是否已删除"""
    
    # 获取 24 小时前的文件列表
    cutoff_time = datetime.now() - timedelta(hours=24)
    
    old_files = client.list_objects(
        bucket=TOS_BUCKET,
        prefix='hairstyle/',
        delimiter='/'
    )
    
    # 检查是否还有原图（不应有）
    for obj in old_files.get('contents', []):
        if obj['lastModified'] < cutoff_time:
            if 'results/' not in obj['key']:
                # 发现未删除的原图
                send_alert(
                    f"发现未删除的原图：{obj['key']}",
                    level='WARNING'
                )
                
                # 手动删除
                client.delete_object(
                    bucket=TOS_BUCKET,
                    key=obj['key']
                )
```

---

## 四、本地服务器安全

### 4.1 文件权限

```bash
# 敏感文件权限设置
chmod 600 /root/.openclaw/workspace/.env          # 仅 root 可读写
chmod 600 /root/.openclaw/workspace/*.key         # 密钥文件
chmod 700 /root/.openclaw/workspace/hairstyle_app # 仅 root 可访问

# 临时目录权限
chmod 1777 /tmp/hairstyle_skill                    # sticky bit
```

### 4.2 临时文件清理

**已实现**：
- `cleanup_tos_data.py` - 每天凌晨 2 点执行
- 清理策略：超过 1 小时的临时文件自动删除
- 清理目录：`/tmp/hairstyle_skill`、`/tmp/hairstyle_bot`

**验证**：
```bash
# 查看清理日志
tail -f /var/log/hairstyle_cleanup.log

# 检查临时目录
ls -lh /tmp/hairstyle_*/
```

### 4.3 服务器加固

**基础加固**：
```bash
# 1. 禁用 root SSH 登录
echo "PermitRootLogin no" >> /etc/ssh/sshd_config

# 2. 启用防火墙
ufw enable
ufw allow 22/tcp    # SSH
ufw allow 443/tcp   # HTTPS
ufw default deny    # 默认拒绝

# 3. 安装入侵检测
apt install fail2ban
systemctl enable fail2ban

# 4. 定期更新
apt update && apt upgrade -y
```

**安全审计**：
```bash
# 安装审计工具
apt install lynis

# 每周执行安全审计
0 3 * * 0 root lynis audit system >> /var/log/lynis_audit.log 2>&1
```

---

## 五、监控与告警

### 5.1 监控指标

| 指标 | 阈值 | 告警级别 |
|------|------|---------|
| API 调用失败率 | >5% | WARNING |
| 证书验证失败 | >0 | CRITICAL |
| 未授权访问 | >0 | CRITICAL |
| 删除失败 | >0 | WARNING |
| 临时文件堆积 | >100 个 | WARNING |

### 5.2 告警渠道

```python
def send_alert(message: str, level: str = 'INFO'):
    """发送告警"""
    
    channels = {
        'INFO': ['log'],
        'WARNING': ['log', 'email'],
        'CRITICAL': ['log', 'email', 'sms', 'phone']
    }
    
    for channel in channels.get(level, ['log']):
        if channel == 'log':
            logger.warning(f"[{level}] {message}")
        elif channel == 'email':
            send_email('security@yourcompany.com', message)
        elif channel == 'sms':
            send_sms('+86-xxx-xxxx-xxxx', message)
        elif channel == 'phone':
            call_phone('+86-xxx-xxxx-xxxx', message)
```

---

## 六、安全事件应急响应

### 6.1 事件分级

| 级别 | 定义 | 响应时限 | 通知对象 |
|------|------|---------|---------|
| P0 | 数据泄露 >1 万条 | 立即 | CEO + 监管 + 用户 |
| P1 | 数据泄露 <1 万条 | 1 小时 | CTO + 法务 |
| P2 | 未遂攻击 | 4 小时 | 安全团队 |
| P3 | 异常访问 | 24 小时 | 运维团队 |

### 6.2 响应流程

```
发现事件
    ↓
初步评估（15 分钟）
    ↓
启动应急预案
    ↓
┌───────────────────┐
│ 技术组：阻断攻击   │
│ 法务组：评估责任   │
│ 公关组：准备声明   │
└───────────────────┘
    ↓
通知用户（24 小时内）
    ↓
报告监管（72 小时内）
    ↓
调查原因 → 整改 → 复盘
```

---

## 七、合规审计

### 7.1 审计频率

| 审计类型 | 频率 | 执行方 |
|---------|------|--------|
| 自动化检查 | 每日 | 系统自动 |
| 人工审查 | 每周 | 安全团队 |
| 内部审计 | 每月 | 数据保护官 |
| 第三方审计 | 每年 | 外部机构 |

### 7.2 审计清单

**每日自动化检查**：
- [ ] TOS 删除任务是否执行
- [ ] 临时文件是否清理
- [ ] API 调用是否异常
- [ ] 访问日志是否有异常

**每周人工审查**：
- [ ] 查看告警日志
- [ ] 检查权限变更
- [ ] 审查新增用户
- [ ] 验证备份完整性

**每月内部审计**：
- [ ] 数据保护政策执行
- [ ] 员工培训完成情况
- [ ] 第三方合规状态
- [ ] 安全事件复盘

---

## 八、保险与责任

### 8.1 数据安全保险

**推荐产品**：
- 平安产险：网络安全保险（保额 100-500 万）
- 人保财险：数据安全责任险
- 太保产险：网络安全责任险

**保障范围**：
- 数据泄露赔偿
- 法律诉讼费用
- 公关危机处理
- 业务中断损失

**保费估算**：1-5 万/年

### 8.2 责任限制

**用户协议条款**：
```
8.1 责任限制
在法律法规允许的最大范围内，平台对因以下原因导致的数据泄露不承担责任：
(a) 用户自身原因（如密码泄露、设备丢失）
(b) 不可抗力（如自然灾害、战争）
(c) 第三方攻击（已采取合理安全措施的情况下）

8.2 赔偿上限
平台的累计赔偿责任不超过用户过去 12 个月支付的服务费用总额。
```

---

## 九、执行清单

### 立即执行（本周）

- [x] 测试清理脚本 ✅
- [ ] 联系火山引擎确认数据政策
- [ ] 启用 TOS 访问日志
- [ ] 配置安全告警

### 短期执行（1 个月内）

- [ ] 实现数字水印追溯
- [ ] 购买数据安全保险
- [ ] 第一次安全审计
- [ ] 员工安全培训

### 中期执行（3 个月内）

- [ ] 第三方安全评估
- [ ] 渗透测试
- [ ] 合规认证（ISO 27001）
- [ ] 应急预案演练

---

**批准人**: _______________  
**职位**: 首席安全官 (CSO)  
**日期**: 2026-03-22

---

*本方案为内部保密文件，未经授权不得对外公开*
