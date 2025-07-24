import { WebSocketMessage, ConnectionStatus } from '../types';
import { useAppStore } from '../store';

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private heartbeatInterval: number | null = null;
  private isManualClose = false;

  constructor(private url: string = 'ws://localhost:8000/ws/') {}

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.isManualClose = false;
        useAppStore.getState().setConnectionStatus('connecting');
        
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
          console.log('WebSocket连接已建立');
          this.reconnectAttempts = 0;
          useAppStore.getState().setConnectionStatus('connected');
          this.startHeartbeat();
          resolve();
        };
        
        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('解析WebSocket消息失败:', error);
          }
        };
        
        this.ws.onerror = (error) => {
          console.error('WebSocket错误:', error);
          useAppStore.getState().setConnectionStatus('error');
          reject(error);
        };
        
        this.ws.onclose = (event) => {
          console.log('WebSocket连接已关闭:', event.code, event.reason);
          this.stopHeartbeat();
          
          if (!this.isManualClose && this.reconnectAttempts < this.maxReconnectAttempts) {
            useAppStore.getState().setConnectionStatus('connecting');
            this.scheduleReconnect();
          } else {
            useAppStore.getState().setConnectionStatus('disconnected');
          }
        };
        
      } catch (error) {
        useAppStore.getState().setConnectionStatus('error');
        reject(error);
      }
    });
  }

  disconnect(): void {
    this.isManualClose = true;
    this.stopHeartbeat();
    
    if (this.ws) {
      this.ws.close(1000, '用户主动断开连接');
      this.ws = null;
    }
    
    useAppStore.getState().setConnectionStatus('disconnected');
  }

  sendMessage(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket未连接，无法发送消息');
      throw new Error('WebSocket未连接');
    }
  }

  private handleMessage(message: WebSocketMessage): void {
    const store = useAppStore.getState();
    
    switch (message.type) {
      case 'message':
        // 处理消息回复
        store.addMessage({
          content: message.data.content,
          role: 'assistant',
          attachments: message.data.attachments,
        });
        break;
        
      case 'tool_call':
        // 处理工具调用状态更新
        if (message.data.action === 'start') {
          store.addToolCall({
            name: message.data.name,
            status: 'running',
            parameters: message.data.parameters,
            startTime: new Date(),
          });
        } else if (message.data.action === 'update') {
          store.updateToolCall(message.data.id, {
            status: message.data.status,
            result: message.data.result,
            error: message.data.error,
            endTime: message.data.status === 'success' || message.data.status === 'error' 
              ? new Date() 
              : undefined,
          });
        }
        break;
        
      case 'status':
        // 处理状态更新
        if (message.data.type === 'connection') {
          store.setConnectionStatus(message.data.status);
        }
        break;
        
      case 'error':
        // 处理错误消息
        console.error('服务器错误:', message.data);
        store.addMessage({
          content: `错误: ${message.data.message || '服务器错误'}`,
          role: 'assistant',
        });
        break;
        
      default:
        console.warn('未知的WebSocket消息类型:', message.type);
    }
  }

  private scheduleReconnect(): void {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`${delay}ms后尝试第${this.reconnectAttempts}次重连...`);
    
    setTimeout(() => {
      if (!this.isManualClose) {
        this.connect().catch(error => {
          console.error('重连失败:', error);
        });
      }
    }, delay);
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000); // 每30秒发送一次心跳
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  getConnectionStatus(): ConnectionStatus {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
      case WebSocket.CLOSED:
        return 'disconnected';
      default:
        return 'error';
    }
  }
}

// 创建单例实例
export const websocketService = new WebSocketService();

// 导出默认实例
export default websocketService; 