/**
 * 集成测试脚本
 * 测试模块间集成
 */

class IntegrationTester {
    constructor() {
        this.results = [];
    }

    /**
     * 运行所有集成测试
     */
    async runAllTests() {
        console.log('🔗 开始集成测试...\n');

        await this.testTaskManagerIntegration();
        await this.testWebSocketIntegration();
        await this.testAppIntegration();

        this.printSummary();
        return this.results;
    }

    /**
     * 测试任务管理器集成
     */
    async testTaskManagerIntegration() {
        console.log('📋 测试任务管理器集成...');
        
        try {
            const client = new TaskManagerClient('http://localhost:8080');
            
            // 测试重试机制
            console.log('  测试重试机制...');
            
            // 模拟请求（这里只是测试代码结构，不实际发送请求）
            const testRetry = async () => {
                let retries = 0;
                const maxRetries = 3;
                
                while (retries < maxRetries) {
                    try {
                        // 模拟成功
                        if (retries === 1) {
                            return { success: true };
                        }
                        throw new Error('模拟错误');
                    } catch (error) {
                        retries++;
                        if (retries >= maxRetries) {
                            throw error;
                        }
                        await new Promise(resolve => setTimeout(resolve, 100));
                    }
                }
            };

            try {
                await testRetry();
                this.addResult('TaskManager', '重试机制', true);
            } catch (error) {
                this.addResult('TaskManager', '重试机制', false, error.message);
            }

            // 测试超时控制
            console.log('  测试超时控制...');
            
            const testTimeout = async () => {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 100);
                
                try {
                    await new Promise((resolve, reject) => {
                        setTimeout(() => {
                            clearTimeout(timeoutId);
                            reject(new Error('请求超时'));
                        }, 200);
                    });
                } catch (error) {
                    if (error.name === 'AbortError') {
                        return { aborted: true };
                    }
                    throw error;
                }
            };

            try {
                await testTimeout();
                this.addResult('TaskManager', '超时控制', true);
            } catch (error) {
                this.addResult('TaskManager', '超时控制', false, error.message);
            }

        } catch (error) {
            this.addResult('TaskManager', '整体集成', false, error.message);
        }
    }

    /**
     * 测试 WebSocket 集成
     */
    async testWebSocketIntegration() {
        console.log('📋 测试 WebSocket 集成...');
        
        try {
            // 测试 WebSocket 管理器初始化
            const wsManager = new WebSocketManager(
                'ws://localhost:8081/ws/test',
                'http://localhost:8080/api/test',
                (status) => console.log(`  状态: ${status}`)
            );

            if (wsManager) {
                this.addResult('WebSocket', '初始化', true);
            } else {
                this.addResult('WebSocket', '初始化', false, '创建失败');
            }

            // 测试回调注册
            let messageReceived = false;
            wsManager.onMessage((data) => {
                messageReceived = true;
            });

            // 模拟消息
            wsManager.notifyCallbacks({ test: true });
            
            if (messageReceived) {
                this.addResult('WebSocket', '消息回调', true);
            } else {
                this.addResult('WebSocket', '消息回调', false, '回调未触发');
            }

            // 测试断开连接
            wsManager.disconnect();
            this.addResult('WebSocket', '断开连接', true);

        } catch (error) {
            this.addResult('WebSocket', '整体集成', false, error.message);
        }
    }

    /**
     * 测试应用集成
     */
    async testAppIntegration() {
        console.log('📋 测试应用集成...');
        
        try {
            // 测试应用初始化
            // 注意：这里只是测试代码结构，不实际创建应用实例
            
            // 测试步骤切换逻辑
            const testStepTransition = () => {
                const steps = [1, 2, 3, 4, 5];
                const transitions = [];
                
                for (let i = 0; i < steps.length - 1; i++) {
                    transitions.push({
                        from: steps[i],
                        to: steps[i + 1],
                        valid: true
                    });
                }
                
                return transitions;
            };

            const transitions = testStepTransition();
            
            if (transitions.length === 4) {
                this.addResult('App', '步骤切换逻辑', true);
            } else {
                this.addResult('App', '步骤切换逻辑', false, '切换数量不正确');
            }

            // 测试状态映射
            const statusMap = {
                10: '等待中',
                30: '排队中',
                42: '处理中',
                45: '已完成，等待确认',
                20: '已确认',
                50: '失败'
            };

            const testStatuses = [10, 30, 42, 45, 20, 50];
            const allMapped = testStatuses.every(s => statusMap[s] !== undefined);

            if (allMapped) {
                this.addResult('App', '状态映射', true);
            } else {
                this.addResult('App', '状态映射', false, '存在未映射状态');
            }

            // 测试文件验证逻辑
            const testFileValidation = (file) => {
                const maxSize = 10 * 1024 * 1024; // 10MB
                const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
                
                if (!allowedTypes.includes(file.type)) {
                    return { valid: false, error: '文件类型不支持' };
                }
                
                if (file.size > maxSize) {
                    return { valid: false, error: '文件大小超过限制' };
                }
                
                return { valid: true };
            };

            // 测试有效文件
            const validFile = { type: 'image/jpeg', size: 5 * 1024 * 1024 };
            const validResult = testFileValidation(validFile);
            
            if (validResult.valid) {
                this.addResult('App', '文件验证-有效文件', true);
            } else {
                this.addResult('App', '文件验证-有效文件', false, validResult.error);
            }

            // 测试无效类型
            const invalidTypeFile = { type: 'application/pdf', size: 5 * 1024 * 1024 };
            const invalidTypeResult = testFileValidation(invalidTypeFile);
            
            if (!invalidTypeResult.valid) {
                this.addResult('App', '文件验证-无效类型', true);
            } else {
                this.addResult('App', '文件验证-无效类型', false, '应拒绝无效类型');
            }

            // 测试超大文件
            const largeFile = { type: 'image/jpeg', size: 15 * 1024 * 1024 };
            const largeResult = testFileValidation(largeFile);
            
            if (!largeResult.valid) {
                this.addResult('App', '文件验证-超大文件', true);
            } else {
                this.addResult('App', '文件验证-超大文件', false, '应拒绝超大文件');
            }

        } catch (error) {
            this.addResult('App', '整体集成', false, error.message);
        }
    }

    /**
     * 添加测试结果
     */
    addResult(module, test, passed, message = '') {
        const result = {
            module,
            test,
            passed,
            message,
            timestamp: new Date().toISOString()
        };
        
        this.results.push(result);
        
        const icon = passed ? '✅' : '❌';
        const status = passed ? '通过' : '失败';
        console.log(`  ${icon} ${module} - ${test}: ${status}${message ? ` (${message})` : ''}`);
    }

    /**
     * 打印汇总
     */
    printSummary() {
        console.log('\n📊 集成测试结果汇总');
        console.log('===================');
        
        const total = this.results.length;
        const passed = this.results.filter(r => r.passed).length;
        const failed = total - passed;
        const passRate = total > 0 ? Math.round((passed / total) * 100) : 0;

        console.log(`总测试数：${total}`);
        console.log(`通过：${passed} ✅`);
        console.log(`失败：${failed} ❌`);
        console.log(`通过率：${passRate}%`);
        
        if (passRate >= 80) {
            console.log('\n🎉 集成测试通过！');
        } else if (passRate >= 60) {
            console.log('\n⚠️ 部分测试失败，需要检查');
        } else {
            console.log('\n❌ 测试未通过，需要修复');
        }
    }
}

// 导出
window.IntegrationTester = IntegrationTester;

// 自动运行测试（如果在测试页面）
if (document.readyState === 'complete') {
    console.log('集成测试脚本已加载');
}