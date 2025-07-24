import React from 'react';

const WelcomeScreen: React.FC = () => {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8">
      <div className="text-center">
        <div className="inline-block bg-blue-600 p-6 rounded-2xl mb-6">
          <span className="material-icons text-white" style={{ fontSize: '48px' }}>history_edu</span>
        </div>
        <h1 className="text-4xl font-bold mb-2">Welcome to HistAgent</h1>
        <p className="text-gray-600 max-w-md mx-auto">
          Ask me anything about history, upload documents to analyze, or start a research project.
        </p>
        <div className="mt-4 text-sm text-gray-500">
          <a className="text-blue-600 hover:underline" href="#">历史研究</a>
          <span className="mx-2">·</span>
          <a className="text-blue-600 hover:underline" href="#">文档分析</a>
          <span className="mx-2">·</span>
          <a className="text-blue-600 hover:underline" href="#">多语言翻译</a>
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen; 