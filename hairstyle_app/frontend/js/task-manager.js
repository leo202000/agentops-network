/**
 * 任务管理器 - 前端 API 客户端（带重试机制）
 */
class TaskManagerClient {
    constructor(baseUrl = 'http://localhost:8080') {
        this.baseUrl = baseUrl;
        this.maxRetries = 3;
        this.retryDelay = 1000; // 1 秒
        this.timeout = 30000; // 30 秒超时
    }

    /**
     * 通用请求方法（带重试）
     */
    async fetchWithRetry(url, options = {}, retries = 0) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);
            
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
            
        } catch (error) {
            // 如果是超时或网络错误，尝试重试
            if ((error.name === 'AbortError' || error.message.includes('network')) && retries < this.maxRetries) {
                console.log(`请求失败，重试 ${retries + 1}/${this.maxRetries}...`);
                await this.sleep(this.retryDelay * Math.pow(2, retries)); // 指数退避
                return this.fetchWithRetry(url, options, retries + 1);
            }
            
            throw error;
        }
    }

    /**
     * 延迟函数
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * 创建任务
     */
    async createTask(userId, photos, hairstyleChoice, description = '') {
        return this.fetchWithRetry(`${this.baseUrl}/api/task/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: userId,
                photos: photos,
                hairstyle_choice: hairstyleChoice,
                description: description
            })
        });
    }

    /**
     * 获取任务状态
     */
    async getTask(taskId) {
        return this.fetchWithRetry(`${this.baseUrl}/api/task/${taskId}`);
    }

    /**
     * 确认任务
     */
    async confirmTask(taskId) {
        return this.fetchWithRetry(`${this.baseUrl}/api/task/${taskId}/confirm`, {
            method: 'POST'
        });
    }

    /**
     * 获取用户任务列表
     */
    async getUserTasks(userId) {
        return this.fetchWithRetry(`${this.baseUrl}/api/user/${userId}/tasks`);
    }
}

// 导出
window.TaskManagerClient = TaskManagerClient;
