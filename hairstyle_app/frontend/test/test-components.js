/**
 * 组件测试脚本
 * 测试 UI 组件功能
 */

class ComponentTester {
    constructor() {
        this.results = [];
    }

    /**
     * 运行所有组件测试
     */
    async runAllTests() {
        console.log('🧪 开始组件测试...\n');

        await this.testToast();
        await this.testModal();
        await this.testLoading();
        await this.testProgress();

        this.printSummary();
        return this.results;
    }

    /**
     * 测试 Toast 组件
     */
    async testToast() {
        console.log('📋 测试 Toast 组件...');
        
        try {
            const ui = new UIComponents();
            
            // 测试不同类型的 Toast
            const types = ['info', 'success', 'warning', 'error'];
            
            for (const type of types) {
                const toast = ui.showToast(`测试 ${type} 消息`, type, 100);
                
                if (toast && toast.classList.contains(`toast-${type}`)) {
                    this.addResult('Toast', `类型 ${type}`, true);
                } else {
                    this.addResult('Toast', `类型 ${type}`, false, '样式类未正确添加');
                }
                
                // 自动清理
                setTimeout(() => ui.hideToast(toast), 200);
            }

            // 测试 Toast 关闭
            const toast = ui.showToast('测试关闭', 'info', 0);
            ui.hideToast(toast);
            
            setTimeout(() => {
                if (!document.body.contains(toast)) {
                    this.addResult('Toast', '关闭功能', true);
                } else {
                    this.addResult('Toast', '关闭功能', false, 'Toast 未正确移除');
                }
            }, 500);

        } catch (error) {
            this.addResult('Toast', '整体测试', false, error.message);
        }
    }

    /**
     * 测试 Modal 组件
     */
    async testModal() {
        console.log('📋 测试 Modal 组件...');
        
        try {
            const ui = new UIComponents();
            
            // 测试基本 Modal
            const modal = ui.showModal({
                title: '测试标题',
                content: '<p>测试内容</p>',
                buttons: [
                    { text: '按钮1', action: 'btn1' },
                    { text: '按钮2', action: 'btn2', class: 'btn-primary' }
                ]
            });

            if (modal && modal.querySelector('.modal-title')) {
                this.addResult('Modal', '基本显示', true);
            } else {
                this.addResult('Modal', '基本显示', false, 'Modal 结构不正确');
            }

            // 测试关闭
            ui.hideModal(modal);
            
            setTimeout(() => {
                if (!document.body.contains(modal)) {
                    this.addResult('Modal', '关闭功能', true);
                } else {
                    this.addResult('Modal', '关闭功能', false, 'Modal 未正确移除');
                }
            }, 500);

            // 测试确认对话框
            const confirmModal = ui.confirm('确认测试？', 
                () => console.log('确认'),
                () => console.log('取消')
            );
            
            if (confirmModal) {
                this.addResult('Modal', '确认对话框', true);
                ui.hideModal(confirmModal);
            } else {
                this.addResult('Modal', '确认对话框', false);
            }

        } catch (error) {
            this.addResult('Modal', '整体测试', false, error.message);
        }
    }

    /**
     * 测试 Loading 组件
     */
    async testLoading() {
        console.log('📋 测试 Loading 组件...');
        
        try {
            const ui = new UIComponents();
            
            // 测试显示
            const loading = ui.showLoading('加载中...');
            
            if (loading && loading.querySelector('.loading-spinner')) {
                this.addResult('Loading', '显示功能', true);
            } else {
                this.addResult('Loading', '显示功能', false, 'Loading 结构不正确');
            }

            // 测试隐藏
            ui.hideLoading(loading);
            
            setTimeout(() => {
                if (!document.body.contains(loading)) {
                    this.addResult('Loading', '隐藏功能', true);
                } else {
                    this.addResult('Loading', '隐藏功能', false, 'Loading 未正确移除');
                }
            }, 500);

            // 测试自定义消息
            const customLoading = ui.showLoading('自定义消息');
            const messageEl = customLoading.querySelector('.loading-message');
            
            if (messageEl && messageEl.textContent === '自定义消息') {
                this.addResult('Loading', '自定义消息', true);
            } else {
                this.addResult('Loading', '自定义消息', false, '消息未正确显示');
            }
            
            ui.hideLoading(customLoading);

        } catch (error) {
            this.addResult('Loading', '整体测试', false, error.message);
        }
    }

    /**
     * 测试进度条组件
     */
    async testProgress() {
        console.log('📋 测试进度条组件...');
        
        try {
            const ui = new UIComponents();
            
            // 创建测试 DOM 结构
            const testContainer = document.createElement('div');
            testContainer.innerHTML = `
                <div id="progress-fill"></div>
                <div id="progress-text"></div>
                <div id="progress-status"></div>
                <div id="queue-info"></div>
            `;
            document.body.appendChild(testContainer);

            // 测试进度更新
            ui.updateProgress(50, '处理中', { position: 3, total: 10, estimatedWait: 30 });
            
            const progressFill = document.getElementById('progress-fill');
            const progressText = document.getElementById('progress-text');
            
            if (progressFill && progressFill.style.width === '50%') {
                this.addResult('Progress', '进度更新', true);
            } else {
                this.addResult('Progress', '进度更新', false, '进度条未正确更新');
            }

            if (progressText && progressText.textContent === '50%') {
                this.addResult('Progress', '百分比显示', true);
            } else {
                this.addResult('Progress', '百分比显示', false, '百分比未正确显示');
            }

            // 清理
            testContainer.remove();

        } catch (error) {
            this.addResult('Progress', '整体测试', false, error.message);
        }
    }

    /**
     * 添加测试结果
     */
    addResult(component, test, passed, message = '') {
        const result = {
            component,
            test,
            passed,
            message,
            timestamp: new Date().toISOString()
        };
        
        this.results.push(result);
        
        const icon = passed ? '✅' : '❌';
        const status = passed ? '通过' : '失败';
        console.log(`  ${icon} ${component} - ${test}: ${status}${message ? ` (${message})` : ''}`);
    }

    /**
     * 打印汇总
     */
    printSummary() {
        console.log('\n📊 测试结果汇总');
        console.log('================');
        
        const total = this.results.length;
        const passed = this.results.filter(r => r.passed).length;
        const failed = total - passed;
        const passRate = total > 0 ? Math.round((passed / total) * 100) : 0;

        console.log(`总测试数：${total}`);
        console.log(`通过：${passed} ✅`);
        console.log(`失败：${failed} ❌`);
        console.log(`通过率：${passRate}%`);
        
        if (passRate >= 80) {
            console.log('\n🎉 组件测试通过！');
        } else if (passRate >= 60) {
            console.log('\n⚠️ 部分测试失败，需要检查');
        } else {
            console.log('\n❌ 测试未通过，需要修复');
        }
    }
}

// 导出
window.ComponentTester = ComponentTester;

// 自动运行测试（如果在测试页面）
if (document.readyState === 'complete') {
    // 页面已加载，可以运行测试
    console.log('组件测试脚本已加载');
}
