#!/usr/bin/env python3
"""
Botcoin 技能配置验证器
验证所有配置是否正确设置
"""

import os
import sys
import json
from datetime import datetime

class BotcoinSetupValidator:
    def __init__(self):
        self.public_key = "/mWVXodQHoPpXX0RT3kTxzV5wCQPjLWDeV2Ze7LvoDs="
        self.config_dir = os.path.expanduser("~/.zeroclaw")
        self.config_file = os.path.join(self.config_dir, "config.toml")
        self.secrets_dir = os.path.join(self.config_dir, "secrets")
        self.logs_dir = os.path.join(self.config_dir, "logs")
        
    def check_directory_structure(self):
        """检查目录结构"""
        print("📁 检查目录结构...")
        
        dirs_to_check = [
            self.config_dir,
            self.secrets_dir,
            self.logs_dir,
            os.path.join(self.config_dir, "workspace"),
            os.path.join(self.config_dir, "workspace", "skills")
        ]
        
        all_exist = True
        for dir_path in dirs_to_check:
            if os.path.exists(dir_path):
                print(f"  ✅ {dir_path}")
            else:
                print(f"  ❌ {dir_path} - 不存在")
                all_exist = False
                
        return all_exist
        
    def check_config_file(self):
        """检查配置文件"""
        print("\n📄 检查配置文件...")
        
        if not os.path.exists(self.config_file):
            print(f"  ❌ 配置文件不存在：{self.config_file}")
            return False
            
        print(f"  ✅ 配置文件存在")
        
        # 读取并验证关键配置
        with open(self.config_file, 'r') as f:
            content = f.read()
            
        checks = [
            ("[skills.botcoin]", "Botcoin 技能配置"),
            ("public_key", "公钥配置"),
            ("gas_management", "Gas 管理配置"),
            ("strategy", "策略配置"),
            ("monitoring", "监控配置")
        ]
        
        all_ok = True
        for check_str, description in checks:
            if check_str in content:
                print(f"  ✅ {description} 已配置")
            else:
                print(f"  ⚠️ {description} 缺失")
                all_ok = False
                
        return all_ok
        
    def check_secrets_file(self):
        """检查密钥文件"""
        print("\n🔐 检查密钥文件...")
        
        secrets_file = os.path.join(self.secrets_dir, "botcoin.key")
        
        if not os.path.exists(secrets_file):
            print(f"  ❌ 密钥文件不存在")
            return False
            
        # 检查文件权限
        file_stat = os.stat(secrets_file)
        perms = oct(file_stat.st_mode)[-3:]
        
        if perms == "600":
            print(f"  ✅ 密钥文件权限正确 (600)")
        else:
            print(f"  ⚠️ 密钥文件权限不安全 ({perms})，建议设置为 600")
            
        # 检查密钥内容
        with open(secrets_file, 'r') as f:
            content = f.read()
            
        if "BOTCOIN_PRIVATE_KEY=" in content:
            print(f"  ✅ 私钥已配置")
        else:
            print(f"  ❌ 私钥未配置")
            return False
            
        if self.public_key.replace("/", "\\/") in content or self.public_key in content:
            print(f"  ✅ 公钥元数据已记录")
        else:
            print(f"  ⚠️ 公钥元数据缺失")
            
        return True
        
    def check_leaderboard_status(self):
        """检查排行榜状态"""
        print("\n🏆 检查排行榜状态...")
        
        try:
            import requests
            response = requests.get("https://botcoin.farm/api/leaderboard", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                leaderboard = data.get('leaderboard', [])
                
                # 搜索您的账户
                found = False
                for i, entry in enumerate(leaderboard):
                    if entry.get('public_key') == self.public_key:
                        print(f"  ✅ 已上榜！排名：#{i+1}")
                        print(f"     硬币数：{entry.get('coins', 0)}")
                        found = True
                        break
                
                if not found:
                    print(f"  🔍 尚未上榜（正常，继续寻宝）")
                    print(f"     总参与人数：{len(leaderboard)}")
                    if leaderboard:
                        print(f"     榜首：{leaderboard[0]['display_name']} - {leaderboard[0]['coins']} 硬币")
                        
                return True
            else:
                print(f"  ⚠️ API 响应异常：{response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ 检查失败：{e}")
            return False
            
    def generate_summary(self, results):
        """生成配置摘要"""
        print("\n" + "="*60)
        print("📊 Botcoin 技能配置验证报告")
        print("="*60)
        print(f"验证时间：{datetime.now()}")
        print(f"配置目录：{self.config_dir}")
        print(f"公钥：{self.public_key[:20]}...{self.public_key[-10:]}")
        print("="*60)
        
        total = len(results)
        passed = sum(1 for r in results.values() if r)
        
        for check_name, passed_check in results.items():
            status = "✅ 通过" if passed_check else "❌ 未通过"
            print(f"{status} - {check_name}")
            
        print("="*60)
        print(f"总计：{passed}/{total} 检查项通过")
        
        if passed == total:
            print("\n🎉 所有配置检查通过！可以开始寻宝了！")
            print("\n下一步:")
            print("1. 确保 ClawHub Botcoin 技能已安装")
            print("2. 运行：zeroclaw botcoin list-hunts")
            print("3. 开始解谜寻宝！")
        else:
            print("\n⚠️ 部分检查未通过，请根据上述提示修复配置")
            
        print("="*60)
        
    def run_validation(self):
        """运行完整验证"""
        results = {
            "目录结构": self.check_directory_structure(),
            "配置文件": self.check_config_file(),
            "密钥文件": self.check_secrets_file(),
            "排行榜连接": self.check_leaderboard_status()
        }
        
        self.generate_summary(results)
        return all(results.values())

def main():
    print("🔧 Botcoin 技能配置验证器")
    print("开始验证配置...\n")
    
    validator = BotcoinSetupValidator()
    success = validator.run_validation()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
