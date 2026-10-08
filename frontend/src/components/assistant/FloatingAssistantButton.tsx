import React from 'react';
import { MessageSquare } from 'lucide-react';

export const FloatingAssistantButton: React.FC<{ onClick: () => void }> = ({ onClick }) => {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-6 right-6 z-40 bg-gov-blue hover:bg-blue-900 text-white p-4 rounded-full shadow-xl border-2 border-gov-gold flex items-center space-x-2 transition transform hover:scale-105"
      title="Open AccessGov AI Assistant"
    >
      <MessageSquare className="w-6 h-6 text-gov-gold" />
      <span className="hidden sm:inline font-bold text-xs pr-1">Ask AccessGov AI</span>
    </button>
  );
};

export default FloatingAssistantButton;
