/**
 * WebSocket 管理器（带断线重连和降级机制）
 */
class WebSocketManager {
    constructor(wsUrl, httpUrl, onStatusChange) {
        this.wsUrl = wsUrl;
        this.httpUrl = httpUrl;
        this.onStatusChange = onStatusChange;
        
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.usePolling = false;
        this.pollingInterval = null;
        this.pollingDelay = 3000; // 3 秒轮询
        
        this.taskId = null;
        this.callbacks = [];
    }

    /**
     * 连接到 WebSocket
     */
    connect(taskId) {
        this.taskId = taskId;
        this.reconnectAttempts = 0;
        
        // 优先尝试 WebSocket
        this.tryWebSocket();
        
        // 同时启动 HTTP 轮询作为备选
        this.startPolling();
    }

    /**
     * 尝试 WebSocket 连接
     */
    tryWebSocket() {
        try {
            this.ws = new WebSocket(this.wsUrl.replace('{task_id}', this.taskId));
            
            this.ws.onopen = () => {
                console.log('✅ WebSocket 连接成功');
                this.reconnectAttempts = 0;
                this.updateStatus('connected');
                
                // 停止 HTTP 轮询（WebSocket 优先）
                this.stopPolling();
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.notifyCallbacks(data);
                } catch (e) {
                    console.error('WebSocket 消息解析失败:', e);
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('❌ WebSocket 错误:', error);
                this.updateStatus('error');
            };
            
            this.ws.onclose = () => {
                console.log('⚠️  WebSocket 关闭');
                this.updateStatus('disconnected');
                
                // 尝试重连
                this.tryReconnect();
            };
            
        } catch (e) {
            console.error('WebSocket 连接失败:', e);
            this.tryReconnect();
        }
    }

    /**
     * 尝试重连
     */
    tryReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts);
            
            console.log(`🔄 ${delay}ms 后尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                if (!this.usePolling) {
                    this.tryWebSocket();
                }
            }, delay);
        } else {
            console.log('❌ WebSocket 重连失败，降级到 HTTP 轮询');
            this.usePolling = true;
            this.startPolling();
        }
    }

    /**
     * 启动 HTTP 轮询
     */
    startPolling() {
        console.log('📡 启动 HTTP 轮询');
        this.updateStatus('polling');
        
        this.pollingInterval = setInterval(async () => {
            try {
                const data = await this.pollTaskStatus();
                this.notifyCallbacks(data);
                
                // 如果任务完成或失败，停止轮询
                if (data.status === 20 || data.status === 50) {
                    this.stopPolling();
                }
            } catch (e) {
                console.error('HTTP 轮询失败:', e);
            }
        }, this.pollingDelay);
    }

    /**
     * 轮询任务状态
     */
    async pollTaskStatus() {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 秒超时
        
        try {
            const response = await fetch(this.httpUrl.replace('{task_id}', this.taskId), {
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
            
        } catch (error) {
            clearTimeout(timeoutId);
            throw error;
        }
    }

    /**
     * 停止 HTTP 轮询
     */
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
            console.log('⏹️ 停止 HTTP 轮询');
        }
    }

    /**
     * 更新连接状态
     */
    updateStatus(status) {
        if (this.onStatusChange) {
            this.onStatusChange(status);
        }
    }

    /**
     * 添加回调
     */
    onMessage(callback) {
        this.callbacks.push(callback);
    }

    /**
     * 通知所有回调
     */
    notifyCallbacks(data) {
        this.callbacks.forEach(callback => {
            try {
                callback(data);
            } catch (e) {
                console.error('回调执行失败:', e);
            }
        });
    }

    /**
     * 断开连接
     */
    disconnect() {
        this.stopPolling();
        
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        
        this.callbacks = [];
    }
}

// 导出
window.WebSocketManager = WebSocketManager;
