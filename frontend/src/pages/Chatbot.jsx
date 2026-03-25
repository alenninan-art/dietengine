import { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, ArrowLeft, Loader2, MessageSquare, Sparkles, Trash2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api, { checkBackendHealth } from '../api';

export default function Chatbot() {
    console.log("Chatbot: Rendering started");
    const navigate = useNavigate();
    const [messages, setMessages] = useState([
        { role: 'bot', text: 'Hello! I am your AI Health Assistant. Ask me anything about your diet or exercise plans!' }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [loading, setLoading] = useState(false);
    const [isBackendOnline, setIsBackendOnline] = useState(true);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        console.log("Chatbot: Mounted");
        scrollToBottom();
        
        // Initial health check
        const checkStatus = async () => {
            const online = await checkBackendHealth();
            setIsBackendOnline(online);
        };
        checkStatus();
        
        // Periodic check every 30 seconds
        const interval = setInterval(checkStatus, 30000);
        return () => clearInterval(interval);
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!inputValue.trim() || loading) return;

        const userMsg = inputValue;
        setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
        setInputValue('');
        setLoading(true);

        try {
            const response = await api.post('/chat', { message: userMsg });
            setMessages(prev => [...prev, { role: 'bot', text: response.data.reply }]);
        } catch (error) {
            console.error('Chat failed:', error);
            let errorMessage = 'I encountered a small hiccup. Please try again.';
            
            if (error.message === 'Network Error') {
                errorMessage = 'I cannot reach the health assistant server. Please ensure the backend (FastAPI) is running on port 8000.';
            } else if (error.response?.data?.detail) {
                errorMessage = `I encountered a small hiccup: ${error.response.data.detail}. Please try again.`;
            } else if (error.message) {
                errorMessage = `I encountered a small hiccup: ${error.message}. Please try again.`;
            }
            
            setMessages(prev => [...prev, { role: 'bot', text: errorMessage }]);
        } finally {
            setLoading(false);
        }
    };

    const clearChat = () => {
        setMessages([{ role: 'bot', text: 'Chat cleared. How else can I help you?' }]);
    };

    // Safety fallback
    if (!messages) {
        console.error("Chatbot: State failure, messages is null");
        return <div style={{ color: 'red', padding: '20px' }}>Fatal Error: Component State Corrupted</div>;
    }

    return (
        <div className="relative flex flex-col h-screen bg-slate-50 overflow-hidden font-sans">
            {/* Background Blobs */}
            <div className="absolute top-0 -left-10 w-96 h-96 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
            <div className="absolute -bottom-10 -right-10 w-96 h-96 bg-indigo-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>

            {/* Header */}
            <header className="relative z-20 bg-white/80 backdrop-blur-md border-b border-gray-100 px-6 py-4 flex items-center justify-between shadow-sm">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => navigate('/recommendations')}
                        className="p-2 hover:bg-gray-100 rounded-xl transition-all active:scale-90"
                    >
                        <ArrowLeft className="w-5 h-5 text-gray-600" />
                    </button>
                    <div className="flex items-center gap-3">
                        <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-2.5 rounded-2xl shadow-lg shadow-blue-100 animate-pop">
                            <Sparkles className="text-white w-5 h-5" />
                        </div>
                        <div>
                            <h1 className="text-lg font-extrabold text-gray-900 leading-none">Health Assistant</h1>
                            <div className="flex items-center gap-1.5 mt-1">
                                <div className={`w-2 h-2 rounded-full ${isBackendOnline ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                                <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                                    {isBackendOnline ? 'AI Powered' : 'Server Offline'}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                <button
                    onClick={clearChat}
                    className="p-2.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-xl transition-all"
                    title="Clear Chat"
                >
                    <Trash2 className="w-5 h-5" />
                </button>
            </header>

            {/* Chat Messages */}
            <main className="relative z-10 flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
                <div className="max-w-4xl mx-auto space-y-6">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-slide-up group`}>
                            <div className={`flex gap-4 max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                                <div className={`w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-sm transition-transform group-hover:scale-110 ${msg.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-white border border-gray-200'}`}>
                                    {msg.role === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5 text-blue-600" />}
                                </div>
                                <div className={`relative px-5 py-4 rounded-2xl shadow-sm ${msg.role === 'user'
                                    ? 'bg-gradient-to-br from-indigo-600 to-blue-700 text-white rounded-tr-none'
                                    : 'bg-white text-gray-800 rounded-tl-none border border-gray-100'
                                    }`}>
                                    <p className="text-sm md:text-base leading-relaxed font-medium">
                                        {msg.text}
                                    </p>
                                    <span className={`text-[10px] mt-2 block opacity-50 font-bold uppercase tracking-tighter ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                                        {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}

                    {loading && (
                        <div className="flex justify-start animate-fade-in">
                            <div className="flex gap-4 max-w-[85%]">
                                <div className="w-10 h-10 rounded-2xl bg-white border border-gray-200 flex items-center justify-center animate-pop shadow-sm">
                                    <Bot className="w-5 h-5 text-blue-600 animate-bounce" />
                                </div>
                                <div className="px-5 py-4 bg-white/50 backdrop-blur-sm rounded-2xl rounded-tl-none border border-white/60 flex items-center gap-3 shadow-sm">
                                    <div className="flex gap-1">
                                        <div className="w-1.5 h-1.5 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                        <div className="w-1.5 h-1.5 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                        <div className="w-1.5 h-1.5 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                    </div>
                                    <span className="text-sm font-bold text-blue-600/70 uppercase tracking-widest text-xs">Assistant is thinking</span>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
            </main>

            {/* Input Area */}
            <footer className="relative z-20 bg-white/80 backdrop-blur-md border-t border-gray-100 p-6 pb-10">
                <form onSubmit={handleSend} className="max-w-4xl mx-auto relative">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        placeholder="Ask me anything..."
                        className="w-full pl-6 pr-16 py-4 bg-gray-50 border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all shadow-inner font-medium text-gray-800 placeholder:text-gray-400"
                    />
                    <button
                        type="submit"
                        disabled={!inputValue.trim() || loading}
                        className="absolute right-2 top-2 bottom-2 px-5 bg-gradient-to-br from-blue-600 to-indigo-700 text-white rounded-xl hover:shadow-lg hover:shadow-blue-200 disabled:opacity-50 disabled:shadow-none transition-all active:scale-90 flex items-center justify-center group"
                    >
                        <Send className="w-5 h-5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                    </button>
                </form>
                <div className="max-w-4xl mx-auto mt-3 px-2 flex gap-4 overflow-x-auto pb-2 no-scrollbar">
                    {['Healthy snacks?', 'Best cardio?', 'Protein intake?'].map((suggestion) => (
                        <button
                            key={suggestion}
                            onClick={() => setInputValue(suggestion)}
                            className="text-xs font-bold text-gray-500 hover:text-blue-600 whitespace-nowrap bg-gray-100/50 hover:bg-blue-50 px-3 py-1.5 rounded-full border border-transparent hover:border-blue-100 transition-all"
                        >
                            {suggestion}
                        </button>
                    ))}
                </div>
            </footer>
        </div>
    );
}
