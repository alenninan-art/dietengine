import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Lock, Mail } from 'lucide-react';

export default function Register() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        const success = await register(email, password);
        if (success) {
            navigate('/dashboard');
        } else {
            setError('Registration failed. Email may be taken.');
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-100 animate-fade-in">
            <div className="px-8 py-6 mt-4 text-left bg-white shadow-lg rounded-xl w-full max-w-md animate-slide-up">
                <h3 className="text-2xl font-bold text-center text-gray-800 animate-pop">Create Account</h3>
                {error && <p className="text-red-500 text-sm my-2 text-center animate-fade-in">{error}</p>}
                <form onSubmit={handleSubmit}>
                    <div className="mt-4 animate-slide-up" style={{ animationDelay: '100ms' }}>
                        <label className="block text-gray-700 font-medium" htmlFor="email">Email</label>
                        <div className="relative mt-1">
                            <span className="absolute inset-y-0 left-0 flex items-center pl-3">
                                <Mail className="w-5 h-5 text-gray-400" />
                            </span>
                            <input
                                type="text"
                                placeholder="Email"
                                className="w-full px-4 py-3 pl-10 mt-2 border rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-600 transition-all duration-300"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>
                    </div>
                    <div className="mt-4 animate-slide-up" style={{ animationDelay: '200ms' }}>
                        <label className="block text-gray-700 font-medium">Password</label>
                        <div className="relative mt-1">
                            <span className="absolute inset-y-0 left-0 flex items-center pl-3">
                                <Lock className="w-5 h-5 text-gray-400" />
                            </span>
                            <input
                                type="password"
                                placeholder="Password"
                                className="w-full px-4 py-3 pl-10 mt-2 border rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-600 transition-all duration-300"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>
                    </div>
                    <div className="flex items-baseline justify-between animate-slide-up" style={{ animationDelay: '300ms' }}>
                        <button className="px-6 py-3 mt-4 text-white bg-green-600 rounded-lg hover:bg-green-700 w-full font-bold transition-all duration-300 shadow-md transform hover:-translate-y-1 active:scale-95">Sign Up</button>
                    </div>
                    <div className="mt-6 text-center animate-fade-in" style={{ animationDelay: '400ms' }}>
                        <a href="/login" className="text-sm text-blue-600 hover:underline">Already have an account? Login</a>
                    </div>
                </form>
            </div>
        </div>
    );
}
