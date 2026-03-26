import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Sparkle, Lightning, Bell, Question } from '@phosphor-icons/react';
import { ScrollArea } from './ui/scroll-area';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';

export const ChatArea = ({ 
  messages = [], 
  onSendMessage, 
  isLoading = false,
  streamingMessageId = null,
  onAttachFile
}) => {
  const scrollRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const EmptyState = () => (
    <div className="empty-state h-full">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-2xl"
      >
        <h2 className="font-bold text-3xl md:text-4xl tracking-tight mb-4">
          Verify policy compliance with{' '}
          <span className="text-[#002FA7]">Precision Intelligence.</span>
        </h2>
        <p className="text-[#52525B] text-base md:text-lg mb-8">
          Upload your documents and let our RAG engine cross-reference against global regulatory standards in real-time.
        </p>

        {/* Pro tip card */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3, duration: 0.4 }}
          className="pro-tip-card text-left inline-block"
        >
          <div className="flex items-center gap-2 mb-2">
            <Sparkle size={16} weight="fill" className="text-[#002FA7]" />
            <span className="font-semibold text-sm">Pro Tip</span>
          </div>
          <p className="text-sm text-[#52525B]">
            Ask about "GDPR Article 17 implications on user data deletion in legacy systems."
          </p>
        </motion.div>
      </motion.div>
    </div>
  );

  return (
    <main className="main-content" data-testid="chat-area">
      {/* Header */}
      <header className="h-16 border-b border-black/5 flex items-center justify-between px-6 flex-shrink-0 bg-white/50 backdrop-blur-sm">
        <div className="flex items-center gap-4">
          <span className="label-text">Compliance Assistant</span>
        </div>
        <div className="flex items-center gap-3">
          <button 
            className="p-2 hover:bg-black/5 rounded-lg transition-colors"
            data-testid="notifications-btn"
          >
            <Bell size={20} className="text-[#52525B]" />
          </button>
          <button 
            className="p-2 hover:bg-black/5 rounded-lg transition-colors"
            data-testid="help-btn"
          >
            <Question size={20} className="text-[#52525B]" />
          </button>
          <div className="flex items-center gap-2 pl-3 border-l border-black/10">
            <span className="text-sm font-medium">By Aryan Gupta</span>
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#002FA7] to-[#00227A] flex items-center justify-center text-white text-xs font-bold">
              AG
            </div>
          </div>
        </div>
      </header>

      {/* Chat messages area */}
      <ScrollArea className="flex-1" ref={scrollRef}>
        <div className="chat-area">
          {messages.length === 0 ? (
            <EmptyState />
          ) : (
            <div className="space-y-6 max-w-4xl mx-auto">
              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                  isStreaming={message.id === streamingMessageId}
                />
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input area */}
      <div className="input-container">
        <div className="max-w-4xl mx-auto">
          <ChatInput 
            onSendMessage={onSendMessage} 
            isLoading={isLoading}
            onAttachFile={onAttachFile}
          />
          

        </div>
      </div>
    </main>
  );
};
