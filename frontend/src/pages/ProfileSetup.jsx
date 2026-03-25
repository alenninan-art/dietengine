import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import { User, Scale, Ruler, Calendar, Activity, Target, ArrowRight, LayoutDashboard, Utensils, Brain, MessageSquare, ShieldCheck, LogOut } from 'lucide-react';
import api from '../api';

export default function ProfileSetup() {
    const { user, logout, checkUser } = useAuth();
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        full_name: '',
        age: '',
        height: '',
        weight: '',
        gender: '',
        activity_level: '',
        health_goals: '',
        workout_location: 'Gym',
        equipment_available: '',
        injuries_limitations: '',
        workout_days_per_week: 3
    });
    const [bmi, setBmi] = useState(null);
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        if (user) {
            setFormData({
                full_name: user.full_name || '',
                age: user.age || '',
                height: user.height || '',
                weight: user.weight || '',
                gender: user.gender || '',
                activity_level: user.activity_level || '',
                health_goals: user.health_goals || '',
                workout_location: user.workout_location || 'Gym',
                equipment_available: user.equipment_available || '',
                injuries_limitations: user.injuries_limitations || '',
                workout_days_per_week: user.workout_days_per_week || 3
            });

            // Fetch BMI if height and weight are set
            if (user.height && user.weight) {
                fetchBMI();
            }
        }
    }, [user]);

    const fetchBMI = async () => {
        try {
            const response = await api.get('/profile/bmi');
            setBmi(response.data);
        } catch (error) {
            console.error('Failed to fetch BMI:', error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setSuccess(false);

        try {
            const age = parseInt(formData.age);
            const height = parseFloat(formData.height);
            const weight = parseFloat(formData.weight);

            const dataToSend = {
                full_name: formData.full_name || null,
                age: !isNaN(age) ? age : null,
                height: !isNaN(height) ? height : null,
                weight: !isNaN(weight) ? weight : null,
                gender: formData.gender || null,
                activity_level: formData.activity_level || null,
                health_goals: formData.health_goals || null,
                workout_location: formData.workout_location || null,
                equipment_available: formData.equipment_available || null,
                injuries_limitations: formData.injuries_limitations || null,
                workout_days_per_week: parseInt(formData.workout_days_per_week) || 3
            };

            await api.put('/profile/', dataToSend);
            await checkUser();
            setSuccess(true);


            // Fetch updated BMI if height and weight are set
            if (formData.height && formData.weight) {
                await fetchBMI();
            }
        } catch (error) {
            console.error('Failed to update profile:', error);
            setError(error.response?.data?.detail || 'Failed to update profile. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8 animate-fade-in">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="bg-white rounded-lg shadow-md p-6 mb-6 animate-slide-up">
                    <div className="flex justify-between items-center">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-800">Profile Setup</h1>
                            <p className="text-gray-600">Complete your health profile for personalized recommendations</p>
                        </div>
                        <button
                            onClick={logout}
                            className="px-4 py-2 bg-white/50 border border-red-200 text-red-600 rounded-xl hover:bg-red-50 transition shadow-sm flex items-center gap-2 font-medium"
                        >
                            <LogOut className="w-4 h-4" />
                            Logout
                        </button>
                    </div>
                </div>

                <div className="grid md:grid-cols-3 gap-6">
                    {/* Profile Form */}
                    <div className="md:col-span-2 bg-white rounded-lg shadow-md p-6 animate-slide-up" style={{ animationDelay: '100ms' }}>
                        <h2 className="text-2xl font-bold text-gray-800 mb-6">Your Information</h2>

                        {error && (
                            <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 animate-fade-in">
                                <p className="text-red-700 text-sm font-medium">{error}</p>
                            </div>
                        )}

                        {success && (
                            <div className="mb-6 animate-pop">
                                <div className="p-4 bg-green-50 border-l-4 border-green-500 text-green-700 rounded-xl mb-4 flex items-center justify-between shadow-sm">
                                    <div className="flex items-center gap-2">
                                        <ShieldCheck className="w-5 h-5 text-green-600" />
                                        <span className="font-semibold">Profile updated successfully!</span>
                                    </div>
                                    <button
                                        onClick={() => navigate('/recommendations')}
                                        className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-green-700 transition flex items-center gap-2 shadow-md shadow-green-200"
                                    >
                                        <ArrowRight className="w-4 h-4" />
                                        View Results
                                    </button>
                                </div>
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="animate-slide-up" style={{ animationDelay: '200ms' }}>
                                <label className="block text-gray-700 font-medium mb-2">
                                    <User className="inline w-5 h-5 mr-2 animate-pop" />
                                    Full Name
                                </label>
                                <input
                                    type="text"
                                    name="full_name"
                                    value={formData.full_name}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                    placeholder="Enter your full name"
                                />
                            </div>

                            <div className="grid md:grid-cols-2 gap-4">
                                <div className="animate-slide-up" style={{ animationDelay: '300ms' }}>
                                    <label className="block text-gray-700 font-medium mb-2">
                                        <Calendar className="inline w-5 h-5 mr-2 animate-pop" />
                                        Age
                                    </label>
                                    <input
                                        type="number"
                                        name="age"
                                        value={formData.age}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                        placeholder="Age"
                                        min="1"
                                        max="120"
                                    />
                                </div>

                                <div className="animate-slide-up" style={{ animationDelay: '350ms' }}>
                                    <label className="block text-gray-700 font-medium mb-2">
                                        Gender
                                    </label>
                                    <select
                                        name="gender"
                                        value={formData.gender}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                    >
                                        <option value="">Select gender</option>
                                        <option value="male">Male</option>
                                        <option value="female">Female</option>
                                        <option value="other">Other</option>
                                    </select>
                                </div>
                            </div>

                            <div className="grid md:grid-cols-2 gap-4">
                                <div className="animate-slide-up" style={{ animationDelay: '400ms' }}>
                                    <label className="block text-gray-700 font-medium mb-2">
                                        <Ruler className="inline w-5 h-5 mr-2 animate-pop" />
                                        Height (cm)
                                    </label>
                                    <input
                                        type="number"
                                        name="height"
                                        value={formData.height}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                        placeholder="Enter height in cm"
                                        step="0.1"
                                        min="1"
                                    />
                                </div>

                                <div className="animate-slide-up" style={{ animationDelay: '450ms' }}>
                                    <label className="block text-gray-700 font-medium mb-2">
                                        <Scale className="inline w-5 h-5 mr-2 animate-pop" />
                                        Weight (kg)
                                    </label>
                                    <input
                                        type="number"
                                        name="weight"
                                        value={formData.weight}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                        placeholder="Enter weight in kg"
                                        step="0.1"
                                        min="1"
                                    />
                                </div>
                            </div>

                            <div className="animate-slide-up" style={{ animationDelay: '500ms' }}>
                                <label className="block text-gray-700 font-medium mb-2">
                                    <Activity className="inline w-5 h-5 mr-2 animate-pop" />
                                    Activity Level
                                </label>
                                <select
                                    name="activity_level"
                                    value={formData.activity_level}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                >
                                    <option value="">Select activity level</option>
                                    <option value="sedentary">Sedentary (little or no exercise)</option>
                                    <option value="lightly_active">Lightly Active (1-3 days/week)</option>
                                    <option value="moderately_active">Moderately Active (3-5 days/week)</option>
                                    <option value="very_active">Very Active (6-7 days/week)</option>
                                    <option value="extra_active">Extra Active (intense exercise daily)</option>
                                </select>
                            </div>

                            <div className="animate-slide-up" style={{ animationDelay: '550ms' }}>
                                <label className="block text-gray-700 font-medium mb-2">
                                    <Target className="inline w-5 h-5 mr-2 animate-pop" />
                                    Health Goals
                                </label>
                                <textarea
                                    name="health_goals"
                                    value={formData.health_goals}
                                    onChange={handleChange}
                                    className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                                    placeholder="e.g., Lose weight, Build muscle, Maintain health"
                                    rows="3"
                                />
                            </div>

                            {/* Fitness Coach Section */}
                            <div className="pt-6 border-t border-gray-100 space-y-4 animate-slide-up" style={{ animationDelay: '600ms' }}>
                                <h3 className="text-lg font-bold text-blue-800 flex items-center gap-2">
                                    <Brain className="w-5 h-5" />
                                    AI Fitness Coach Settings
                                </h3>

                                <div className="grid md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-gray-700 font-medium mb-2">Workout Location</label>
                                        <select
                                            name="workout_location"
                                            value={formData.workout_location}
                                            onChange={handleChange}
                                            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        >
                                            <option value="Gym">Gym</option>
                                            <option value="Home">Home (No Gym Access)</option>
                                            <option value="Outdoors">Outdoors</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-gray-700 font-medium mb-2">Days per Week</label>
                                        <input
                                            type="number"
                                            name="workout_days_per_week"
                                            value={formData.workout_days_per_week}
                                            onChange={handleChange}
                                            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            min="1"
                                            max="7"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-gray-700 font-medium mb-2">Equipment Available</label>
                                    <input
                                        type="text"
                                        name="equipment_available"
                                        value={formData.equipment_available}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        placeholder="e.g., Dumbbells, Resistance bands, Pull-up bar"
                                    />
                                </div>

                                <div>
                                    <label className="block text-gray-700 font-medium mb-2">Injuries or Limitations</label>
                                    <input
                                        type="text"
                                        name="injuries_limitations"
                                        value={formData.injuries_limitations}
                                        onChange={handleChange}
                                        className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        placeholder="e.g., Lower back pain, shoulder injury"
                                    />
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition disabled:bg-gray-400 flex items-center justify-center shadow-lg animate-pop"
                                style={{ animationDelay: '600ms' }}
                            >
                                {loading ? 'Saving...' : 'Save Profile'}
                                <ArrowRight className="ml-2 w-5 h-5" />
                            </button>
                        </form>
                    </div>

                    {/* BMI Display */}
                    <div className="space-y-6">
                        {bmi && (
                            <div className="bg-white rounded-lg shadow-md p-6 animate-pop" style={{ animationDelay: '200ms' }}>
                                <h3 className="text-xl font-bold text-gray-800 mb-4">Your BMI</h3>
                                <div className="text-center">
                                    <div className="text-5xl font-bold text-blue-600 mb-2">
                                        {bmi.bmi}
                                    </div>
                                    <div className={`text-lg font-semibold mb-4 ${bmi.category === 'Normal weight' ? 'text-green-600' :
                                        bmi.category === 'Underweight' ? 'text-yellow-600' :
                                            bmi.category === 'Overweight' ? 'text-orange-600' :
                                                'text-red-600'
                                        }`}>
                                        {bmi.category}
                                    </div>
                                    <div className="text-sm text-gray-600 space-y-1">
                                        <p>Height: {bmi.height} cm</p>
                                        <p>Weight: {bmi.weight} kg</p>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg shadow-md p-6 text-white animate-slide-up" style={{ animationDelay: '300ms' }}>
                            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                                <LayoutDashboard className="w-5 h-5 text-blue-200" />
                                Next Steps
                            </h3>
                            <div className="space-y-3">
                                <button
                                    onClick={() => navigate('/recommendations')}
                                    className="w-full text-left p-3 rounded-xl bg-white/10 hover:bg-white/20 transition group flex items-center justify-between border border-white/10"
                                >
                                    <div className="flex items-center gap-3">
                                        <Utensils className="w-5 h-5 text-blue-200" />
                                        <span className="font-semibold">View Diet Plans</span>
                                    </div>
                                    <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition" />
                                </button>

                                <button
                                    onClick={() => navigate('/ai')}
                                    className="w-full text-left p-3 rounded-xl bg-white/10 hover:bg-white/20 transition group flex items-center justify-between border border-white/10"
                                >
                                    <div className="flex items-center gap-3">
                                        <Brain className="w-5 h-5 text-blue-200" />
                                        <span className="font-semibold">AI Calorie Scan</span>
                                    </div>
                                    <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition" />
                                </button>

                                <button
                                    onClick={() => navigate('/chat')}
                                    className="w-full text-left p-3 rounded-xl bg-white/10 hover:bg-white/20 transition group flex items-center justify-between border border-white/10"
                                >
                                    <div className="flex items-center gap-3">
                                        <MessageSquare className="w-5 h-5 text-blue-200" />
                                        <span className="font-semibold">Chat with AI</span>
                                    </div>
                                    <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
