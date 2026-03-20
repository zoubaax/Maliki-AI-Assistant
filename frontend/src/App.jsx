import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send,
  Bot,
  User,
  Sparkles,
  Gavel,
  Landmark,
  Scroll,
  BookOpen,
  List,
  Loader2,
  Cpu,
  PenLine,
} from 'lucide-react';

const App = () => {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        'السلام عليكم ورحمة الله وبركاته. أنا **المساعد المالكي**، خادمكم في استخراج الأحكام الفقهية الموثقة من أمهات الكتب. ما هي المسألة التي تشغل بالكم اليوم؟',
      sources: [],
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  const scrollRef = useRef(null);
  const textareaRef = useRef(null);

  /* ── Auto-scroll ── */
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  /* ── Auto-focus on mount ── */
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  /* ── Auto-grow textarea ── */
  const handleInputChange = (e) => {
    setInput(e.target.value);
    const el = e.target;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 128)}px`;
  };

  /* ── Reset textarea height after send ── */
  const resetTextarea = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  /* ── Send message ── */
  const sendMessage = useCallback(
    async (text) => {
      const userMessage = text.trim();
      if (!userMessage || isLoading) return;

      setInput('');
      resetTextarea();

      setMessages((prev) => [
        ...prev,
        { id: Date.now().toString(), role: 'user', content: userMessage },
      ]);
      setIsLoading(true);
      setIsTyping(true);

      try {
        const apiBase = import.meta.env.VITE_API_BASE_URL || '';
        const response = await axios.post(`${apiBase}/ask`, {
          question: userMessage,
        });
        await new Promise((resolve) => setTimeout(resolve, 600));

        setMessages((prev) => [
          ...prev,
          {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: response.data.answer,
            sources: response.data.sources || [],
          },
        ]);
      } catch (error) {
        console.error('Chat Error:', error);
        setMessages((prev) => [
          ...prev,
          {
            id: `error-${Date.now()}`,
            role: 'assistant',
            content:
              '⚠️ عذرًا، حدث خطأ في الاتصال بالمكتبة المالكية. يرجى المحاولة لاحقًا.',
            sources: [],
          },
        ]);
      } finally {
        setIsLoading(false);
        setIsTyping(false);
      }
    },
    [isLoading]
  );

  /* ── Form submit ── */
  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  /* ── Enter key to send (Shift+Enter for newline) ── */
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  const quickQuestions = [
    { text: 'نواقض الوضوء عند المالكية؟', icon: <Sparkles size={14} /> },
    { text: 'حكم الجمع في السفر؟',        icon: <Scroll size={14} /> },
    { text: 'أركان الصلاة وشروطها؟',      icon: <Gavel size={14} /> },
    { text: 'كيفية صلاة الجنازة؟',        icon: <BookOpen size={14} /> },
  ];

  return (
    <div className="app-viewport">

      {/* ── Header ── */}
      <header className="app-header-v2">
        <div className="header-info-v2">
          <div className="header-icon-box-v2">
            <Landmark size={18} />
          </div>
          <div className="header-text-v2">
            <h1>المساعد المالكي</h1>
            <div className="header-status-v2">
              <span className="status-dot-v2" />
              <span>واجهة الفقيه · متصل</span>
            </div>
          </div>
        </div>

        <div className="header-badge">
          <Cpu size={14} />
        </div>
      </header>

      {/* ── Chat Area ── */}
      <main ref={scrollRef} className="chat-main-v2 scrollbar-v2">
        <div className="chat-center-container">

          <AnimatePresence mode="popLayout">
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                layout
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25 }}
                className={`message-row-v2 ${msg.role === 'user' ? 'row-user' : ''}`}
              >
                {/* Avatar */}
                <div className={`avatar-v2 ${msg.role === 'user' ? 'avatar-user-v2' : 'avatar-bot-v2'}`}>
                  {msg.role === 'user' ? <User size={14} /> : <Bot size={14} />}
                </div>

                {/* Bubble */}
                <div className="message-box-v2">
                  <div className={`bubble-v2 ${msg.role === 'user' ? 'user-bubble-v2' : 'bot-bubble-v2'}`}>

                    {/* Welcome Heading */}
                    {msg.id === 'welcome' && (
                      <span className="welcome-title">المكتبة المالكية الذكية</span>
                    )}

                    <div className="markdown-body">
                      <ReactMarkdown rehypePlugins={[rehypeRaw]}>
                        {msg.content}
                      </ReactMarkdown>
                    </div>

                    {/* Sources */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="sources-v2">
                        <p className="source-label-v2">
                          <List size={10} />
                          التوثيق المرجعي:
                        </p>
                        <div className="source-chips-v2">
                          {msg.sources.map((src, i) => (
                            <div key={i} className="chip-v2">
                              {src.book} (ص {src.page})
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}

            {/* Typing indicator */}
            {isTyping && (
              <motion.div
                key="typing"
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="message-row-v2"
              >
                <div className="avatar-v2 avatar-bot-v2">
                  <Bot size={14} />
                </div>
                <div className="bubble-v2 bot-bubble-v2">
                  <div className="typing-dots">
                    <div className="dot" />
                    <div className="dot" />
                    <div className="dot" />
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Quick Questions — shown only on welcome state */}
          {messages.length === 1 && (
            <div className="hero-v2">
              <h2>مجلس فقهي مالكي موثق</h2>
              <div className="questions-grid-v2">
                {quickQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => sendMessage(q.text)}
                    className="q-btn-v2"
                  >
                    <span className="q-icon">{q.icon}</span>
                    <span>{q.text}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

        </div>
      </main>

      {/* ── Footer / Input ── */}
      <footer className="app-footer-v2">
        <form onSubmit={handleSubmit} className="input-wrapper-v2">
          {/* Right icon */}
          <div className="input-icon-v2">
            <PenLine size={17} />
          </div>

          {/* Auto-grow textarea */}
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="اسأل عن مسألة فقهية ..."
            className="input-field-v2"
            rows={1}
            dir="rtl"
            autoComplete="off"
          />

          {/* Send button */}
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="send-action-v2"
            aria-label="إرسال"
          >
            {isLoading
              ? <Loader2 size={16} className="animate-spin" />
              : <Send size={16} />
            }
          </button>
        </form>

        <p className="footer-tip">
          مجلس علم رقمي مستخرج من المتون المعتمدة
        </p>
      </footer>

    </div>
  );
};

export default App;
