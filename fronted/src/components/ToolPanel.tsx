import React from 'react';
import { useToolCalls } from '../store';
import clsx from 'clsx';

const ToolPanel: React.FC = () => {
  const toolCalls = useToolCalls();

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return 'sync';
      case 'success':
        return 'check_circle';
      case 'error':
        return 'error';
      default:
        return 'schedule';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return '等待调用';
      case 'running':
        return '正在调用';
      case 'success':
        return '调用成功';
      case 'error':
        return '调用失败';
      default:
        return '未知状态';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'text-gray-600 bg-gray-100';
      case 'running':
        return 'text-blue-600 bg-blue-100';
      case 'success':
        return 'text-green-600 bg-green-100';
      case 'error':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="tool-panel w-96 bg-white border-l border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold flex items-center">
          <span className="material-icons mr-2 text-blue-600">build_circle</span>
          工具调用
        </h3>
      </div>
      
      <div className="flex-1 p-4 space-y-4 overflow-y-auto">
        {toolCalls.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <span className="material-icons text-4xl mb-2">build</span>
            <p>暂无工具调用</p>
          </div>
        ) : (
          toolCalls.map((toolCall) => (
            <div 
              key={toolCall.id} 
              className={clsx('tool-call bg-gray-50 p-4 rounded-lg', toolCall.status)}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-sm text-gray-800 flex items-center">
                  <span className="material-icons mr-2 text-blue-500">
                    {toolCall.name === 'search' ? 'search' : 
                     toolCall.name === 'document' ? 'description' :
                     toolCall.name === 'translate' ? 'g_translate' : 'build'}
                  </span>
                  {toolCall.name === 'search' ? '搜索引擎' :
                   toolCall.name === 'document' ? '文档分析' :
                   toolCall.name === 'translate' ? '多语言翻译' : '工具调用'}
                </span>
                <span className={clsx('text-xs px-2 py-1 rounded-full font-medium', getStatusColor(toolCall.status))}>
                  <span className={clsx('material-icons mr-1', {
                    'animate-spin': toolCall.status === 'running'
                  })} style={{ fontSize: '16px' }}>
                    {getStatusIcon(toolCall.status)}
                  </span>
                  {getStatusText(toolCall.status)}
                </span>
              </div>
              
              {/* 工具参数 */}
              {toolCall.parameters && (
                <div className="mt-3 bg-white p-3 rounded-md border border-gray-200">
                  <p className="text-sm font-medium text-gray-700">调用参数:</p>
                  <div className="text-sm text-gray-500 mt-1">
                    {typeof toolCall.parameters === 'object' ? (
                      Object.entries(toolCall.parameters).map(([key, value]) => (
                        <div key={key} className="flex">
                          <span className="font-medium mr-2">{key}:</span>
                          <span>{String(value)}</span>
                        </div>
                      ))
                    ) : (
                      <span>{String(toolCall.parameters)}</span>
                    )}
                  </div>
                </div>
              )}
              
              {/* 错误信息 */}
              {toolCall.error && (
                <div className="mt-3 bg-white p-3 rounded-md border border-red-200">
                  <p className="text-sm font-medium text-red-700">错误信息:</p>
                  <p className="text-sm text-red-500 mt-1">{toolCall.error}</p>
                </div>
              )}
              
              {/* 执行时间 */}
              {toolCall.startTime && (
                <div className="mt-2 text-xs text-gray-400">
                  开始时间: {toolCall.startTime.toLocaleTimeString()}
                  {toolCall.endTime && (
                    <span className="ml-2">
                      耗时: {Math.round((toolCall.endTime.getTime() - toolCall.startTime.getTime()) / 1000)}s
                    </span>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ToolPanel; 