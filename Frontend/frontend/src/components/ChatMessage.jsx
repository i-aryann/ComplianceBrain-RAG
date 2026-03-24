import { motion } from 'framer-motion';
import { Lightning, User } from '@phosphor-icons/react';

export const ChatMessage = ({ message, isStreaming = false }) => {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
      data-testid={`chat-message-${message.id}`}
    >
      <div className={`flex gap-3 max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div 
          className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
            isUser 
              ? 'bg-[#09090B] text-white' 
              : 'bg-[#002FA7] text-white'
          }`}
        >
          {isUser ? (
            <User size={18} weight="bold" />
          ) : (
            <Lightning size={18} weight="fill" />
          )}
        </div>

        {/* Message bubble */}
        <div className={isUser ? 'chat-bubble-user' : 'chat-bubble-ai'}>
          {!isUser && (
            <div className="label-text text-[#002FA7] mb-2 flex items-center gap-2">
              <Lightning size={12} weight="fill" />
              Intelligence Report
            </div>
          )}
          <div className={`text-sm leading-relaxed ${isStreaming ? 'streaming-cursor' : ''}`}>
            {message.content}
          </div>
          {message.timestamp && (
            <div className={`text-xs mt-2 ${isUser ? 'text-white/60' : 'text-[#52525B]'}`}>
              {new Date(message.timestamp).toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};
