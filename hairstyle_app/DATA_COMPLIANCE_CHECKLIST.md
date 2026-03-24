# 数据合规执行清单

**项目**: AI 发型生成系统  
**日期**: 2026-03-22  
**状态**: 🔄 进行中

---

## ✅ 已完成（技术层面）

### 1. TOS 自动删除机制

- [x] 创建清理脚本 `cleanup_tos_data.py`
- [x] 设置定时任务（每天凌晨 2 点）
- [x] 配置日志记录
- [x] 测试删除功能

**验证命令**：
```bash
# 手动执行一次验证
cd /root/.openclaw/workspace/hairstyle_app/backend
source venv/bin/activate
python3 cleanup_tos_data.py

# 查看定时任务
cat /etc/cron.d/hairstyle_cleanup

# 查看执行日志
tail -f /var/log/hairstyle_cleanup.log
```

---

### 2. 本地临时文件清理

- [x] 清理脚本已包含在 `cleanup_tos_data.py`
- [x] 清理目录：`/tmp/hairstyle_skill`、`/tmp/hairstyle_bot`
- [x] 清理策略：超过 1 小时自动删除

---

### 3. 文档准备

- [x] 用户隐私协议 `USER_DATA_PRIVACY_AGREEMENT.md`
- [x] 数据合规白皮书 `DATA_COMPLIANCE_WHITEPAPER.md`
- [x] 执行清单 `DATA_COMPLIANCE_CHECKLIST.md`

---

## ⏳ 待完成（法律层面）

### 1. 火山引擎数据保护确认

**优先级**: P0（最高）

**任务**：
- [ ] 联系火山引擎商务确认数据政策
- [ ] 获取书面确认（邮件/DPA）
- [ ] 确认关键条款：
  - [ ] 不用于模型训练
  - [ ] 24 小时内删除
  - [ ] 符合 PIPL 要求
  - [ ] 违约责任

**模板邮件**：
```
收件人：火山引擎商务合作 (ark@volcengine.com)
抄送：火山引擎法务 (legal@volcengine.com)
主题：关于 Doubao-Seedream API 数据使用政策的确认

您好，

我司 [公司名称] 计划商用火山引擎 Doubao-Seedream-4.5 API，
用于发型设计服务（toC 业务）。

为确保符合《个人信息保护法》要求，请确认以下事项：

【数据使用限制】
1. 用户上传的图片是否会被用于模型训练或优化？
2. 图片是否会被用于其他 AI 模型的训练？
3. 图片是否会与第三方共享？

【数据存储】
4. 图片在火山服务器的存储期限是多久？
5. 服务完成后是否会自动删除？
6. 是否有数据保留日志？

【合规保障】
7. 是否可以提供数据处理协议（DPA）？
8. 是否符合 GDPR/个人信息保护法要求？
9. 如发生数据泄露，贵司的响应流程是？

【技术支持】
10. 是否支持加密传输（HTTPS）？
11. 是否支持数据脱敏处理？
12. 是否有数据追溯机制？

盼复，谢谢！

此致
敬礼

[您的姓名]
[公司名称]
[联系方式]
[日期]
```

**预计完成时间**: 3-5 个工作日

---

### 2. 用户授权流程实现

**优先级**: P0

**任务**：
- [ ] 在网站/App 添加隐私协议勾选框
- [ ] 实现同意记录存储
- [ ] 实现授权撤回功能

**前端代码示例**：
```html
<!-- 用户上传前必须勾选 -->
<label>
  <input type="checkbox" id="privacy_agreement" required>
  我已阅读并同意 <a href="/privacy" target="_blank">《用户数据授权与隐私保护协议》</a>
</label>

<button onclick="uploadPhoto()" id="upload_btn" disabled>
  上传照片
</button>

<script>
document.getElementById('privacy_agreement').addEventListener('change', function() {
  document.getElementById('upload_btn').disabled = !this.checked;
});
</script>
```

**后端记录**：
```python
# 记录用户同意
def record_consent(user_id, ip_address, user_agent):
    consent_record = {
        "user_id": user_id,
        "agreement_version": "1.0.0",
        "agreed_at": datetime.now().isoformat(),
        "ip_address": ip_address,
        "user_agent": user_agent,
        "consent_items": [
            "data_collection",
            "data_processing",
            "third_party_transfer",
            "auto_deletion"
        ]
    }
    
    # 存储到数据库（保留 90 天）
    db.consent_records.insert_one(consent_record)
    
    return consent_record
```

**预计完成时间**: 1-2 个工作日

---

### 3. 公司注册与资质

**优先级**: P1

**任务**：
- [ ] 注册公司（个体工商户即可）
- [ ] 办理营业执照
- [ ] 开通对公账户
- [ ] 申请 ICP 备案（如需网站）

**推荐注册类型**：
```
类型：个体工商户 / 有限责任公司
注册资本：10-100 万（认缴）
经营范围：
  - 信息技术咨询服务
  - 个人形象设计服务
  - 软件开发
  - 互联网数据服务
```

**预计完成时间**: 5-10 个工作日

---

### 4. 数据安全保险

**优先级**: P2

**任务**：
- [ ] 咨询网络安全保险产品
- [ ] 评估保额需求（建议 100-500 万）
- [ ] 购买保险

**保险公司**：
- 平安产险：网络安全保险
- 人保财险：数据安全责任险
- 太保产险：网络安全责任险

**预计保费**: 1-5 万/年（根据保额）

---

## 📅 执行时间表

| 周次 | 任务 | 负责人 | 状态 |
|------|------|--------|------|
| **第 1 周** | 联系火山引擎确认数据政策 | [姓名] | ⏳ 待开始 |
| **第 1 周** | 实现用户授权流程 | [姓名] | ⏳ 待开始 |
| **第 2 周** | 测试 TOS 自动删除 | [姓名] | ⏳ 待开始 |
| **第 2 周** | 完成公司注册 | [姓名] | ⏳ 待开始 |
| **第 3 周** | 购买数据安全保险 | [姓名] | ⏳ 待开始 |
| **第 4 周** | 第一次合规审计 | [姓名] | ⏳ 待开始 |

---

## 🔍 验证测试

### 每周验证（自动化）

```bash
#!/bin/bash
# weekly_compliance_check.sh

echo "=== 数据合规周检 ==="
echo "日期：$(date)"

# 1. 检查 TOS 清理日志
echo -e "\n1. TOS 清理检查"
tail -n 20 /var/log/hairstyle_cleanup.log | grep "删除"

# 2. 检查临时文件
echo -e "\n2. 临时文件检查"
ls -lh /tmp/hairstyle_*/ 2>/dev/null || echo "无临时文件"

# 3. 检查授权记录
echo -e "\n3. 授权记录检查"
# (需要数据库查询)

# 4. 检查 API 调用日志
echo -e "\n4. API 调用检查"
# (需要查看火山引擎控制台)

echo -e "\n=== 检查完成 ==="
```

### 每月验证（人工）

**检查清单**：
- [ ] 查看 TOS 删除日志（是否正常运行）
- [ ] 抽查用户授权记录（是否完整）
- [ ] 查看火山引擎账单（是否有异常调用）
- [ ] 检查安全更新（是否有漏洞修复）
- [ ] 员工培训记录（是否完成）

---

## 📊 合规指标

| 指标 | 目标值 | 当前值 | 状态 |
|------|--------|--------|------|
| 原图删除率 | 100% | - | ⏳ 待监测 |
| 用户授权率 | 100% | - | ⏳ 待监测 |
| 数据泄露事件 | 0 | 0 | ✅ |
| 用户投诉 | <1% | - | ⏳ 待监测 |
| 合规审计通过率 | 100% | - | ⏳ 待监测 |

---

## 📞 紧急联系

**数据泄露应急**：
1. 立即停止数据收集
2. 通知数据保护官
3. 启动应急预案
4. 通知受影响用户
5. 报告监管部门

**联系方式**：
- 数据保护官：privacy@yourcompany.com
- 技术支持：tech@yourcompany.com
- 客服热线：[电话]

---

**最后更新**: 2026-03-22  
**下次审查**: 2026-03-29

---

*本清单为内部文件，定期更新*
