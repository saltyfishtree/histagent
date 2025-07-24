import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { 
  Message, 
  Session, 
  ToolCall, 
  UIState, 
  User, 
  ConnectionStatus,
  UploadProgress 
} from '../types';

// 主状态接口
interface AppState {
  // UI状态
  ui: UIState;
  setUI: (updates: Partial<UIState>) => void;
  toggleSidebar: () => void;
  toggleSidebarMobile: () => void;
  toggleToolPanel: () => void;
  
  // 用户状态
  user: User | null;
  setUser: (user: User | null) => void;
  
  // 会话状态
  sessions: Session[];
  currentSessionId: string | null;
  getCurrentSession: () => Session | null;
  createSession: () => Session;
  switchSession: (sessionId: string) => void;
  updateSession: (sessionId: string, updates: Partial<Session>) => void;
  deleteSession: (sessionId: string) => void;
  
  // 消息状态
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  updateMessage: (messageId: string, updates: Partial<Message>) => void;
  deleteMessage: (messageId: string) => void;
  
  // 工具调用状态
  toolCalls: ToolCall[];
  addToolCall: (toolCall: Omit<ToolCall, 'id'>) => void;
  updateToolCall: (toolCallId: string, updates: Partial<ToolCall>) => void;
  clearToolCalls: () => void;
  
  // 连接状态
  connectionStatus: ConnectionStatus;
  setConnectionStatus: (status: ConnectionStatus) => void;
  
  // 文件上传状态
  uploadProgress: UploadProgress[];
  addUploadProgress: (progress: UploadProgress) => void;
  updateUploadProgress: (fileId: string, updates: Partial<UploadProgress>) => void;
  removeUploadProgress: (fileId: string) => void;
}

// 生成UUID
function generateId(): string {
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
}

// 创建store
export const useAppStore = create<AppState>()(
  subscribeWithSelector((set, get) => ({
    // 初始UI状态
    ui: {
      sidebarCollapsed: false,
      sidebarMobileOpen: false,
      toolPanelOpen: false,
      isLoading: false,
      connectionStatus: 'disconnected',
    },
    
    setUI: (updates) =>
      set((state) => ({
        ui: { ...state.ui, ...updates }
      })),
    
    toggleSidebar: () =>
      set((state) => ({
        ui: { ...state.ui, sidebarCollapsed: !state.ui.sidebarCollapsed }
      })),
    
    toggleSidebarMobile: () =>
      set((state) => ({
        ui: { ...state.ui, sidebarMobileOpen: !state.ui.sidebarMobileOpen }
      })),
    
    toggleToolPanel: () =>
      set((state) => ({
        ui: { ...state.ui, toolPanelOpen: !state.ui.toolPanelOpen }
      })),
    
    // 用户状态
    user: null,
    setUser: (user) => set({ user }),
    
    // 会话状态
    sessions: [],
    currentSessionId: null,
    
    getCurrentSession: () => {
      const { sessions, currentSessionId } = get();
      return sessions.find(s => s.id === currentSessionId) || null;
    },
    
    createSession: () => {
      const newSession: Session = {
        id: generateId(),
        title: '新对话',
        messages: [],
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      
      set((state) => ({
        sessions: [newSession, ...state.sessions],
        currentSessionId: newSession.id,
      }));
      
      return newSession;
    },
    
    switchSession: (sessionId) => set({ currentSessionId: sessionId }),
    
    updateSession: (sessionId, updates) =>
      set((state) => ({
        sessions: state.sessions.map(session =>
          session.id === sessionId
            ? { ...session, ...updates, updatedAt: new Date() }
            : session
        )
      })),
    
    deleteSession: (sessionId) =>
      set((state) => {
        const newSessions = state.sessions.filter(s => s.id !== sessionId);
        const newCurrentId = state.currentSessionId === sessionId
          ? (newSessions[0]?.id || null)
          : state.currentSessionId;
        
        return {
          sessions: newSessions,
          currentSessionId: newCurrentId,
        };
      }),
    
    // 消息操作
    addMessage: (messageData) => {
      const message: Message = {
        ...messageData,
        id: generateId(),
        timestamp: new Date(),
      };
      
      const { currentSessionId } = get();
      if (!currentSessionId) return;
      
      set((state) => ({
        sessions: state.sessions.map(session =>
          session.id === currentSessionId
            ? {
                ...session,
                messages: [...session.messages, message],
                updatedAt: new Date(),
                title: session.messages.length === 0 && message.role === 'user' 
                  ? message.content.slice(0, 30) + (message.content.length > 30 ? '...' : '')
                  : session.title
              }
            : session
        )
      }));
    },
    
    updateMessage: (messageId, updates) => {
      const { currentSessionId } = get();
      if (!currentSessionId) return;
      
      set((state) => ({
        sessions: state.sessions.map(session =>
          session.id === currentSessionId
            ? {
                ...session,
                messages: session.messages.map(msg =>
                  msg.id === messageId ? { ...msg, ...updates } : msg
                ),
                updatedAt: new Date(),
              }
            : session
        )
      }));
    },
    
    deleteMessage: (messageId) => {
      const { currentSessionId } = get();
      if (!currentSessionId) return;
      
      set((state) => ({
        sessions: state.sessions.map(session =>
          session.id === currentSessionId
            ? {
                ...session,
                messages: session.messages.filter(msg => msg.id !== messageId),
                updatedAt: new Date(),
              }
            : session
        )
      }));
    },
    
    // 工具调用状态
    toolCalls: [],
    
    addToolCall: (toolCallData) => {
      const toolCall: ToolCall = {
        ...toolCallData,
        id: generateId(),
      };
      
      set((state) => ({
        toolCalls: [...state.toolCalls, toolCall]
      }));
    },
    
    updateToolCall: (toolCallId, updates) =>
      set((state) => ({
        toolCalls: state.toolCalls.map(call =>
          call.id === toolCallId ? { ...call, ...updates } : call
        )
      })),
    
    clearToolCalls: () => set({ toolCalls: [] }),
    
    // 连接状态
    connectionStatus: 'disconnected',
    setConnectionStatus: (status) => 
      set((state) => ({ 
        connectionStatus: status,
        ui: { ...state.ui, connectionStatus: status }
      })),
    
    // 文件上传状态
    uploadProgress: [],
    
    addUploadProgress: (progress) =>
      set((state) => ({
        uploadProgress: [...state.uploadProgress, progress]
      })),
    
    updateUploadProgress: (fileId, updates) =>
      set((state) => ({
        uploadProgress: state.uploadProgress.map(progress =>
          progress.fileId === fileId ? { ...progress, ...updates } : progress
        )
      })),
    
    removeUploadProgress: (fileId) =>
      set((state) => ({
        uploadProgress: state.uploadProgress.filter(progress => 
          progress.fileId !== fileId
        )
      })),
  }))
);

// 选择器hooks
export const useUI = () => useAppStore((state) => state.ui);
export const useUser = () => useAppStore((state) => state.user);
export const useSessions = () => useAppStore((state) => state.sessions);
export const useCurrentSession = () => useAppStore((state) => state.getCurrentSession());
export const useToolCalls = () => useAppStore((state) => state.toolCalls);
export const useConnectionStatus = () => useAppStore((state) => state.connectionStatus);
export const useUploadProgress = () => useAppStore((state) => state.uploadProgress); 