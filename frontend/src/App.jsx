import React, { useState, useEffect, useRef } from 'react';
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
  Layers,
  List,
  Loader2,
  Cpu,
  PenLine,
  ChevronLeft
} from 'lucide-react';

const App = () => {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: "السلام عليكم ورحمة الله وبركاته. أنا **المساعد المالكي**، خادمكم في استخراج الأحكام الفقهية الموثقة من أمهات الكتب. ما هي المسألة التي تشغل بالكم اليوم؟",
      sources: []
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSend = async (e, directMessage = null) => {
    if (e && e.preventDefault) e.preventDefault();

    const messageToSend = directMessage || input;
    if (!messageToSend.trim() || isLoading) return;

    const userMessage = messageToSend.trim();
    if (!directMessage) setInput('');
    
    setMessages(prev => [...prev, { id: Date.now().toString(), role: 'user', content: userMessage }]);
    setIsLoading(true);
    setIsTyping(true);

    try {
      const response = await axios.post('/ask', { question: userMessage });
      await new Promise(resolve => setTimeout(resolve, 600));

      setMessages(prev => [...prev, { 
        id: (Date.now() + 1).toString(),
        role: 'assistant', 
        content: response.data.answer,
        sources: response.data.sources || []
      }]);
    } catch (error) {
      console.error('Chat Error:', error);
      setMessages(prev => [...prev, {
        id: 'error',
        role: 'assistant',
        content: "⚠️ عذرًا، حدث خطأ في الاتصال بالمكتبة المالكية. يرجى المحاولة لاحقًا.",
        sources: []
      }]);
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  const handleQuickQuestion = (question) => {
    handleSend(null, question);
  };

  const quickQuestions = [
    { text: "نواقض الوضوء عند المالكية؟", icon: <Sparkles size={16} /> },
    { text: "حكم الجمع في السفر؟", icon: <Scroll size={16} /> },
    { text: "أركان الصلاة وشروطها؟", icon: <Gavel size={16} /> },
    { text: "كيفية صلاة الجنازة؟", icon: <BookOpen size={16} /> }
  ];

  return (
    <div className="app-viewport">
      {/* Header (Simplified) */}
      <header className="app-header-v2">
        <div className="header-info-v2">
          <div className="header-icon-box-v2">
            <Landmark size={20} className="text-gold-primary" />
          </div>
          <div className="header-text-v2 text-right">
            <h1>المساعد المالكي</h1>
            <div className="header-status-v2">
              <span className="status-dot-v2"></span>
              <span>واجهة الفقيه · متصل</span>
            </div>
          </div>
        </div>

        {/* Removed Tech Badge as requested */}
        <div style={{ opacity: 0.5, fontSize: '0.7rem' }}>
           <Cpu size={14} />
        </div>
      </header>

      {/* Main Chat Area */}
      <main ref={scrollRef} className="chat-main-v2 scrollbar-v2">
        <div className="chat-center-container">
          <AnimatePresence mode="popLayout">
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                layout
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`message-row-v2 ${msg.role === 'user' ? 'row-user' : ''}`}
              >
                <div className={`avatar-v2 ${msg.role === 'user' ? 'avatar-user-v2' : 'avatar-bot-v2'}`}>
                  {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                </div>
                
                <div className={`message-box-v2`}>
                  <div className={`bubble-v2 ${msg.role === 'user' ? 'user-bubble-v2' : 'bot-bubble-v2'}`}>
                    {msg.id === 'welcome' && (
                       <p style={{ fontSize: '1.1rem', marginBottom: '1rem', color: 'var(--gold-primary)', fontWeight: 'bold' }}>
                         المكتبة المالكية الذكية
                       </p>
                    )}
                    <div className="markdown-body" style={{ fontSize: '0.9rem' }}>
                      <ReactMarkdown rehypePlugins={[rehypeRaw]}>{msg.content}</ReactMarkdown>
                    </div>

                    {msg.sources && msg.sources.length > 0 && (
                      <div className="sources-v2">
                        <p className="source-label-v2"><List size={10} /> التوثيق المرجعي:</p>
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

            {isTyping && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="message-row-v2">
                <div className="avatar-v2 avatar-bot-v2">
                  <Bot size={16} />
                </div>
                <div className="bubble-v2 bot-bubble-v2">
                  <div className="typing-dots">
                    <div className="dot"></div>
                    <div className="dot"></div>
                    <div className="dot"></div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {messages.length === 1 && (
            <div className="hero-v2">
              <h2>مجلس فقهي مالكي موثق</h2>
              <div className="questions-grid-v2">
                {quickQuestions.map((q, i) => (
                  <button key={i} onClick={() => handleQuickQuestion(q.text)} className="q-btn-v2">
                    <span style={{ opacity: 0.6 }}>{q.icon}</span>
                    <span>{q.text}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Input Form */}
      <footer className="app-footer-v2">
        <form onSubmit={handleSend} className="input-wrapper-v2">
          <div className="input-icon-v2">
            <PenLine size={20} />
          </div>
          <input 
            ref={inputRef}
            type="text" 
            value={input} 
            onChange={(e) => setInput(e.target.value)}
            placeholder="اسأل عن مسألة فقهية ..." 
            className="input-field-v2"
          />
          <button type="submit" disabled={!input.trim() || isLoading} className="send-action-v2">
            {isLoading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
          </button>
        </form>
        <div style={{ textAlign: 'center', marginTop: '1rem', fontSize: '0.65rem', color: 'rgba(212, 175, 55, 0.4)' }}>
           مجلس علم رقمي مستخرج من المتون المعتمدة
        </div>
      </footer>
    </div>
  );
};

export default App;
