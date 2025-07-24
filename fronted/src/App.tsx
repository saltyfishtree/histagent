import React, { useEffect } from 'react';
import { useAppStore } from './store';
import websocketService from './services/websocket';
import Sidebar from './components/Sidebar';
import MainContent from './components/MainContent';
import ToolPanel from './components/ToolPanel';
import { useUI } from './store';

const App: React.FC = () => {
  const { sidebarCollapsed, sidebarMobileOpen } = useUI();
  const setUser = useAppStore((state) => state.setUser);

  useEffect(() => {
    // 初始化用户信息
    setUser({
      id: '1',
      name: 'Research User',
      email: 'user@example.com',
      plan: 'premium',
    });

    // 尝试连接WebSocket
    websocketService.connect().catch(error => {
      console.error('WebSocket连接失败:', error);
    });

    // 清理函数
    return () => {
      websocketService.disconnect();
    };
  }, [setUser]);

  return (
    <div className="main-layout flex h-screen bg-white">
      {/* 侧边栏 */}
      <Sidebar 
        collapsed={sidebarCollapsed}
        mobileOpen={sidebarMobileOpen}
      />
      
      {/* 主内容区域 */}
      <div className="content-area flex-1 flex">
        <MainContent />
        <ToolPanel />
      </div>
      
      {/* 移动端遮罩 */}
      {sidebarMobileOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={() => useAppStore.getState().toggleSidebarMobile()}
        />
      )}
    </div>
  );
};

export default App; 