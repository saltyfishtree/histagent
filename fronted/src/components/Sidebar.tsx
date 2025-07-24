import React from 'react';
import { useAppStore, useSessions, useUser } from '../store';
import clsx from 'clsx';

interface SidebarProps {
  collapsed: boolean;
  mobileOpen: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed, mobileOpen }) => {
  const sessions = useSessions();
  const user = useUser();
  const { 
    toggleSidebar, 
    toggleSidebarMobile,
    createSession, 
    switchSession, 
    deleteSession, 
    currentSessionId 
  } = useAppStore();

  const handleNewChat = () => {
    createSession();
    // 移动端创建新会话后关闭侧边栏
    if (mobileOpen) {
      toggleSidebarMobile();
    }
  };

  const handleSessionClick = (sessionId: string) => {
    switchSession(sessionId);
    // 移动端切换会话后关闭侧边栏
    if (mobileOpen) {
      toggleSidebarMobile();
    }
  };

  return (
    <div 
      className={clsx(
        'sidebar bg-gray-50 flex flex-col p-4 transition-all duration-300',
        collapsed ? 'collapsed' : 'w-64',
        mobileOpen ? 'mobile-open' : ''
      )}
      style={{ width: collapsed ? '80px' : '260px' }}
    >
      {/* 头部 */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center">
          <div className="bg-blue-600 p-2 rounded-lg mr-3">
            <span className="material-icons text-white">history_edu</span>
          </div>
          <h1 className="text-xl font-bold logo-text">HistAgent</h1>
        </div>
        <button 
          className="toggle-button p-2 rounded-md hover:bg-gray-200" 
          onClick={toggleSidebar}
        >
          <span className="material-icons">menu</span>
        </button>
      </div>

      {/* 新建会话按钮 */}
      <button 
        className="w-full bg-blue-600 text-white flex items-center justify-center py-3 rounded-lg hover:bg-blue-700 transition-colors mb-6"
        onClick={handleNewChat}
      >
        <span className="material-icons">add</span>
        <span className="ml-2 font-semibold new-chat-text">新建会话</span>
      </button>

      {/* 导航菜单 */}
      <nav className="flex-grow">
        <ul>
          <li className="mb-2">
            <a className="flex items-center p-3 text-gray-700 rounded-lg bg-blue-100 text-blue-600 font-semibold" href="#">
              <span className="material-icons">smart_toy</span>
              <span className="ml-4 sidebar-text">智能对话</span>
            </a>
          </li>
          <li className="mb-2">
            <a className="flex items-center p-3 text-gray-500 hover:bg-gray-200 rounded-lg" href="#">
              <span className="material-icons">build</span>
              <span className="ml-4 sidebar-text">工具箱</span>
            </a>
          </li>
          <li className="mb-2">
            <a className="flex items-center p-3 text-gray-500 hover:bg-gray-200 rounded-lg" href="#">
              <span className="material-icons">science</span>
              <span className="ml-4 sidebar-text">深度研究</span>
            </a>
          </li>
          <li className="mb-2">
            <a className="flex items-center p-3 text-gray-500 hover:bg-gray-200 rounded-lg" href="#">
              <span className="material-icons">history</span>
              <span className="ml-4 sidebar-text">历史记录</span>
            </a>
          </li>
        </ul>

        {/* 会话列表 */}
        {sessions.length > 0 && (
          <div className="mt-6">
            <h3 className="text-sm font-semibold text-gray-500 mb-3 sidebar-text">最近会话</h3>
            <ul className="space-y-1">
              {sessions.slice(0, 10).map((session) => (
                <li key={session.id}>
                  <div 
                    className={clsx(
                      'flex items-center p-2 rounded-lg cursor-pointer group',
                      session.id === currentSessionId 
                        ? 'bg-blue-100 text-blue-600' 
                        : 'text-gray-600 hover:bg-gray-200'
                    )}
                    onClick={() => handleSessionClick(session.id)}
                  >
                    <span className="material-icons text-sm mr-2">chat</span>
                    <span className="sidebar-text flex-1 text-sm truncate">
                      {session.title}
                    </span>
                    <button
                      className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded sidebar-text"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteSession(session.id);
                      }}
                    >
                      <span className="material-icons text-xs text-red-500">delete</span>
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </nav>

      {/* 底部 */}
      <div className="mt-auto">
        {sessions.length === 0 && (
          <div className="flex flex-col items-center text-center p-4 border-t border-gray-200">
            <div className="p-4 rounded-full bg-gray-200 mb-4">
              <span className="material-icons text-gray-500" style={{ fontSize: '36px' }}>chat</span>
            </div>
            <p className="text-gray-600 sidebar-footer-text">暂无会话历史</p>
            <p className="text-xs text-gray-400 sidebar-footer-text">开始对话以创建您的第一个会话</p>
          </div>
        )}
        
        {/* 用户信息 */}
        {user && (
          <div className="flex items-center justify-between text-sm text-gray-500 p-2 border-t border-gray-200">
            <div className="sidebar-text flex items-center">
              <span className="material-icons mr-2">account_circle</span>
              <div>
                <p className="font-semibold">{user.name}</p>
                <p className="text-xs">{user.plan === 'premium' ? 'Premium Plan' : 'Free Plan'}</p>
              </div>
            </div>
          </div>
        )}
        
        <div className="flex items-center justify-between text-sm text-gray-500 p-2 border-t border-gray-200">
          <span className="sidebar-text">v1.0.0</span>
          <span className="sidebar-text">© 2024 HistAgent</span>
        </div>
      </div>
    </div>
  );
};

export default Sidebar; 