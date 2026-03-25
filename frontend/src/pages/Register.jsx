import { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, Mail, UserPlus, Loader2, Eye, EyeOff } from 'lucide-react';

export default function Register() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);
        try {
            const res = await register(email, password);
            if (res?.success) {
                navigate('/dashboard');
            } else {
                setError(res?.message || 'Registration failed. Email may be taken.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="relative flex items-center justify-center min-h-screen bg-slate-50 overflow-hidden">
            {/* Animated Background Blobs */}
            <div className="absolute top-0 -left-4 w-72 h-72 bg-green-400 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob"></div>
            <div className="absolute top-0 -right-4 w-72 h-72 bg-emerald-400 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-2000"></div>
            <div className="absolute -bottom-8 left-20 w-72 h-72 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-4000"></div>

            <div className="relative glass px-8 py-10 text-left bg-white/40 shadow-2xl rounded-2xl w-full max-w-md animate-slide-up z-10 border border-white/50">
                <div className="flex justify-center mb-6">
                    <div className="p-3 bg-green-600 rounded-2xl shadow-lg animate-pop">
                        <UserPlus className="w-8 h-8 text-white" />
                    </div>
                </div>

                <h3 className="text-3xl font-extrabold text-center text-gray-900 mb-2">Create Account</h3>
                <p className="text-center text-gray-600 mb-8">Join us and start your health journey today</p>

                {error && (
                    <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 animate-fade-in">
                        <p className="text-red-700 text-sm font-medium">{error}</p>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="animate-slide-up" style={{ animationDelay: '100ms' }}>
                        <label className="block text-sm font-semibold text-gray-700 mb-2" htmlFor="email">
                            Email Address
                        </label>
                        <div className="relative group">
                            <span className="absolute inset-y-0 left-0 flex items-center pl-3">
                                <Mail className="w-5 h-5 text-gray-400 group-focus-within:text-green-600 transition-colors" />
                            </span>
                            <input
                                id="email"
                                type="email"
                                placeholder="name@example.com"
                                className="w-full px-4 py-3 pl-10 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white/50 transition-all duration-300"
                                value={email}
                                onChange={(e) => {
                                    setEmail(e.target.value);
                                    if (error) setError('');
                                }}
                                required
                            />
                        </div>
                    </div>

                    <div className="animate-slide-up" style={{ animationDelay: '200ms' }}>
                        <label className="block text-sm font-semibold text-gray-700 mb-2" htmlFor="password">
                            Password
                        </label>
                        <div className="relative group">
                            <span className="absolute inset-y-0 left-0 flex items-center pl-3">
                                <Lock className="w-5 h-5 text-gray-400 group-focus-within:text-green-600 transition-colors" />
                            </span>
                            <input
                                id="password"
                                type={showPassword ? "text" : "password"}
                                placeholder="********"
                                className="w-full px-4 py-3 pl-10 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white/50 transition-all duration-300"
                                value={password}
                                onChange={(e) => {
                                    setPassword(e.target.value);
                                    if (error) setError('');
                                }}
                                required
                            />
                            <button
                                type="button"
                                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-green-600 transition-colors"
                                onClick={() => setShowPassword(!showPassword)}
                            >
                                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                            </button>
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="group relative flex justify-center py-3.5 px-4 border border-transparent text-sm font-bold rounded-xl text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 w-full transition-all duration-300 shadow-xl shadow-green-200 active:scale-95 disabled:bg-green-400 disabled:cursor-not-allowed"
                    >
                        {isLoading ? (
                            <Loader2 className="w-5 h-5 animate-spin mr-2" />
                        ) : null}
                        {isLoading ? "Creating Account..." : "Sign Up"}
                    </button>

                    <div className="text-center mt-8 animate-fade-in" style={{ animationDelay: '400ms' }}>
                        <p className="text-sm text-gray-600">
                            Already have an account?{' '}
                            <Link to="/login" className="font-bold text-green-600 hover:underline">
                                Login Here
                            </Link>
                        </p>
                    </div>
                </form>
            </div>
        </div>
    );
}
