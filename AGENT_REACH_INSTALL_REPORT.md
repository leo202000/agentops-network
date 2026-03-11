# Agent Reach 安装报告

**安装时间**: 2026-03-11 08:19 AM  
**版本**: agent-reach 1.3.0  
**环境**: Server/VPS (auto-detected)

## ✅ 已安装组件

| 组件 | 状态 | 位置 |
|------|------|------|
| agent-reach | ✅ | /usr/local/lib/python3.12/dist-packages |
| mcporter | ✅ | /usr/local/bin |
| xreach | ✅ | /usr/bin |
| yt-dlp | ✅ | /usr/local/bin |
| gh CLI | ✅ | /usr/bin |
| Node.js | ✅ | /usr/bin |
| undici | ✅ | npm global |
| douyin-mcp-server | ✅ | ~/.agent-reach/tools/douyin-mcp-server |

## ✅ 已配置 MCP 服务

| 服务 | 地址 | 状态 |
|------|------|------|
| **Exa 搜索** | `https://mcp.exa.ai/mcp` | ✅ 可用 |
| **微博** | `mcp-server-weibo` | ⚠️ 待修复 |
| **小红书** | `http://localhost:18060/mcp` | ✅ 运行中 (Docker) |
| **抖音** | `http://localhost:18070/mcp` | ✅ 运行中 |

## 📊 当前状态

**可用渠道**: 8/14

### ✅ 立即可用

1. **GitHub** - gh CLI 已安装（需认证解锁完整功能）
2. **YouTube** - 视频信息和字幕提取
3. **RSS/Atom** - 订阅源读取
4. **全网搜索** - Exa 语义搜索
5. **任意网页** - Jina Reader (curl https://r.jina.ai/URL)
6. **Twitter/X** - 推文读取和搜索
7. **B 站** - 视频信息和字幕提取
8. **小红书** - 笔记搜索、阅读、发帖、评论、点赞
9. **抖音** - 视频解析、无水印下载链接

### ⚠️ 需要配置

1. **Reddit** - 需要代理避免 IP 封锁
2. **微博** - MCP 工具加载失败，需修复
3. **Twitter 认证** - 需要 Cookie 解锁搜索和发帖

### 🔒 可选扩展（按需安装）

| 平台 | 安装命令 |
|------|----------|
| LinkedIn | `pip install linkedin-scraper-mcp` |
| Boss 直聘 | `git clone https://github.com/mucsbr/mcp-bosszp.git` |
| 微信公众号 | `pip install camoufox[geoip] markdownify beautifulsoup4 httpx mcp` |
| 小宇宙播客 | `agent-reach configure groq-key gsk_xxx` |

## 📝 配置文件位置

- **mcporter 配置**: `/root/.openclaw/workspace/config/mcporter.json`
- **Agent Reach 配置**: `~/.agent-reach/config.json`
- **小红书服务**: Docker 容器 `xiaohongshu-mcp` (端口 18060)
- **抖音服务**: `~/.agent-reach/tools/douyin-mcp-server` (端口 18070)

## 🚀 使用示例

```bash
# 小红书搜索笔记
mcporter call 'xiaohongshu.search_feeds(keyword="AI", limit=10)'

# 小红书获取笔记详情
mcporter call 'xiaohongshu.get_note_detail(note_id="xxx")'

# 抖音视频解析
mcporter call 'douyin.parse_douyin_video_info(video_url="https://v.douyin.com/xxx")'

# Twitter 搜索
xreach search "AI agent" -n 10

# YouTube 视频信息
yt-dlp --dump-json "https://youtube.com/watch?v=xxx"

# 网页读取
curl -s "https://r.jina.ai/https://example.com"

# Exa 语义搜索
mcporter call 'exa.web_search_exa(query="AI agents", num_results=10)'
```

## 🐳 Docker 容器管理

```bash
# 查看小红书容器状态
docker ps | grep xiaohongshu

# 重启小红书服务
docker restart xiaohongshu-mcp

# 查看日志
docker logs xiaohongshu-mcp --tail 50

# 停止服务
docker stop xiaohongshu-mcp
```

## 🔧 后续优化

1. **GitHub 认证**: `gh auth login`
2. **Twitter Cookie**: `agent-reach configure twitter-cookies "Cookie 字符串"`
3. **代理配置**: `agent-reach configure proxy http://user:pass@ip:port`
4. **微博修复**: 检查 mcp-server-weibo 版本兼容性

---

**安装完成！** 8/14 渠道已可用，其余可按需扩展。
