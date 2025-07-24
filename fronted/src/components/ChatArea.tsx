import React, { useEffect, useRef } from 'react';
import { Session } from '../types';
import MessageItem from './MessageItem';

interface ChatAreaProps {
  session: Session;
}

const ChatArea: React.FC<ChatAreaProps> = ({ session }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // 自动滚动到底部
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [session.messages]);

  return (
    <div className="chat-container flex-1 overflow-y-auto p-8">
      <div className="max-w-3xl mx-auto">
        {session.messages.map((message) => (
          <MessageItem key={message.id} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatArea; 