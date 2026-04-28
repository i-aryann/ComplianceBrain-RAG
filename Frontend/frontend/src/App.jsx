import { useState, useCallback, useRef, useEffect } from 'react';
import '@/App.css';
import { Toaster, toast } from 'sonner';
import { List } from '@phosphor-icons/react';
import { Sidebar } from './components/Sidebar';
import { ChatArea } from './components/ChatArea';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || '/api';
const API = `${BACKEND_URL}/api`;

// Generate unique IDs
const generateId = () => Math.random().toString(36).substring(2) + Date.now().toString(36);

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [chatHistory, setChatHistory] = useState(() => {
    const saved = localStorage.getItem('compliance_chat_history');
    return saved ? JSON.parse(saved) : [];
  });
  const [currentChatId, setCurrentChatId] = useState(() => {
    const saved = localStorage.getItem('compliance_current_chat_id');
    return saved ? JSON.parse(saved) : null;
  });
  const [messages, setMessages] = useState(() => {
    const savedId = localStorage.getItem('compliance_current_chat_id');
    const parsedId = savedId ? JSON.parse(savedId) : null;
    if (parsedId) {
      const savedMessages = localStorage.getItem(`compliance_messages_${parsedId}`);
      return savedMessages ? JSON.parse(savedMessages) : [];
    }
    return [];
  });

  // Save chat history
  useEffect(() => {
    localStorage.setItem('compliance_chat_history', JSON.stringify(chatHistory));
  }, [chatHistory]);

  // Save current chat ID
  useEffect(() => {
    localStorage.setItem('compliance_current_chat_id', JSON.stringify(currentChatId));
  }, [currentChatId]);

  // Save messages for current chat
  useEffect(() => {
    if (currentChatId) {
      localStorage.setItem(`compliance_messages_${currentChatId}`, JSON.stringify(messages));
    }
  }, [messages, currentChatId]);
  const [isLoading, setIsLoading] = useState(false);
  const [streamingMessageId, setStreamingMessageId] = useState(null);
  const abortControllerRef = useRef(null);

  // Create a new chat
  const handleNewChat = useCallback(() => {
    const newChatId = generateId();
    const newChat = {
      id: newChatId,
      title: 'New Compliance Query',
      createdAt: new Date().toISOString(),
    };
    setChatHistory(prev => [newChat, ...prev]);
    setCurrentChatId(newChatId);
    setMessages([]);
    setSidebarOpen(false);
  }, []);

  // Select a chat from history
  const handleSelectChat = useCallback((chatId) => {
    setCurrentChatId(chatId);
    // Load messages from local storage
    const savedMessages = localStorage.getItem(`compliance_messages_${chatId}`);
    setMessages(savedMessages ? JSON.parse(savedMessages) : []);
    setSidebarOpen(false);
  }, []);

  // Handle file upload
  const handleUpload = useCallback((files) => {
    toast.success(`${files.length} file(s) uploaded successfully`, {
      description: 'Documents are being processed for RAG indexing.',
    });
  }, []);

  // Handle attach file from chat input
  const handleAttachFile = useCallback(() => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.pdf,.txt,.doc,.docx';
    input.multiple = true;
    input.onchange = (e) => {
      const files = Array.from(e.target.files);
      if (files.length > 0) {
        handleUpload(files);
      }
    };
    input.click();
  }, [handleUpload]);

  // Simulate streaming response (replace with actual API call)
  const simulateStreamingResponse = async (userMessage, aiMessageId) => {
    // This is a mock streaming response - replace with your actual backend call
    const mockResponses = [
      `Based on your query about "${userMessage.substring(0, 50)}...", I've analyzed the relevant compliance documentation.\n\n`,
      "According to the **FinCEN Beneficial Ownership Information (BOI) Reporting Requirements** updated for 2024, ",
      "your Q3 internal audit must address three critical vectors:\n\n",
      "**01.** Identification of all \"Reporting Companies\" within the subsidiary structure that meet the gross receipts threshold.\n\n",
      "**02.** Verification of beneficial owner information accuracy and completeness against current records.\n\n",
      "**03.** Assessment of exemption eligibility for each entity classification.\n\n",
      "I recommend reviewing sections 31 CFR 1010.380 for detailed compliance guidelines."
    ];

    let fullResponse = '';

    for (const chunk of mockResponses) {
      if (abortControllerRef.current?.signal.aborted) {
        break;
      }
      
      await new Promise(resolve => setTimeout(resolve, 100 + Math.random() * 200));
      fullResponse += chunk;
      
      setMessages(prev => prev.map(msg => 
        msg.id === aiMessageId 
          ? { ...msg, content: fullResponse }
          : msg
      ));
    }

    return fullResponse;
  };

  // Send message with streaming support
  const handleSendMessage = useCallback(async (content) => {
    if (!content.trim() || isLoading) return;

    // Create a new chat if none exists
    if (!currentChatId) {
      const newChatId = generateId();
      const newChat = {
        id: newChatId,
        title: content.substring(0, 50) + (content.length > 50 ? '...' : ''),
        createdAt: new Date().toISOString(),
      };
      setChatHistory(prev => [newChat, ...prev]);
      setCurrentChatId(newChatId);
    } else {
      // Update chat title if it's a new chat
      setChatHistory(prev => prev.map(chat => 
        chat.id === currentChatId && chat.title === 'New Compliance Query'
          ? { ...chat, title: content.substring(0, 50) + (content.length > 50 ? '...' : '') }
          : chat
      ));
    }

    // Add user message
    const userMessage = {
      id: generateId(),
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Create placeholder for AI response
    const aiMessageId = generateId();
    const aiMessage = {
      id: aiMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, aiMessage]);
    setStreamingMessageId(aiMessageId);

    // Create abort controller for cancellation
    abortControllerRef.current = new AbortController();

    try {
      // Replace this with your actual streaming API call
      // Example for real implementation:
      /*
      const response = await fetch(`${API}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: content, chatId: currentChatId }),
        signal: abortControllerRef.current.signal,
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        fullResponse += chunk;
        
        setMessages(prev => prev.map(msg => 
          msg.id === aiMessageId 
            ? { ...msg, content: fullResponse }
            : msg
        ));
      }
      */

      // Using mock streaming for demo
    const response = await fetch(`${BACKEND_URL}/ask-stream`, {
    method: "POST",
    headers: {
    "Content-Type": "application/json"
    },
    body: JSON.stringify({
    question: content
    }),
    signal: abortControllerRef.current.signal
    });

    if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    const SENTINEL = "\n__SOURCES__:";

    let buffer  = "";
    let sources = [];

    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        // Stream ended — check for sentinel in whatever is buffered
        const si = buffer.indexOf(SENTINEL);
        if (si !== -1) {
          const answerPart  = buffer.substring(0, si);
          const sourcesPart = buffer.substring(si + SENTINEL.length);
          try { sources = JSON.parse(sourcesPart); } catch (_) { sources = []; }
          setMessages(prev => prev.map(msg =>
            msg.id === aiMessageId
              ? { ...msg, content: answerPart.trim(), sources }
              : msg
          ));
        } else if (buffer.trim()) {
          // No sentinel but we have text — show it anyway
          setMessages(prev => prev.map(msg =>
            msg.id === aiMessageId ? { ...msg, content: buffer.trim() } : msg
          ));
        }
        break;
      }

      // Append incoming chunk to buffer
      buffer += decoder.decode(value, { stream: true });

      // Check if the sentinel has arrived
      const si = buffer.indexOf(SENTINEL);
      if (si !== -1) {
        const answerPart  = buffer.substring(0, si);
        const sourcesPart = buffer.substring(si + SENTINEL.length);
        try { sources = JSON.parse(sourcesPart); } catch (_) { sources = []; }
        setMessages(prev => prev.map(msg =>
          msg.id === aiMessageId
            ? { ...msg, content: answerPart.trim(), sources }
            : msg
        ));
        break;
      }

      // No sentinel yet — show live text, masking any partial sentinel at the tail
      const safeText = buffer.replace(/\n__SOURCES__[\s\S]*$/, "");
      setMessages(prev => prev.map(msg =>
        msg.id === aiMessageId ? { ...msg, content: safeText } : msg
      ));
    }

    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('Error sending message:', error);
        toast.error(`Error: ${error.message || 'Unknown network error'}`, {
          description: 'Please capture a screenshot of this error message.',
        });
        // Remove failed AI message
        setMessages(prev => prev.filter(msg => msg.id !== aiMessageId));
      }
    } finally {
      setIsLoading(false);
      setStreamingMessageId(null);
      abortControllerRef.current = null;
    }
  }, [currentChatId, isLoading]);

  return (
    <div className="app-shell">
      <Toaster 
        position="top-right" 
        richColors 
        toastOptions={{
          className: 'font-sans',
        }}
      />
      
      {/* Mobile menu button */}
      <button
        className="fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-md border border-black/10 md:hidden"
        onClick={() => setSidebarOpen(true)}
        data-testid="mobile-menu-btn"
      >
        <List size={24} />
      </button>

      <Sidebar
        chatHistory={chatHistory}
        currentChatId={currentChatId}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onUpload={handleUpload}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <ChatArea
        messages={messages}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        streamingMessageId={streamingMessageId}
        onAttachFile={handleAttachFile}
      />
    </div>
  );
}

export default App;
