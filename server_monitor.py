#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentOps Network - 服务监控模块
监控服务器状态、资源使用、网络连通性
"""

import psutil
import json
import time
from datetime import datetime
from pathlib import Path

class ServiceMonitor:
    """服务监控器"""
    
    def __init__(self, config_path="monitor_config.json"):
        self.config = self.load_config(config_path)
        self.alerts = []
        self.metrics_history = []
    
    def load_config(self, path):
        """加载监控配置"""
        default_config = {
            "thresholds": {
                "cpu_warning": 80,
                "cpu_critical": 95,
                "memory_warning": 80,
                "memory_critical": 95,
                "disk_warning": 80,
                "disk_critical": 95
            },
            "check_interval": 60,  # 秒
            "alert_endpoints": [],
            "monitored_services": [
                "agentcoin_mining",
                "botcoin_hunting",
                "moltbook_api"
            ]
        }
        
        if Path(path).exists():
            with open(path, 'r') as f:
                return json.load(f)
        return default_config
    
    def get_cpu_metrics(self):
        """获取 CPU 指标"""
        return {
            "usage_percent": psutil.cpu_percent(interval=1),
            "cores": psutil.cpu_count(),
            "freq": psutil.cpu_freq().current if psutil.cpu_freq() else 0
        }
    
    def get_memory_metrics(self):
        """获取内存指标"""
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent,
            "swap_total": psutil.swap_memory().total,
            "swap_used": psutil.swap_memory().used
        }
    
    def get_disk_metrics(self):
        """获取磁盘指标"""
        disk = psutil.disk_usage('/')
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }
    
    def get_network_metrics(self):
        """获取网络指标"""
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "errin": net_io.errin,
            "errout": net_io.errout
        }
    
    def check_service_health(self, service_name):
        """检查服务健康状态"""
        health_checks = {
            "agentcoin_mining": self.check_agentcoin,
            "botcoin_hunting": self.check_botcoin,
            "moltbook_api": self.check_moltbook
        }
        
        if service_name in health_checks:
            return health_checks[service_name]()
        return {"status": "unknown", "message": f"Unknown service: {service_name}"}
    
    def check_agentcoin(self):
        """检查 AgentCoin 服务"""
        try:
            import urllib.request
            req = urllib.request.Request(
                "https://api.agentcoin.site/api/v1/agent/34506",
                method='GET'
            )
            response = urllib.request.urlopen(req, timeout=10)
            return {
                "status": "healthy" if response.status == 200 else "degraded",
                "response_time": 1000,  # ms
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    def check_botcoin(self):
        """检查 Botcoin 服务"""
        try:
            import urllib.request
            req = urllib.request.Request(
                "https://botcoin.farm/api/leaderboard",
                method='GET'
            )
            response = urllib.request.urlopen(req, timeout=10)
            return {
                "status": "healthy" if response.status == 200 else "degraded",
                "response_time": 1000,
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    def check_moltbook(self):
        """检查 Moltbook API"""
        try:
            import urllib.request
            req = urllib.request.Request(
                "https://www.moltbook.com/api/v1/agents/me",
                method='GET',
                headers={
                    "Authorization": "Bearer moltbook_sk_3Y-R3S8dP291uZ_CuX_R0RVTCbHdNpgN"
                }
            )
            response = urllib.request.urlopen(req, timeout=10)
            return {
                "status": "healthy" if response.status == 200 else "degraded",
                "response_time": 1000,
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    def generate_alert(self, severity, metric, value, threshold):
        """生成告警"""
        alert = {
            "timestamp": datetime.utcnow().isoformat(),
            "severity": severity,  # warning, critical
            "metric": metric,
            "value": value,
            "threshold": threshold,
            "message": f"{metric} is {value}% (threshold: {threshold}%)"
        }
        self.alerts.append(alert)
        return alert
    
    def check_thresholds(self, metrics):
        """检查阈值"""
        thresholds = self.config["thresholds"]
        
        # CPU 检查
        cpu_usage = metrics["cpu"]["usage_percent"]
        if cpu_usage >= thresholds["cpu_critical"]:
            self.generate_alert("critical", "cpu", cpu_usage, thresholds["cpu_critical"])
        elif cpu_usage >= thresholds["cpu_warning"]:
            self.generate_alert("warning", "cpu", cpu_usage, thresholds["cpu_warning"])
        
        # 内存检查
        mem_usage = metrics["memory"]["percent"]
        if mem_usage >= thresholds["memory_critical"]:
            self.generate_alert("critical", "memory", mem_usage, thresholds["memory_critical"])
        elif mem_usage >= thresholds["memory_warning"]:
            self.generate_alert("warning", "memory", mem_usage, thresholds["memory_warning"])
        
        # 磁盘检查
        disk_usage = metrics["disk"]["percent"]
        if disk_usage >= thresholds["disk_critical"]:
            self.generate_alert("critical", "disk", disk_usage, thresholds["disk_critical"])
        elif disk_usage >= thresholds["disk_warning"]:
            self.generate_alert("warning", "disk", disk_usage, thresholds["disk_warning"])
    
    def collect_all_metrics(self):
        """收集所有指标"""
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": self.get_cpu_metrics(),
            "memory": self.get_memory_metrics(),
            "disk": self.get_disk_metrics(),
            "network": self.get_network_metrics(),
            "services": {}
        }
        
        # 检查所有服务
        for service in self.config["monitored_services"]:
            metrics["services"][service] = self.check_service_health(service)
        
        # 检查阈值
        self.check_thresholds(metrics)
        
        # 保存历史
        self.metrics_history.append(metrics)
        
        return metrics
    
    def save_metrics(self, output_path="metrics_history.jsonl"):
        """保存指标到文件"""
        with open(output_path, 'a') as f:
            for metric in self.metrics_history:
                f.write(json.dumps(metric) + '\n')
        self.metrics_history = []
    
    def get_status_summary(self):
        """获取状态摘要"""
        if not self.metrics_history:
            return {"status": "no_data"}
        
        latest = self.metrics_history[-1]
        alerts_count = len(self.alerts)
        
        # 计算整体健康度
        health_score = 100
        
        # CPU 影响
        if latest["cpu"]["usage_percent"] > 90:
            health_score -= 30
        elif latest["cpu"]["usage_percent"] > 70:
            health_score -= 10
        
        # 内存影响
        if latest["memory"]["percent"] > 90:
            health_score -= 30
        elif latest["memory"]["percent"] > 70:
            health_score -= 10
        
        # 服务健康影响
        for service, health in latest["services"].items():
            if health["status"] == "unhealthy":
                health_score -= 20
            elif health["status"] == "degraded":
                health_score -= 10
        
        health_score = max(0, health_score)
        
        return {
            "health_score": health_score,
            "status": "healthy" if health_score >= 80 else "degraded" if health_score >= 50 else "critical",
            "alerts_count": alerts_count,
            "services_status": {
                name: data["status"] 
                for name, data in latest["services"].items()
            },
            "timestamp": latest["timestamp"]
        }
    
    def run_continuous(self, interval=None):
        """持续监控"""
        if interval is None:
            interval = self.config["check_interval"]
        
        print(f"🔍 开始监控 (间隔：{interval}秒)")
        print(f"监控服务：{', '.join(self.config['monitored_services'])}")
        print("-" * 70)
        
        try:
            while True:
                metrics = self.collect_all_metrics()
                summary = self.get_status_summary()
                
                # 打印状态
                print(f"\n[{metrics['timestamp']}]")
                print(f"健康度：{summary['health_score']}/100 ({summary['status']})")
                print(f"CPU: {metrics['cpu']['usage_percent']:.1f}% | "
                      f"内存：{metrics['memory']['percent']:.1f}% | "
                      f"磁盘：{metrics['disk']['percent']:.1f}%")
                
                # 服务状态
                print("服务状态:")
                for service, health in metrics["services"].items():
                    status_icon = "✅" if health["status"] == "healthy" else "⚠️" if health["status"] == "degraded" else "❌"
                    print(f"  {status_icon} {service}: {health['status']}")
                
                # 告警
                if self.alerts:
                    print(f"\n⚠️  新增告警：{len(self.alerts)} 条")
                    for alert in self.alerts[-3:]:  # 显示最近 3 条
                        print(f"  [{alert['severity'].upper()}] {alert['message']}")
                    self.alerts = []
                
                # 定期保存
                if len(self.metrics_history) >= 60:  # 每 60 次保存
                    self.save_metrics()
                    print(f"\n💾 已保存指标历史")
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\n⏹️  监控停止")
            self.save_metrics()
            print(f"📊 共收集 {len(self.metrics_history)} 条指标")


def main():
    """主函数"""
    monitor = ServiceMonitor()
    
    # 单次检查
    print("🔍 执行单次系统检查...\n")
    metrics = monitor.collect_all_metrics()
    summary = monitor.get_status_summary()
    
    print(f"系统健康度：{summary['health_score']}/100 ({summary['status']})")
    print(f"\n资源使用:")
    print(f"  CPU: {metrics['cpu']['usage_percent']:.1f}%")
    print(f"  内存：{metrics['memory']['percent']:.1f}% ({metrics['memory']['used']/1024/1024/1024:.2f}GB / {metrics['memory']['total']/1024/1024/1024:.2f}GB)")
    print(f"  磁盘：{metrics['disk']['percent']:.1f}% ({metrics['disk']['used']/1024/1024/1024:.2f}GB / {metrics['disk']['total']/1024/1024/1024:.2f}GB)")
    
    print(f"\n服务状态:")
    for service, health in metrics["services"].items():
        status_icon = "✅" if health["status"] == "healthy" else "⚠️" if health["status"] == "degraded" else "❌"
        print(f"  {status_icon} {service}: {health['status']}")
    
    if summary['alerts_count'] > 0:
        print(f"\n⚠️  告警：{summary['alerts_count']} 条")
    
    print(f"\n💡 提示:")
    print(f"  - 运行 'python3 server_monitor.py --continuous' 启动持续监控")
    print(f"  - 指标历史保存在 metrics_history.jsonl")


if __name__ == "__main__":
    main()
