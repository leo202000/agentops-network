#!/usr/bin/env python3
"""
发型模板系统
预设发型配置 + 提示词模板
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class HairstyleCategory(Enum):
    """发型分类"""
    CURLY = "curly"      # 卷发
    STRAIGHT = "straight" # 直发
    SHORT = "short"      # 短发
    LONG = "long"        # 长发
    BRAID = "braid"      # 编发
    SPECIAL = "special"  # 特殊


@dataclass
class HairstyleTemplate:
    """发型模板"""
    id: str
    name: str
    name_en: str
    category: HairstyleCategory
    icon: str
    description: str
    prompt_template: str
    negative_prompt: str
    recommended_params: Dict[str, float]
    preview_image: Optional[str] = None


class HairstyleTemplateManager:
    """发型模板管理器"""
    
    def __init__(self):
        self.templates: Dict[str, HairstyleTemplate] = {}
        self._init_templates()
    
    def _init_templates(self):
        """初始化预设模板"""
        templates = [
            # 卷发类
            HairstyleTemplate(
                id="big_waves",
                name="大波浪",
                name_en="Big Waves",
                category=HairstyleCategory.CURLY,
                icon="🌊",
                description="自然蓬松的大波浪卷发，优雅浪漫",
                prompt_template="将图片中的发型修改为自然蓬松的大波浪卷发，波浪大而明显，从发根到发尾都有自然的卷曲，保持人物面部和服装不变，realistic photo, high quality, natural lighting",
                negative_prompt="short hair, bob cut, straight hair, 短发，直发, flat hair, messy hair",
                recommended_params={
                    "strength": 0.75,
                    "cfg_scale": 10.0,
                    "sample_steps": 40
                }
            ),
            HairstyleTemplate(
                id="wool_curls",
                name="羊毛卷",
                name_en="Wool Curls",
                category=HairstyleCategory.CURLY,
                icon="🐑",
                description="细密蓬松的羊毛卷，可爱俏皮",
                prompt_template="将图片中的发型修改为细密蓬松的羊毛卷，卷曲小而密集，整体蓬松饱满，保持人物面部和服装不变，realistic photo, high quality, natural lighting",
                negative_prompt="short hair, straight hair, 短发，直发, flat hair",
                recommended_params={
                    "strength": 0.80,
                    "cfg_scale": 10.0,
                    "sample_steps": 42
                }
            ),
            
            # 直发类
            HairstyleTemplate(
                id="long_straight",
                name="黑长直",
                name_en="Long Straight",
                category=HairstyleCategory.STRAIGHT,
                icon="✨",
                description="柔顺亮丽的长直发，清纯优雅",
                prompt_template="将图片中的发型修改为柔顺亮丽的长直发，发丝顺滑有光泽，长度及腰，保持人物面部和服装不变，realistic photo, high quality, natural lighting",
                negative_prompt="curly hair, wavy hair, short hair, 卷发，短发",
                recommended_params={
                    "strength": 0.70,
                    "cfg_scale": 9.0,
                    "sample_steps": 35
                }
            ),
            
            # 短发类
            HairstyleTemplate(
                id="bob_cut",
                name="波波头",
                name_en="Bob Cut",
                category=HairstyleCategory.SHORT,
                icon="💇",
                description="时尚干练的波波头短发",
                prompt_template="将图片中的发型修改为时尚干练的波波头短发，长度到下巴，发尾微卷内扣，保持人物面部和服装不变，realistic photo, high quality, natural lighting",
                negative_prompt="long hair, curly hair, 长发，卷发",
                recommended_params={
                    "strength": 0.85,
                    "cfg_scale": 11.0,
                    "sample_steps": 45
                }
            ),
            HairstyleTemplate(
                id="pixie_cut",
                name="精灵短发",
                name_en="Pixie Cut",
                category=HairstyleCategory.SHORT,
                icon="🧚",
                description="清爽个性的精灵短发",
                prompt_template="将图片中的发型修改为清爽个性的精灵短发，层次分明，露出耳朵和颈部线条，保持人物面部和服装不变，realistic photo, high quality, natural lighting",
                negative_prompt="long hair, medium hair, 长发，中长发",
                recommended_params={
                    "strength": 0.90,
                    "cfg_scale": 12.0,
                    "sample_steps": 50
                }
            ),
            
            # 长发类
            HairstyleTemplate(
                id="ponytail",
                name="高马尾",
                name_en="High Ponytail",
                category=HairstyleCategory.LONG,
                icon="🎀",
                description="活力青春的高马尾",
                prompt_template="将图片中的发型修改为活力青春的高马尾，头发梳得整齐光滑，马尾高高束起，保持人物面部和服装不变，realistic photo, high quality, natural lighting",
                negative_prompt="short hair, loose hair, 短发，散发",
                recommended_params={
                    "strength": 0.75,
                    "cfg_scale": 10.0,
                    "sample_steps": 40
                }
            ),
            
            # 编发类
            HairstyleTemplate(
                id="french_braid",
                name="法式编发",
                name_en="French Braid",
                category=HairstyleCategory.BRAID,
                icon="🌸",
                description="优雅精致的法式编发",
                prompt_template="将图片中的发型修改为优雅精致的法式编发，编发纹理清晰，整体整洁美观，保持人物面部和服装不变，realistic photo, high quality, natural lighting",
                negative_prompt="short hair, messy hair, 短发，乱发",
                recommended_params={
                    "strength": 0.80,
                    "cfg_scale": 10.0,
                    "sample_steps": 42
                }
            ),
            
            # 特殊类
            HairstyleTemplate(
                id="custom",
                name="自定义",
                name_en="Custom",
                category=HairstyleCategory.SPECIAL,
                icon="✏️",
                description="自定义发型描述",
                prompt_template="将图片中的发型修改为：{custom_description}，保持人物面部和服装不变，realistic photo, high quality, natural lighting",
                negative_prompt="",
                recommended_params={
                    "strength": 0.75,
                    "cfg_scale": 10.0,
                    "sample_steps": 40
                }
            )
        ]
        
        for template in templates:
            self.templates[template.id] = template
    
    def get_template(self, template_id: str) -> Optional[HairstyleTemplate]:
        """获取模板"""
        return self.templates.get(template_id)
    
    def get_all_templates(self) -> List[HairstyleTemplate]:
        """获取所有模板"""
        return list(self.templates.values())
    
    def get_templates_by_category(self, category: HairstyleCategory) -> List[HairstyleTemplate]:
        """按分类获取模板"""
        return [t for t in self.templates.values() if t.category == category]
    
    def generate_prompt(self, template_id: str, custom_description: str = "") -> Dict[str, str]:
        """
        生成提示词
        
        Args:
            template_id: 模板 ID
            custom_description: 自定义描述（用于自定义模板）
        
        Returns:
            包含正向提示词和负向提示词的字典
        """
        template = self.get_template(template_id)
        if not template:
            return {
                "prompt": "",
                "negative_prompt": "",
                "error": "模板不存在"
            }
        
        # 生成正向提示词
        prompt = template.prompt_template
        if template_id == "custom" and custom_description:
            prompt = prompt.replace("{custom_description}", custom_description)
        
        return {
            "prompt": prompt,
            "negative_prompt": template.negative_prompt,
            "recommended_params": template.recommended_params
        }
    
    def get_template_info(self, template_id: str) -> Optional[Dict]:
        """获取模板信息（用于前端展示）"""
        template = self.get_template(template_id)
        if not template:
            return None
        
        return {
            "id": template.id,
            "name": template.name,
            "name_en": template.name_en,
            "category": template.category.value,
            "icon": template.icon,
            "description": template.description,
            "recommended_params": template.recommended_params
        }
    
    def get_categories(self) -> List[Dict]:
        """获取所有分类"""
        categories = {}
        for template in self.templates.values():
            cat = template.category.value
            if cat not in categories:
                categories[cat] = {
                    "id": cat,
                    "name": self._get_category_name(cat),
                    "count": 0
                }
            categories[cat]["count"] += 1
        
        return list(categories.values())
    
    def _get_category_name(self, category: str) -> str:
        """获取分类名称"""
        names = {
            "curly": "卷发",
            "straight": "直发",
            "short": "短发",
            "long": "长发",
            "braid": "编发",
            "special": "特殊"
        }
        return names.get(category, category)


# 使用示例
if __name__ == "__main__":
    manager = HairstyleTemplateManager()
    
    print("📋 发型模板列表")
    print("=" * 50)
    
    for template in manager.get_all_templates():
        print(f"\n{template.icon} {template.name} ({template.name_en})")
        print(f"   分类：{template.category.value}")
        print(f"   描述：{template.description}")
        print(f"   推荐参数：{template.recommended_params}")
    
    print("\n" + "=" * 50)
    print("\n📝 生成提示词示例")
    
    # 生成大波浪提示词
    result = manager.generate_prompt("big_waves")
    print(f"\n大波浪：")
    print(f"  正向：{result['prompt'][:100]}...")
    print(f"  负向：{result['negative_prompt']}")
    
    # 生成自定义提示词
    result = manager.generate_prompt("custom", "粉色渐变长发，带有微卷")
    print(f"\n自定义：")
    print(f"  正向：{result['prompt']}")
