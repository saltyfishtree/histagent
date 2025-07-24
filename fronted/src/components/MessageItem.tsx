import React from 'react';
import { Message } from '../types';
import clsx from 'clsx';
import fileUploadService from '../services/fileUpload';

interface MessageItemProps {
  message: Message;
}

const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={clsx('message flex mb-4', isUser ? 'user justify-end' : 'assistant')}>
      {!isUser && (
        <div className="flex-shrink-0 mr-3">
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <span className="material-icons text-white text-sm">smart_toy</span>
          </div>
        </div>
      )}
      
      <div className={clsx('message-content', isUser ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900')}>
        {/* 消息内容 */}
        <div className="whitespace-pre-wrap">{message.content}</div>
        
        {/* 附件 */}
        {message.attachments && message.attachments.length > 0 && (
          <div className="mt-3 space-y-2">
            {message.attachments.map((attachment) => (
              <div key={attachment.id} className="flex items-center space-x-2 p-2 bg-black bg-opacity-10 rounded">
                <span className="material-icons text-sm">
                  {fileUploadService.getFileIcon(attachment.type)}
                </span>
                <span className="text-sm">{attachment.name}</span>
                <span className="text-xs opacity-75">
                  ({fileUploadService.formatFileSize(attachment.size)})
                </span>
                {attachment.url && (
                  <a 
                    href={attachment.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-xs underline hover:no-underline"
                  >
                    查看
                  </a>
                )}
              </div>
            ))}
          </div>
        )}
        
        {/* 时间戳 */}
        <div className={clsx('text-xs mt-2 opacity-75', isUser ? 'text-right' : 'text-left')}>
          {message.timestamp.toLocaleTimeString()}
        </div>
      </div>
      
      {isUser && (
        <div className="flex-shrink-0 ml-3">
          <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center">
            <span className="material-icons text-white text-sm">person</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default MessageItem; 