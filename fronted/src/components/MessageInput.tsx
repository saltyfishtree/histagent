import React, { useState, useRef } from 'react';
import { useAppStore, useConnectionStatus } from '../store';
import websocketService from '../services/websocket';
import fileUploadService from '../services/fileUpload';
import { Attachment } from '../types';

const MessageInput: React.FC = () => {
  const [message, setMessage] = useState('');
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  const connectionStatus = useConnectionStatus();
  const { addMessage, currentSessionId } = useAppStore();

  const isConnected = connectionStatus === 'connected';
  const canSend = message.trim() || attachments.length > 0;

  const handleSend = async () => {
    if (!canSend || !isConnected) return;

    const content = message.trim();
    if (!content && attachments.length === 0) return;

    // 确保有当前会话
    let sessionId = currentSessionId;
    if (!sessionId) {
      const newSession = useAppStore.getState().createSession();
      sessionId = newSession.id;
    }

    // 添加用户消息到本地状态
    addMessage({
      content,
      role: 'user',
      attachments: attachments.length > 0 ? attachments : undefined,
    });

    // 发送到服务器
    try {
      websocketService.sendMessage({
        type: 'user_message',
        data: {
          content,
          attachments,
          sessionId,
        },
      });
    } catch (error) {
      console.error('发送消息失败:', error);
      addMessage({
        content: '发送消息失败，请检查网络连接',
        role: 'assistant',
      });
    }

    // 清空输入
    setMessage('');
    setAttachments([]);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    
    // 自动调整高度
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
  };

  const handleFileSelect = async (files: FileList) => {
    try {
      const newAttachments = await fileUploadService.uploadFiles(files);
      setAttachments(prev => [...prev, ...newAttachments]);
    } catch (error) {
      console.error('文件上传失败:', error);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files) {
      handleFileSelect(e.dataTransfer.files);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const removeAttachment = (attachmentId: string) => {
    setAttachments(prev => prev.filter(att => att.id !== attachmentId));
  };

  return (
    <footer className="input-container p-4 bg-white border-t border-gray-200">
      <div className="max-w-3xl mx-auto">
        {/* 附件预览 */}
        {attachments.length > 0 && (
          <div className="mb-3 flex flex-wrap gap-2">
            {attachments.map((attachment) => (
              <div key={attachment.id} className="flex items-center bg-gray-100 rounded-lg px-3 py-2">
                <span className="material-icons text-gray-500 mr-2">
                  {fileUploadService.getFileIcon(attachment.type)}
                </span>
                <span className="text-sm text-gray-700 mr-2">{attachment.name}</span>
                <button
                  onClick={() => removeAttachment(attachment.id)}
                  className="text-gray-400 hover:text-red-500"
                >
                  <span className="material-icons text-sm">close</span>
                </button>
              </div>
            ))}
          </div>
        )}

        <div 
          className={`relative file-drop-zone ${isDragging ? 'dragover' : ''}`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleTextareaChange}
            onKeyPress={handleKeyPress}
            placeholder={isConnected ? "请输入您的问题..." : "等待连接服务器..."}
            disabled={!isConnected}
            className="w-full py-3 pl-12 pr-20 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none min-h-[48px] max-h-[120px]"
            rows={1}
          />
          
          {/* 左侧附件按钮 */}
          <input
            ref={fileInputRef}
            type="file"
            multiple
            className="hidden"
            onChange={(e) => e.target.files && handleFileSelect(e.target.files)}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            disabled={!isConnected}
          >
            <span className="material-icons">attach_file</span>
          </button>
          
          {/* 右侧按钮 */}
          <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center space-x-2">
            <button className="text-gray-400 hover:text-gray-600">
              <span className="material-icons">sentiment_satisfied_alt</span>
            </button>
            <button
              onClick={handleSend}
              disabled={!canSend || !isConnected}
              className={`p-2 rounded-lg transition-colors ${
                canSend && isConnected
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              }`}
            >
              <span className="material-icons">send</span>
            </button>
          </div>
        </div>
        
        <p className="text-xs text-center text-gray-500 mt-2">
          HistAgent 可以帮助您进行历史研究、文档分析和多语言翻译 ✨
        </p>
      </div>
    </footer>
  );
};

export default MessageInput; 