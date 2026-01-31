import { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, ArrowLeft, Loader2, MessageSquare } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000',
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export default function Chatbot() {
    const navigate = useNavigate();
    const [messages, setMessages] = useState([
        { role: 'bot', text: 'Hello! I am your AI Nutrition & Health Assistant. How can I help you today?' }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!inputValue.trim() || loading) return;

        const userMsg = inputValue;
        setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
        setInputValue('');
        setLoading(true);

        try {
            const response = await api.post('/chat/', { message: userMsg });
            setMessages(prev => [...prev, { role: 'bot', text: response.data.reply }]);
        } catch (error) {
            console.error('Chat failed:', error);
            setMessages(prev => [...prev, { role: 'bot', text: 'Sorry, I am having trouble connecting right now. Please try again later.' }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col animate-fade-in">
            {/* Header */}
            <div className="bg-white shadow-sm p-4 flex items-center justify-between sticky top-0 z-10 animate-slide-up">
                <div className="flex items-center gap-3">
                    <button onClick={() => navigate('/recommendations')} className="p-2 hover:bg-gray-100 rounded-full transition">
                        <ArrowLeft className="w-5 h-5 text-gray-600" />
                    </button>
                    <div className="flex items-center gap-2">
                        <div className="bg-blue-600 p-2 rounded-lg animate-pop">
                            <MessageSquare className="text-white w-5 h-5" />
                        </div>
                        <h1 className="text-xl font-bold text-gray-800">Health Assistant</h1>
                    </div>
                </div>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 max-w-4xl mx-auto w-full">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-slide-up`} style={{ animationDelay: idx === 0 ? '300ms' : '0ms' }}>
                        <div className={`flex gap-3 max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 animate-pop ${msg.role === 'user' ? 'bg-indigo-600' : 'bg-blue-100'}`}>
                                {msg.role === 'user' ? <User className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-blue-600" />}
                            </div>
                            <div className={`p-4 rounded-2xl shadow-sm ${msg.role === 'user' ? 'bg-indigo-600 text-white rounded-tr-none' : 'bg-white text-gray-800 rounded-tl-none border border-gray-100'}`}>
                                {msg.text}
                            </div>
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex justify-start animate-fade-in">
                        <div className="flex gap-3 max-w-[80%]">
                            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center animate-pop">
                                <Bot className="w-5 h-5 text-blue-600" />
                            </div>
                            <div className="p-4 bg-white rounded-2xl rounded-tl-none border border-gray-100 flex items-center gap-2">
                                <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                                <span className="text-gray-400 italic">Thinking...</span>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="bg-white border-t p-4 pb-8 sticky bottom-0 animate-slide-up" style={{ animationDelay: '500ms' }}>
                <form onSubmit={handleSend} className="max-w-4xl mx-auto flex gap-2">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        placeholder="Ask about diet, exercise, or health..."
                        className="flex-1 p-4 bg-gray-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition shadow-inner"
                    />
                    <button
                        type="submit"
                        disabled={!inputValue.trim() || loading}
                        className="bg-blue-600 text-white p-4 rounded-xl hover:bg-blue-700 disabled:opacity-50 transition shadow-lg"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </form>
            </div>
        </div>
    );
}
