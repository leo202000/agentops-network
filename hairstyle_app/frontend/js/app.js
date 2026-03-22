/**
 * 主应用模块
 * 整合所有功能模块
 */

class HairstyleApp {
    constructor() {
        this.currentStep = 1;
        this.uploadedPhotos = [];
        this.selectedHairstyle = null;
        this.customDescription = '';
        this.currentTask = null;
        
        this.taskManager = new TaskManagerClient();
        this.wsManager = null;
        this.ui = new UIComponents();
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.showStep(1);
        console.log('✅ 发型生成应用已初始化');
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 步骤 1: 上传照片
        this.bindUploadEvents();
        
        // 步骤 2: 选择发型
        this.bindHairstyleEvents();
        
        // 步骤 3: 进度（自动）
        
        // 步骤 4: 预览（自动）
        
        // 步骤 5: 完成（自动）
    }

    /**
     * 绑定上传事件
     */
    bindUploadEvents() {
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('file-input');
        const nextBtn = document.getElementById('step-1-next');

        // 点击上传
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        // 文件选择
        fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });

        // 拖拽上传
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            this.handleFiles(e.dataTransfer.files);
        });

        // 下一步按钮
        nextBtn.addEventListener('click', () => {
            if (this.uploadedPhotos.length === 0) {
                this.ui.showToast('请先上传照片', 'warning');
                return;
            }
            this.showStep(2);
        });
    }

    /**
     * 处理文件
     */
    handleFiles(files) {
        const maxFiles = 5;
        const maxSize = 10 * 1024 * 1024; // 10MB

        if (this.uploadedPhotos.length + files.length > maxFiles) {
            this.ui.showToast(`最多上传 ${maxFiles} 张照片`, 'warning');
            return;
        }

        Array.from(files).forEach(file => {
            if (!file.type.startsWith('image/')) {
                this.ui.showToast(`${file.name} 不是图片文件`, 'warning');
                return;
            }

            if (file.size > maxSize) {
                this.ui.showToast(`${file.name} 超过 10MB 限制`, 'warning');
                return;
            }

            // 读取并预览
            const reader = new FileReader();
            reader.onload = (e) => {
                this.uploadedPhotos.push({
                    file: file,
                    dataUrl: e.target.result
                });
                this.updatePhotoPreview();
            };
            reader.readAsDataURL(file);
        });
    }

    /**
     * 更新照片预览
     */
    updatePhotoPreview() {
        const previewContainer = document.getElementById('photo-preview');
        const uploadArea = document.getElementById('upload-area');

        // 清空预览
        previewContainer.innerHTML = '';

        // 添加预览项
        this.uploadedPhotos.forEach((photo, index) => {
            const item = document.createElement('div');
            item.className = 'preview-item';
            item.innerHTML = `
                <img src="${photo.dataUrl}" alt="预览 ${index + 1}">
                <button class="remove-btn" data-index="${index}">&times;</button>
            `;

            // 删除按钮
            item.querySelector('.remove-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                this.removePhoto(index);
            });

            previewContainer.appendChild(item);
        });

        // 更新上传区域状态
        if (this.uploadedPhotos.length > 0) {
            uploadArea.classList.add('has-files');
        } else {
            uploadArea.classList.remove('has-files');
        }
    }

    /**
     * 删除照片
     */
    removePhoto(index) {
        this.uploadedPhotos.splice(index, 1);
        this.updatePhotoPreview();
    }

    /**
     * 绑定发型选择事件
     */
    bindHairstyleEvents() {
        const cards = document.querySelectorAll('.hairstyle-card');
        const customDesc = document.getElementById('custom-desc');
        const prevBtn = document.getElementById('step-2-prev');
        const nextBtn = document.getElementById('step-2-next');

        // 发型卡片点击
        cards.forEach(card => {
            card.addEventListener('click', () => {
                cards.forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                this.selectedHairstyle = card.dataset.style;
            });
        });

        // 自定义描述
        customDesc.addEventListener('input', (e) => {
            this.customDescription = e.target.value;
        });

        // 上一步
        prevBtn.addEventListener('click', () => {
            this.showStep(1);
        });

        // 下一步（提交任务）
        nextBtn.addEventListener('click', async () => {
            if (!this.selectedHairstyle) {
                this.ui.showToast('请选择一种发型', 'warning');
                return;
            }
            await this.submitTask();
        });
    }

    /**
     * 提交任务
     */
    async submitTask() {
        const loading = this.ui.showLoading('正在提交任务...');

        try {
            // 生成用户 ID
            const userId = 'user_' + Date.now();

            // 提取照片 URL（这里应该是上传后的 URL）
            const photoUrls = this.uploadedPhotos.map(p => p.dataUrl);

            // 创建任务
            const result = await this.taskManager.createTask(
                userId,
                photoUrls,
                this.selectedHairstyle,
                this.customDescription
            );

            this.currentTask = result.task;
            
            this.ui.hideLoading(loading);
            this.ui.showToast('任务提交成功', 'success');
            
            // 进入进度步骤
            this.showStep(3);
            this.startProgressTracking();

        } catch (error) {
            this.ui.hideLoading(loading);
            this.ui.showToast('提交失败：' + error.message, 'error');
            console.error('提交任务失败:', error);
        }
    }

    /**
     * 开始进度跟踪
     */
    startProgressTracking() {
        if (!this.currentTask) return;

        // 创建 WebSocket 连接
        this.wsManager = new WebSocketManager(
            `ws://localhost:8081/ws/task/${this.currentTask.id}`,
            `http://localhost:8080/api/task/${this.currentTask.id}`,
            (status) => {
                this.updateConnectionStatus(status);
            }
        );

        // 监听消息
        this.wsManager.onMessage((data) => {
            this.handleTaskUpdate(data);
        });

        // 连接
        this.wsManager.connect(this.currentTask.id);
    }

    /**
     * 处理任务更新
     */
    handleTaskUpdate(data) {
        const { status, progress, queue_info, result_url, error } = data;

        // 更新进度
        this.ui.updateProgress(progress, this.getStatusText(status), queue_info);

        // 状态处理
        switch (status) {
            case 20: // CONFIRMED
                this.showStep(5);
                this.showFinalResult(result_url);
                break;

            case 45: // COMPLETED
                this.showStep(4);
                this.showPreview(result_url);
                break;

            case 50: // FAILED
                this.ui.showToast('生成失败：' + (error || '未知错误'), 'error');
                this.showStep(2);
                break;
        }
    }

    /**
     * 获取状态文本
     */
    getStatusText(status) {
        const statusMap = {
            10: '等待中',
            30: '排队中',
            42: '处理中',
            45: '已完成，等待确认',
            20: '已确认',
            50: '失败'
        };
        return statusMap[status] || '未知状态';
    }

    /**
     * 更新连接状态
     */
    updateConnectionStatus(status) {
        const statusEl = document.getElementById('connection-status');
        const dotEl = statusEl?.querySelector('.status-dot');
        const textEl = statusEl?.querySelector('.status-text');

        if (!statusEl) return;

        const statusConfig = {
            'connected': { class: 'connected', text: '已连接' },
            'disconnected': { class: 'disconnected', text: '已断开' },
            'polling': { class: 'polling', text: '轮询中' },
            'error': { class: 'error', text: '连接错误' }
        };

        const config = statusConfig[status] || statusConfig['disconnected'];

        if (dotEl) {
            dotEl.className = `status-dot ${config.class}`;
        }
        if (textEl) {
            textEl.textContent = config.text;
        }
    }

    /**
     * 显示预览
     */
    showPreview(imageUrl) {
        this.ui.showResult(imageUrl, 
            // 确认
            async () => {
                try {
                    await this.taskManager.confirmTask(this.currentTask.id);
                    this.ui.showToast('已确认保存', 'success');
                    this.showStep(5);
                    this.showFinalResult(imageUrl);
                } catch (error) {
                    this.ui.showToast('确认失败：' + error.message, 'error');
                }
            },
            // 重新生成
            () => {
                this.showStep(2);
                this.ui.showToast('请重新选择发型', 'info');
            }
        );
    }

    /**
     * 显示最终结果
     */
    showFinalResult(imageUrl) {
        const resultImg = document.getElementById('result-img');
        if (resultImg) {
            resultImg.src = imageUrl;
        }

        // 绑定下载按钮
        const downloadBtn = document.getElementById('download-btn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => {
                this.downloadImage(imageUrl);
            });
        }

        // 绑定重新开始按钮
        const restartBtn = document.getElementById('restart-btn');
        if (restartBtn) {
            restartBtn.addEventListener('click', () => {
                this.reset();
                this.showStep(1);
            });
        }
    }

    /**
     * 下载图片
     */
    downloadImage(imageUrl) {
        const link = document.createElement('a');
        link.href = imageUrl;
        link.download = `hairstyle_${Date.now()}.jpg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        this.ui.showToast('下载已开始', 'success');
    }

    /**
     * 显示步骤
     */
    showStep(stepNumber) {
        // 隐藏所有步骤
        document.querySelectorAll('.step-section').forEach(section => {
            section.classList.remove('active');
        });

        // 显示当前步骤
        const currentSection = document.getElementById(`step-${stepNumber}`);
        if (currentSection) {
            currentSection.classList.add('active');
        }

        // 更新步骤指示器
        this.updateStepIndicator(stepNumber);

        this.currentStep = stepNumber;
    }

    /**
     * 更新步骤指示器
     */
    updateStepIndicator(currentStep) {
        const steps = document.querySelectorAll('.step-indicator .step');
        steps.forEach((step, index) => {
            const stepNum = index + 1;
            step.classList.remove('active', 'completed');
            
            if (stepNum === currentStep) {
                step.classList.add('active');
            } else if (stepNum < currentStep) {
                step.classList.add('completed');
            }
        });
    }

    /**
     * 重置应用
     */
    reset() {
        this.uploadedPhotos = [];
        this.selectedHairstyle = null;
        this.customDescription = '';
        this.currentTask = null;

        // 清理 UI
        document.getElementById('photo-preview').innerHTML = '';
        document.getElementById('upload-area').classList.remove('has-files');
        document.querySelectorAll('.hairstyle-card').forEach(c => c.classList.remove('selected'));
        document.getElementById('custom-desc').value = '';

        // 断开 WebSocket
        if (this.wsManager) {
            this.wsManager.disconnect();
            this.wsManager = null;
        }
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.app = new HairstyleApp();
});
