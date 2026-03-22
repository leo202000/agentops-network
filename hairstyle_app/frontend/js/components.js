/**
 * UI 组件模块
 * 可复用的界面组件
 */

class UIComponents {
    constructor() {
        this.toastContainer = null;
        this.modalContainer = null;
        this.init();
    }

    init() {
        // 创建 Toast 容器
        this.toastContainer = document.createElement('div');
        this.toastContainer.className = 'toast-container';
        document.body.appendChild(this.toastContainer);

        // 创建 Modal 容器
        this.modalContainer = document.createElement('div');
        this.modalContainer.className = 'modal-container';
        document.body.appendChild(this.modalContainer);
    }

    /**
     * 显示 Toast 提示
     */
    showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        };

        toast.innerHTML = `
            <span class="toast-icon">${icons[type]}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close">&times;</button>
        `;

        // 关闭按钮
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.hideToast(toast);
        });

        this.toastContainer.appendChild(toast);

        // 自动隐藏
        if (duration > 0) {
            setTimeout(() => {
                this.hideToast(toast);
            }, duration);
        }

        return toast;
    }

    hideToast(toast) {
        toast.classList.add('toast-hiding');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }

    /**
     * 显示 Modal 弹窗
     */
    showModal(options) {
        const {
            title = '',
            content = '',
            buttons = [],
            closable = true,
            onClose = null
        } = options;

        const modal = document.createElement('div');
        modal.className = 'modal-overlay';

        let buttonsHtml = buttons.map(btn => `
            <button class="btn ${btn.class || 'btn-secondary'}" data-action="${btn.action}">
                ${btn.text}
            </button>
        `).join('');

        modal.innerHTML = `
            <div class="modal-content">
                ${closable ? '<button class="modal-close">&times;</button>' : ''}
                ${title ? `<h3 class="modal-title">${title}</h3>` : ''}
                <div class="modal-body">${content}</div>
                ${buttons.length ? `<div class="modal-footer">${buttonsHtml}</div>` : ''}
            </div>
        `;

        // 关闭按钮
        if (closable) {
            modal.querySelector('.modal-close').addEventListener('click', () => {
                this.hideModal(modal);
                if (onClose) onClose();
            });

            // 点击遮罩关闭
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal(modal);
                    if (onClose) onClose();
                }
            });
        }

        // 按钮事件
        buttons.forEach(btn => {
            const btnEl = modal.querySelector(`[data-action="${btn.action}"]`);
            if (btnEl) {
                btnEl.addEventListener('click', () => {
                    if (btn.onClick) btn.onClick();
                    if (btn.closeOnClick !== false) {
                        this.hideModal(modal);
                    }
                });
            }
        });

        this.modalContainer.appendChild(modal);

        // 显示动画
        requestAnimationFrame(() => {
            modal.classList.add('modal-visible');
        });

        return modal;
    }

    hideModal(modal) {
        modal.classList.remove('modal-visible');
        setTimeout(() => {
            modal.remove();
        }, 300);
    }

    /**
     * 显示确认对话框
     */
    confirm(message, onConfirm, onCancel = null) {
        return this.showModal({
            title: '确认',
            content: `<p>${message}</p>`,
            buttons: [
                {
                    text: '取消',
                    action: 'cancel',
                    class: 'btn-secondary',
                    onClick: onCancel
                },
                {
                    text: '确认',
                    action: 'confirm',
                    class: 'btn-primary',
                    onClick: onConfirm
                }
            ]
        });
    }

    /**
     * 显示加载动画
     */
    showLoading(message = '加载中...') {
        const loading = document.createElement('div');
        loading.className = 'loading-overlay';
        loading.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <p class="loading-message">${message}</p>
            </div>
        `;
        document.body.appendChild(loading);
        return loading;
    }

    hideLoading(loading) {
        loading.classList.add('loading-hiding');
        setTimeout(() => {
            loading.remove();
        }, 300);
    }

    /**
     * 更新进度条
     */
    updateProgress(progress, status, queueInfo = null) {
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        const progressStatus = document.getElementById('progress-status');
        const queueInfoEl = document.getElementById('queue-info');

        if (progressFill) {
            progressFill.style.width = `${progress}%`;
        }

        if (progressText) {
            progressText.textContent = `${progress}%`;
        }

        if (progressStatus) {
            progressStatus.textContent = status;
        }

        if (queueInfoEl && queueInfo) {
            queueInfoEl.innerHTML = `
                <p>队列位置：${queueInfo.position}/${queueInfo.total}</p>
                <p>预计等待：${queueInfo.estimatedWait}s</p>
            `;
        }
    }

    /**
     * 显示结果图片
     */
    showResult(imageUrl, onConfirm, onRetry) {
        return this.showModal({
            title: '发型预览',
            content: `
                <div class="result-preview">
                    <img src="${imageUrl}" alt="生成的发型" />
                </div>
                <p class="result-hint">满意吗？确认后保存结果</p>
            `,
            buttons: [
                {
                    text: '重新生成',
                    action: 'retry',
                    class: 'btn-secondary',
                    onClick: onRetry
                },
                {
                    text: '确认保存',
                    action: 'confirm',
                    class: 'btn-primary',
                    onClick: onConfirm
                }
            ]
        });
    }
}

// 导出
window.UIComponents = UIComponents;
