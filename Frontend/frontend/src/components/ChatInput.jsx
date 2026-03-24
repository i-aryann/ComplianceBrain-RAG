import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { PaperPlaneRight, Paperclip } from '@phosphor-icons/react';
import { Button } from './ui/button';

export const ChatInput = ({ onSendMessage, isLoading = false, onAttachFile }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  }, [message]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message.trim());
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="input-box" data-testid="chat-input-form">
      {/* Attach button */}
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="h-10 w-10 flex-shrink-0 text-[#52525B] hover:text-[#002FA7] hover:bg-[#002FA7]/5"
        onClick={onAttachFile}
        data-testid="attach-file-btn"
      >
        <Paperclip size={20} />
      </Button>

      {/* Text input */}
      <textarea
        ref={textareaRef}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your compliance inquiry..."
        className="flex-1 resize-none border-0 bg-transparent px-2 py-2.5 text-sm focus:outline-none focus:ring-0 placeholder:text-[#52525B]/60 max-h-[200px]"
        rows={1}
        disabled={isLoading}
        data-testid="chat-input"
      />

      {/* Send button */}
      <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
        <Button
          type="submit"
          size="icon"
          className="h-10 w-10 flex-shrink-0 bg-[#002FA7] hover:bg-[#00227A] rounded-lg"
          disabled={!message.trim() || isLoading}
          data-testid="send-message-btn"
        >
          <PaperPlaneRight size={20} weight="fill" />
        </Button>
      </motion.div>
    </form>
  );
};
