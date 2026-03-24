import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Plus, 
  MagnifyingGlass, 
  ClockCounterClockwise,
  FileText,
  CaretRight,
  X
} from '@phosphor-icons/react';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { UploadDropzone } from './UploadDropzone';

export const Sidebar = ({ 
  chatHistory = [], 
  currentChatId, 
  onNewChat, 
  onSelectChat,
  onUpload,
  isOpen,
  onClose
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredHistory = chatHistory.filter(chat => 
    chat.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/20 z-40 md:hidden"
          onClick={onClose}
        />
      )}
      
      <aside 
        className={`sidebar ${isOpen ? 'open' : ''}`}
        data-testid="sidebar"
      >
        {/* Header with logo */}
        <div className="sidebar-header">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-[#002FA7] flex items-center justify-center">
                <FileText size={22} weight="bold" className="text-white" />
              </div>
              <div>
                <h1 className="font-bold text-lg tracking-tight">Compliance RAG</h1>
                <span className="label-text">V2.4 Intelligence</span>
              </div>
            </div>
            <button 
              className="md:hidden p-2 hover:bg-black/5 rounded-lg"
              onClick={onClose}
              data-testid="close-sidebar-btn"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* New Chat Button */}
        <div className="p-4">
          <motion.button
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            className="new-chat-btn rounded-lg"
            onClick={onNewChat}
            data-testid="new-chat-btn"
          >
            <Plus size={20} weight="bold" />
            New Chat
          </motion.button>
        </div>

        {/* Search */}
        <div className="px-4 pb-4">
          <div className="relative">
            <MagnifyingGlass 
              size={18} 
              className="absolute left-3 top-1/2 -translate-y-1/2 text-[#52525B]" 
            />
            <Input
              type="text"
              placeholder="Search compliance archives..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 bg-white border-black/10 focus:border-[#002FA7] focus:ring-[#002FA7]"
              data-testid="search-input"
            />
          </div>
        </div>

        {/* Chat History */}
        <div className="flex-1 overflow-hidden">
          <div className="px-4 pb-2">
            <span className="label-text flex items-center gap-2">
              <ClockCounterClockwise size={14} />
              Compliance History
            </span>
          </div>
          <ScrollArea className="h-[calc(100%-2rem)] px-4">
            <div className="space-y-1 pb-4">
              {filteredHistory.length === 0 ? (
                <p className="text-sm text-[#52525B] py-4 text-center">
                  No conversations yet
                </p>
              ) : (
                filteredHistory.map((chat) => (
                  <motion.button
                    key={chat.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={`sidebar-link ${currentChatId === chat.id ? 'active' : ''}`}
                    onClick={() => onSelectChat(chat.id)}
                    data-testid={`chat-history-item-${chat.id}`}
                  >
                    <CaretRight size={14} className="flex-shrink-0" />
                    <span className="truncate">{chat.title}</span>
                  </motion.button>
                ))
              )}
            </div>
          </ScrollArea>
        </div>

        {/* Upload Section */}
        <div className="sidebar-footer">
          <UploadDropzone onUpload={onUpload} />
        </div>
      </aside>
    </>
  );
};
