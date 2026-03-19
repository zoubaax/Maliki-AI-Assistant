import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Building, 
  Bot, 
  Scroll, 
  Cpu, 
  Quote, 
  Sparkles, 
  BookOpen, 
  CheckCircle, 
  PenLine, 
  Send, 
  Gavel, 
  UserCircle,
  Loader2,
  Layers,
  List
} from 'lucide-react';

const App = () => {
  const [messages, setMessages] = useState([
    {
      role: 'bot',
      id: 'welcome',
      text: 'السلام عليكم ورحمة الله وبركاته. مساعد شرعي متخصص في **الفقه المالكي**. استخرج الأحكام من أمهات الكتب: "مختصر الأخضري"، "الرسالة"، "المدونة".',
      sources: []
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      id: Date.now().toString(),
      text: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post('/ask', { question: input });
      const botMessage = {
        role: 'bot',
        id: (Date.now() + 1).toString(),
        text: response.data.answer,
        sources: response.data.sources || [],
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          id: (Date.now() + 1).toString(),
          text: '⚠️ عذرًا، حدث خطأ في الاتصال بالمكتبة المالكية. يرجى المحاولة لاحقًا.',
          sources: [],
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container" dir="rtl">
      {/* Header */}
      <header className="app-header">
        <div className="header-logo-container">
          <div className="logo-icon-box">
             <Building className="text-gold-primary" size={28} />
          </div>
          <div className="header-title-box">
            <h1>
              <Bot className="text-gold-muted" size={20} />
              المساعد المالكي
            </h1>
            <p className="header-subtitle">
              <Scroll className="text-gold-dim" size={14} />
              Maliki AI Assistant · pure css
            </p>
          </div>
        </div>

        <div className="tech-badge">
          <Cpu className="text-gold-muted" size={18} />
          <span>Gemini 2.5 Flash · React</span>
        </div>
      </header>

      {/* Main Chat area */}
      <main ref={scrollRef} className="chat-main">
        <AnimatePresence mode="popLayout">
          {messages.map((msg) => (
            <motion.div
              layout
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              key={msg.id}
              className={`message-row ${msg.role === 'user' ? 'message-user' : ''}`}
            >
              {msg.role === 'bot' && (
                <div className="avatar-box">
                   <Gavel className="text-gold-primary" size={20} />
                </div>
              )}

              <div className="message-content-wrapper">
                <span className="message-label">
                  {msg.role === 'user' ? <UserCircle size={12} /> : <Bot size={12} />}
                  {msg.role === 'user' ? 'سؤالك' : 'الجواب المالكي'}
                </span>

                <div className={`message-bubble ${msg.role === 'user' ? 'user-bubble' : 'ai-card'}`}>
                  {msg.id === 'welcome' && (
                    <Quote className="quote-icon" size={40} style={{ opacity: 0.1, float: 'left', margin: '-5px 0 0 -5px' }} />
                  )}
                  {msg.id === 'welcome' && (
                     <p style={{ fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                       <Sparkles className="text-gold-primary" size={20} /> 
                       السلام عليكم ورحمة الله وبركاته
                     </p>
                  )}
                  <div className="markdown-body">
                    <ReactMarkdown>{msg.text}</ReactMarkdown>
                  </div>
                  
                  {msg.sources && msg.sources.length > 0 && (
                    <motion.div 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.3 }}
                      className="sources-container"
                    >
                      <p className="sources-label">
                        <List size={12} /> المصادر المرجعية:
                      </p>
                      <div className="source-chips">
                        {msg.sources.map((source, i) => (
                           <div key={i} className="source-chip">
                              <BookOpen size={12} className="text-gold-muted" />
                              {source.book || 'مخطوطة'} (ص {source.page || '--'})
                              {source.volume && (
                                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                  <Layers size={12} className="text-gold-dim" /> ج{source.volume}
                                </span>
                              )}
                           </div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </div>
              </div>

              {msg.role === 'user' && (
                <div className="avatar-box">
                   <UserCircle className="text-gold-muted" size={24} />
                </div>
              )}
            </motion.div>
          ))}
          
          {isLoading && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="message-row"
            >
              <div className="avatar-box">
                <Bot className="text-gold-muted animate-pulse" size={20} />
              </div>
              <div className="loading-indicator">
                <Loader2 className="animate-spin" size={20} />
                <span>البحث في المتون المالكية...</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Input section */}
      <footer className="app-footer">
        <form onSubmit={handleSendMessage} className="input-form">
          <div className="input-icon">
            <PenLine size={24} />
          </div>
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="اكتب مسألتك الفقهية ... (مثال: ما هي نواقض الوضوء عند المالكية؟)" 
            className="chat-input"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            disabled={!input.trim() || isLoading}
            className={`send-button ${input.trim() && !isLoading ? 'active' : 'disabled'}`}
          >
            <Send size={24} />
          </button>
          
          <div className="input-hint">
            <CheckCircle size={12} /> اسأل عن أي مسألة فقهية مالكية موثقة
          </div>
        </form>
      </footer>
    </div>
  );
};

export default App;
