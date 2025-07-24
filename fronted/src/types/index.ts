// 消息类型
export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  attachments?: Attachment[];
}

// 附件类型
export interface Attachment {
  id: string;
  name: string;
  type: string;
  size: number;
  url?: string;
  data?: ArrayBuffer;
}

// 工具调用类型
export interface ToolCall {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'success' | 'error';
  parameters?: Record<string, any>;
  result?: any;
  error?: string;
  startTime?: Date;
  endTime?: Date;
}

// 会话类型
export interface Session {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

// WebSocket消息类型
export interface WebSocketMessage {
  type: 'message' | 'tool_call' | 'status' | 'error';
  data: any;
  timestamp: Date;
}

// 连接状态
export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

// UI状态
export interface UIState {
  sidebarCollapsed: boolean;
  sidebarMobileOpen: boolean;
  toolPanelOpen: boolean;
  isLoading: boolean;
  connectionStatus: ConnectionStatus;
}

// 用户信息
export interface User {
  id: string;
  name: string;
  email: string;
  plan: 'free' | 'premium';
  avatar?: string;
}

// 工具定义
export interface ToolDefinition {
  name: string;
  description: string;
  parameters: Record<string, any>;
  icon: string;
  category: string;
}

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// 文件上传进度
export interface UploadProgress {
  fileId: string;
  progress: number;
  status: 'uploading' | 'completed' | 'error';
  error?: string;
} 