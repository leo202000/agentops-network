# 🎨 客户指定发型功能

**需求**: 客户提供指定发型图片 → AI 生成同款发型  
**状态**: 📋 需求确认 → 🔧 实施中

---

## 📊 功能说明

### 用户流程

```
1. 用户上传自己的照片
   ↓
2. 上传想要的发型参考图（明星/网红/朋友）
   ↓
3. AI 分析参考图发型特征
   ↓
4. 生成用户 + 参考发型的合成效果
   ↓
5. 用户预览并确认
```

---

## 🛠️ 技术实现方案

### 方案 A：基于提示词反推 ⭐ 推荐

**流程**:
```
参考图 → AI 分析 → 提取发型特征 → 生成提示词 → 调用生成 API
```

**优点**:
- ✅ 复用现有 Doubao-Seedream-4.5 API
- ✅ 无需额外训练模型
- ✅ 实施简单快速

**缺点**:
- ⚠️ 相似度 80-90%（非 100% 精确）

---

### 方案 B：IP-Adapter 精确复制

**流程**:
```
参考图 → IP-Adapter 提取特征 → ControlNet 控制 → 生成同款
```

**优点**:
- ✅ 相似度 95%+（高度精确）

**缺点**:
- ⚠️ 需要额外部署模型
- ⚠️ 实施复杂度高
- ⚠️ 计算资源需求大

---

### 推荐方案：方案 A（快速实施）

**理由**:
1. 快速上线验证需求
2. 成本低，风险小
3. 80-90% 相似度已满足大部分需求
4. 后续可升级到方案 B

---

## 💻 实施代码

### 1. 发型分析模块

```python
# hairstyle_analyzer.py
from openai import OpenAI

class HairstyleAnalyzer:
    """发型分析器 - 从参考图提取发型特征"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=api_key
        )
        self.model = "doubao-seedream-4-5-251128"
    
    def analyze_hairstyle(self, reference_image_url: str) -> dict:
        """
        分析参考图的发型特征
        
        Args:
            reference_image_url: 参考图 URL
        
        Returns:
            发型特征描述
        """
        # 使用多模态模型分析图片
        response = self.client.chat.completions.create(
            model="doubao-vision-pro-32k",  # 视觉分析模型
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "请详细分析这张图片中的发型特征，包括：1.长度（短发/齐肩/长发）2.卷度（直发/微卷/大卷/小卷）3.刘海（无/空气/斜/齐）4.发色 5.造型（披发/马尾/丸子等）6.其他特征。请用中文描述，100 字以内。"},
                    {"type": "image_url", "image_url": {"url": reference_image_url}}
                ]
            }]
        )
        
        description = response.choices[0].message.content
        
        # 提取关键词生成提示词
        prompt = self._generate_prompt(description)
        
        return {
            'success': True,
            'description': description,
            'prompt': prompt,
            'reference_url': reference_image_url
        }
    
    def _generate_prompt(self, description: str) -> str:
        """根据描述生成 AI 绘画提示词"""
        # 简单映射
        prompt = f"保持人物脸部完全一致，只改变发型为：{description}, realistic photo, high quality"
        return prompt
```

---

### 2. 集成到生成器

```python
# hairstyle_generator.py 新增方法
def generate_custom_style(
    self,
    user_photo_path: str,
    reference_photo_path: str
) -> dict:
    """
    生成客户指定发型
    
    Args:
        user_photo_path: 用户照片
        reference_photo_path: 参考发型照片
    
    Returns:
        生成结果
    """
    # 1. 上传参考图到 TOS
    ref_url = self.upload_image(reference_photo_path)
    
    # 2. 分析参考图发型
    analyzer = HairstyleAnalyzer(self.api_key)
    analysis = analyzer.analyze_hairstyle(ref_url)
    
    if not analysis['success']:
        return {'error': '发型分析失败'}
    
    # 3. 使用分析结果生成
    result = self.generate_with_prompt(
        image_path=user_photo_path,
        prompt=analysis['prompt']
    )
    
    return {
        'success': True,
        'analysis': analysis['description'],
        'result': result
    }
```

---

## 💰 定价策略

### 收费模式

| 服务 | 价格 | 说明 |
|------|------|------|
| 标准发型（15-25 种） | 包含在套餐内 | 使用预设发型 |
| **指定发型（AI 分析）** | **¥5/次** | 额外收费服务 |
| **指定发型（精确复制）** | **¥10/次** | IP-Adapter 高精度 |
| **指定发型（包月）** | **¥50/月** | 无限次指定发型 |

---

### 套餐整合

```
体验包（¥2）: 1 次标准发型
10 次卡（¥15）: 10 次标准发型
50 次卡（¥50）: 50 次标准发型 + 5 次指定发型（赠送）
月卡（¥99/200 次）: 200 次标准发型 + 20 次指定发型（赠送）
```

---

## 📋 实施清单

### 阶段 1：基础功能（本周） ⭐⭐⭐⭐⭐

- [ ] 创建 HairstyleAnalyzer 类
- [ ] 集成到 HairstyleGenerator
- [ ] 测试分析准确率
- [ ] 更新定价系统
- [ ] 更新 Telegram Bot

### 阶段 2：优化升级（下周） ⭐⭐⭐⭐

- [ ] 添加相似度评分
- [ ] 支持多图参考
- [ ] 优化提示词生成
- [ ] A/B 测试定价

### 阶段 3：高级功能（本月） ⭐⭐⭐

- [ ] IP-Adapter 部署
- [ ] 精确复制模式
- [ ] 批量对比功能
- [ ] 企业 API 开放

---

## 🎯 预期效果

| 指标 | 目标值 |
|------|--------|
| 分析准确率 | >85% |
| 用户满意度 | >90% |
| 使用率 | 30% 订单 |
| 额外收入 | +20% |

---

**状态**: 📋 需求确认完成，准备实施
