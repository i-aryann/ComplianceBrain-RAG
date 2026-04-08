import { motion } from 'framer-motion';
import { Lightning, User, BookOpen, FileText } from '@phosphor-icons/react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// ─── Citation Card ────────────────────────────────────────────────────────────
const CitationCard = ({ source, index }) => {
  const clause = source.clause && source.clause !== 'N/A' && source.clause !== 'UNKNOWN'
    ? `Clause ${source.clause}`
    : null;
  const page = source.page && source.page !== -1 && source.page !== 'N/A'
    ? `Page ${source.page}`
    : null;
  const label = [clause, page].filter(Boolean).join(' · ') || 'Reference';

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.25 }}
      className="citation-card"
    >
      <div className="flex items-start gap-2">
        <div className="citation-icon flex-shrink-0">
          <BookOpen size={13} weight="bold" />
        </div>
        <div className="min-w-0">
          {/* Regulation badge */}
          <span className="citation-badge">
            {source.regulation || 'Regulation'}
          </span>

          {/* File name */}
          <div className="citation-file flex items-center gap-1 mt-0.5">
            <FileText size={11} />
            <span className="truncate">{source.source_file || source.doc_id || 'Document'}</span>
          </div>

          {/* Clause + Page */}
          <div className="citation-meta">
            {label}
            {source.topic && source.topic !== 'GENERAL' && (
              <span className="citation-topic">· {source.topic}</span>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

// ─── ChatMessage ──────────────────────────────────────────────────────────────
export const ChatMessage = ({ message, isStreaming = false }) => {
  const isUser = message.role === 'user';

  let formattedContent = message.content || "";

  // Force inline bullet points onto new lines
  formattedContent = formattedContent.replace(/ ([-\*]) \*\*/g, '\n\n$1 **');

  // Clean up accidental bold tags around Citations if the LLM injected them
  formattedContent = formattedContent.replace(/\*\*Citations:\*\*/g, 'Citations:');

  // Force Citations block and its items to break into new lines correctly
  formattedContent = formattedContent.replace(/Citations:/g, '\n\n**Citations:**\n\n');
  formattedContent = formattedContent.replace(/\) - /g, ')\n- ');
  formattedContent = formattedContent.replace(/\*\*Citations:\*\*\n\n\s*- /g, '**Citations:**\n\n- ');

  // Structured source objects passed via message.sources
  const sources = Array.isArray(message.sources) ? message.sources : [];

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
          <div className={`text-sm leading-relaxed prose prose-sm max-w-none ${isUser ? 'prose-invert' : ''} ${isStreaming ? 'streaming-cursor' : ''}`}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {formattedContent}
            </ReactMarkdown>
          </div>

          {/* ── Structured citations ───────────────────────────────────── */}
          {!isUser && !isStreaming && sources.length > 0 && (
            <div className="citations-section">
              <div className="citations-header">
                <BookOpen size={13} weight="bold" />
                Sources
              </div>
              <div className="citations-grid">
                {sources.map((src, i) => (
                  <CitationCard key={src.doc_id || i} source={src} index={i} />
                ))}
              </div>
            </div>
          )}

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
