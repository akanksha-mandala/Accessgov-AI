import React, { createContext, useContext, useState, useEffect } from 'react';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  language?: string;
}

interface ConversationContextType {
  sessionId: string;
  messages: ChatMessage[];
  addMessage: (sender: 'user' | 'assistant', text: string, language?: string) => void;
  clearHistory: () => void;
  selectedLanguage: string;
  setSelectedLanguage: (lang: string) => void;
  isStreaming: boolean;
  setIsStreaming: (streaming: boolean) => void;
}

const ConversationContext = createContext<ConversationContextType | undefined>(undefined);

export const ConversationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [sessionId] = useState<string>(() => {
    return localStorage.getItem('accessgov_session_id') || `session_${Date.now()}`;
  });

  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    const saved = localStorage.getItem(`messages_${sessionId}`);
    return saved ? JSON.parse(saved) : [
      {
        id: 'msg_welcome',
        sender: 'assistant',
        text: selectedLanguage === 'te' ? 'నమస్కారం! నేను AccessGov AI. ప్రభుత్వ సేవలు, పథకాల అర్హత లేదా పత్రాల గురించి మీకు సహాయం చేయగలను.' : selectedLanguage === 'ta' ? 'வணக்கம்! நான் AccessGov AI. அரசு சேவைகள், திட்டத் தகுதி அல்லது ஆவணங்கள் குறித்து உங்களுக்கு உதவுகிறேன்.' : selectedLanguage === 'hi' ? 'नमस्ते! मैं AccessGov AI हूँ। सरकारी सेवाएं, योजना पात्रता और दस्तावेज़ों में मैं आपकी सहायता कर सकता हूँ।' : selectedLanguage === 'kn' ? 'ನಮಸ್ಕಾರ! ನಾನು AccessGov AI. ಸರ್ಕಾರಿ ಸೇವೆಗಳು, ಯೋಜನೆಗಳ ಅರ್ಹತೆ ಮತ್ತು ದಾಖಲೆಗಳ ಬಗ್ಗೆ ನಿಮಗೆ ಸಹಾಯ ಮಾಡುತ್ತೇನೆ.' : 'Namaste! I am AccessGov AI. I can help with government services, scheme eligibility, and documents.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        language: selectedLanguage
      }
    ];
  });

  const [selectedLanguage, setSelectedLanguage] = useState<string>(() => localStorage.getItem('accessgov_language') || 'en');

  useEffect(() => { localStorage.setItem('accessgov_language', selectedLanguage); }, [selectedLanguage]);
  const [isStreaming, setIsStreaming] = useState<boolean>(false);

  useEffect(() => {
    localStorage.setItem('accessgov_session_id', sessionId);
  }, [sessionId]);

  useEffect(() => {
    const trimmed = messages.slice(-20);
    localStorage.setItem(`messages_${sessionId}`, JSON.stringify(trimmed));
  }, [messages, sessionId]);

  const addMessage = (sender: 'user' | 'assistant', text: string, language?: string) => {
    const newMsg: ChatMessage = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 4)}`,
      sender,
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      language: language || selectedLanguage,
    };
    setMessages((prev) => [...prev, newMsg]);
  };

  const clearHistory = () => {
    setMessages([
      {
        id: `msg_welcome_${Date.now()}`,
        sender: 'assistant',
        text: 'Namaste! Session reset. How may I help you?',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        language: selectedLanguage
      }
    ]);
  };

  return (
    <ConversationContext.Provider
      value={{
        sessionId,
        messages,
        addMessage,
        clearHistory,
        selectedLanguage,
        setSelectedLanguage,
        isStreaming,
        setIsStreaming,
      }}
    >
      {children}
    </ConversationContext.Provider>
  );
};

export const useConversation = () => {
  const context = useContext(ConversationContext);
  if (!context) throw new Error('useConversation must be used within ConversationProvider');
  return context;
};
