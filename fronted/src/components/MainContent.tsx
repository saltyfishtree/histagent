import React from 'react';
import { useCurrentSession, useConnectionStatus, useUser } from '../store';
import ChatArea from './ChatArea';
import MessageInput from './MessageInput';
import WelcomeScreen from './WelcomeScreen';

const MainContent: React.FC = () => {
  const currentSession = useCurrentSession();
  const connectionStatus = useConnectionStatus();
  const user = useUser();

  const getStatusText = () => {
    switch (connectionStatus) {
      case 'connected':
        return '已连接';
      case 'connecting':
        return '正在连接服务器...';
      case 'disconnected':
        return '未连接';
      case 'error':
        return '连接错误';
      default:
        return '未知状态';
    }
  };

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'text-green-600';
      case 'connecting':
        return 'text-yellow-600';
      case 'disconnected':
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      {/* 头部 */}
      <header className="flex items-center justify-between p-4 border-b border-gray-200 bg-white">
        <div>
          <h2 className="text-lg font-semibold">HistAgent 对话</h2>
          <p className="text-sm text-gray-500">与AI助手对话，获取专业历史研究支持</p>
        </div>
        <div className="flex items-center space-x-4">
          {/* 连接状态 */}
          <div className="flex items-center space-x-2">
            <div className={`status-indicator ${connectionStatus}`}></div>
            <span className={`text-sm ${getStatusColor()}`}>
              {getStatusText()}
            </span>
          </div>
          
          {/* 用户信息 */}
          {user && (
            <div className="flex items-center space-x-2">
              <span className="material-icons text-purple-600">account_circle</span>
              <div className="text-sm">
                <p className="font-semibold">{user.name}</p>
                <p className="text-purple-600">
                  {user.plan === 'premium' ? 'Premium Plan' : 'Free Plan'}
                </p>
              </div>
              {user.plan === 'premium' && (
                <span className="material-icons text-yellow-500">star</span>
              )}
            </div>
          )}
        </div>
      </header>

      {/* 主内容区 */}
      <main className="flex-1 flex bg-gray-50 overflow-hidden">
        <div className="flex-1 flex flex-col">
          {currentSession && currentSession.messages.length > 0 ? (
            <ChatArea session={currentSession} />
          ) : (
            <WelcomeScreen />
          )}
          
          {/* 消息输入区 */}
          <MessageInput />
        </div>
      </main>
    </div>
  );
};

export default MainContent; 