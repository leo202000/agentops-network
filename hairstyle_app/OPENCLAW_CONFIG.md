# 发型 AI 助手 - OpenClaw 配置

## 工具配置

### 1. 图片上传工具（OSS/Cloudinary）

```json
{
  "name": "upload_image",
  "type": "http",
  "method": "POST",
  "url": "http://localhost:8000/upload",
  "body": {
    "image": "{{input.image}}"
  }
}
```

### 2. 发型生成工具（即梦 API）

```json
{
  "name": "generate_hairstyle",
  "type": "http",
  "method": "POST",
  "url": "http://localhost:8000/generate-hairstyle",
  "body": {
    "user_image": "{{input.image_url}}",
    "style": "{{input.style}}",
    "reference_image": "{{input.ref_image}}"
  }
}
```

### 3. 批量生成工具（对比图）

```json
{
  "name": "generate_batch",
  "type": "http",
  "method": "POST",
  "url": "http://localhost:8000/generate-batch",
  "body": {
    "user_image": "{{input.image_url}}",
    "styles": ["短发", "卷发", "中分", "长发"]
  }
}
```

## Agent 配置

```json
{
  "name": "hairstyle_bot",
  "description": "AI 发型生成助手 - 帮助用户尝试不同发型",
  "prompt": "你是专业的发型顾问。当用户上传图片时：\n1. 询问想要的发型风格\n2. 或推荐适合用户脸型的发型\n3. 调用 generate_hairstyle 生成\n4. 提供专业建议\n\n支持：\n- 短发、卷发、中分、长发\n- 上传参考发型图\n- 批量生成对比",
  "tools": ["upload_image", "generate_hairstyle", "generate_batch"]
}
```

## 使用示例

### 用户输入
```
帮我换成短发
[上传图片]
```

### Agent 流程
1. 识别意图：换发型 → 短发
2. 上传图片 → 获取 URL
3. 调用 generate_hairstyle
4. 返回生成结果

### 批量生成
```
帮我试试不同发型
[上传图片]
```

→ 生成 4 种发型对比图
