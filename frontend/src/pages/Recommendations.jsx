import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Apple, Dumbbell, TrendingUp, Clock, Flame, ArrowLeft, Brain, MessageSquare } from 'lucide-react';
import api from '../api';

export default function Recommendations() {
    const { logout } = useAuth();
    const navigate = useNavigate();
    const [dietPlans, setDietPlans] = useState([]);
    const [exercises, setExercises] = useState([]);
    const [selectedTab, setSelectedTab] = useState('diet'); // 'diet' or 'exercise'
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchRecommendations();
    }, []);

    const fetchRecommendations = async () => {
        try {
            const [dietResponse, exerciseResponse] = await Promise.all([
                api.get('/recommendations/diet'),
                api.get('/recommendations/exercise')
            ]);
            setDietPlans(dietResponse.data);
            setExercises(exerciseResponse.data);
            setError(null);
        } catch (err) {
            console.error('Failed to fetch recommendations:', err);
            setError(err.response?.data?.detail || 'Failed to load recommendations. Please complete your profile first.');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
                <div className="text-xl text-gray-600">Loading recommendations...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
                <div className="max-w-4xl mx-auto">
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                        <p className="font-bold">Error</p>
                        <p>{error}</p>
                    </div>
                    <button
                        onClick={() => navigate('/profile')}
                        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                        Complete Profile
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                    <div className="flex justify-between items-center">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-800">Your Personalized Recommendations</h1>
                            <p className="text-gray-600">Tailored diet plans and exercises based on your profile</p>
                        </div>
                        <div className="flex gap-3">
                            <button
                                onClick={() => navigate('/ai')}
                                className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition flex items-center gap-2"
                            >
                                <Brain className="w-4 h-4" />
                                AI Calorie Scan
                            </button>
                            <button
                                onClick={() => navigate('/chat')}
                                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition flex items-center gap-2"
                            >
                                <MessageSquare className="w-4 h-4" />
                                AI Chat
                            </button>
                            <button
                                onClick={() => navigate('/profile')}
                                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition flex items-center gap-2"
                            >
                                <ArrowLeft className="w-4 h-4" />
                                Back to Profile
                            </button>
                            <button
                                onClick={logout}
                                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition"
                            >
                                Logout
                            </button>
                        </div>
                    </div>
                </div>

                {/* Tab Navigation */}
                <div className="bg-white rounded-lg shadow-md mb-6">
                    <div className="flex border-b">
                        <button
                            onClick={() => setSelectedTab('diet')}
                            className={`flex-1 py-4 px-6 font-semibold transition flex items-center justify-center gap-2 ${selectedTab === 'diet'
                                ? 'text-blue-600 border-b-2 border-blue-600'
                                : 'text-gray-600 hover:text-blue-600'
                                }`}
                        >
                            <Apple className="w-5 h-5" />
                            Diet Plans ({dietPlans.length})
                        </button>
                        <button
                            onClick={() => setSelectedTab('exercise')}
                            className={`flex-1 py-4 px-6 font-semibold transition flex items-center justify-center gap-2 ${selectedTab === 'exercise'
                                ? 'text-blue-600 border-b-2 border-blue-600'
                                : 'text-gray-600 hover:text-blue-600'
                                }`}
                        >
                            <Dumbbell className="w-5 h-5" />
                            Exercises ({exercises.length})
                        </button>
                    </div>
                </div>

                {/* Diet Plans Tab */}
                {selectedTab === 'diet' && (
                    <div className="space-y-6 animate-fade-in">
                        {dietPlans.map((plan, planIdx) => (
                            <div key={plan.id} className="bg-white rounded-lg shadow-md p-6 animate-slide-up" style={{ animationDelay: `${planIdx * 100}ms` }}>
                                <div className="border-b pb-4 mb-4">
                                    <h2 className="text-2xl font-bold text-gray-800 mb-2">{plan.name}</h2>
                                    <p className="text-gray-600 mb-4">{plan.description}</p>

                                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                                        <div className="bg-blue-50 p-3 rounded text-center animate-pop" style={{ animationDelay: '200ms' }}>
                                            <div className="text-xs text-gray-600 uppercase">Calories</div>
                                            <div className="text-xl font-bold text-blue-600">{plan.calories_per_day}</div>
                                        </div>
                                        <div className="bg-green-50 p-3 rounded text-center animate-pop" style={{ animationDelay: '300ms' }}>
                                            <div className="text-xs text-gray-600 uppercase">Protein</div>
                                            <div className="text-xl font-bold text-green-600">{plan.protein_g}g</div>
                                        </div>
                                        <div className="bg-yellow-50 p-3 rounded text-center animate-pop" style={{ animationDelay: '400ms' }}>
                                            <div className="text-xs text-gray-600 uppercase">Carbs</div>
                                            <div className="text-xl font-bold text-yellow-600">{plan.carbs_g}g</div>
                                        </div>
                                        <div className="bg-orange-50 p-3 rounded text-center animate-pop" style={{ animationDelay: '500ms' }}>
                                            <div className="text-xs text-gray-600 uppercase">Fats</div>
                                            <div className="text-xl font-bold text-orange-600">{plan.fats_g}g</div>
                                        </div>
                                        <div className="bg-purple-50 p-3 rounded text-center animate-pop" style={{ animationDelay: '600ms' }}>
                                            <div className="text-xs text-gray-600 uppercase">Daily Cost</div>
                                            <div className="text-xl font-bold text-purple-600">
                                                ₹{plan.meals.reduce((sum, m) => sum + m.price_estimate, 0).toFixed(0)}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <h3 className="text-xl font-semibold text-gray-800 mb-4">Meal Plan</h3>
                                <div className="grid md:grid-cols-2 gap-4">
                                    {plan.meals.map((meal, mealIdx) => (
                                        <div key={meal.id} className="border rounded-lg p-4 hover:shadow-md transition bg-white animate-slide-up" style={{ animationDelay: `${mealIdx * 50 + 700}ms` }}>
                                            <div className="flex justify-between items-start mb-2">
                                                <div>
                                                    <div className="text-xs uppercase text-gray-500 font-semibold">{meal.meal_type}</div>
                                                    <div className="text-lg font-bold text-gray-800">{meal.name}</div>
                                                    {meal.quantity && (
                                                        <div className="text-sm font-medium text-indigo-600 mt-1 flex items-center gap-1">
                                                            <div className="w-1.5 h-1.5 rounded-full bg-indigo-600 animate-pulse"></div>
                                                            Quantity: {meal.quantity}
                                                        </div>
                                                    )}
                                                </div>
                                                <div className="text-right">
                                                    <div className="text-2xl font-bold text-blue-600">{meal.calories}</div>
                                                    <div className="text-xs text-gray-500">cal</div>
                                                </div>
                                            </div>
                                            <p className="text-sm text-gray-600 mb-3">{meal.description}</p>
                                            <div className="flex justify-between items-center mb-1">
                                                <div className="flex gap-3 text-xs">
                                                    <span className="bg-green-100 text-green-700 px-2 py-1 rounded">P: {meal.protein_g}g</span>
                                                    <span className="bg-yellow-100 text-yellow-700 px-2 py-1 rounded">C: {meal.carbs_g}g</span>
                                                    <span className="bg-orange-100 text-orange-700 px-2 py-1 rounded">F: {meal.fats_g}g</span>
                                                </div>
                                                <div className="text-sm border-l pl-3 font-semibold text-gray-700">
                                                    ₹{meal.price_estimate.toFixed(0)}
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Exercise Tab */}
                {selectedTab === 'exercise' && (
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 animate-fade-in">
                        {exercises.map((exercise, idx) => (
                            <div key={exercise.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition animate-pop" style={{ animationDelay: `${idx * 100}ms` }}>
                                <div className="flex justify-between items-start mb-3">
                                    <h3 className="text-xl font-bold text-gray-800">{exercise.name}</h3>
                                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${exercise.intensity === 'low' ? 'bg-green-100 text-green-700' :
                                        exercise.intensity === 'moderate' ? 'bg-yellow-100 text-yellow-700' :
                                            'bg-red-100 text-red-700'
                                        }`}>
                                        {exercise.intensity}
                                    </span>
                                </div>

                                <p className="text-gray-600 text-sm mb-4">{exercise.description}</p>

                                <div className="space-y-2 text-sm">
                                    <div className="flex items-center gap-2 text-gray-700">
                                        <TrendingUp className="w-4 h-4 text-blue-500" />
                                        <span className="font-semibold">Category:</span> {exercise.category}
                                    </div>
                                    <div className="flex items-center gap-2 text-gray-700">
                                        <Clock className="w-4 h-4 text-blue-500" />
                                        <span className="font-semibold">Duration:</span> {exercise.duration_minutes} min
                                    </div>
                                    <div className="flex items-center gap-2 text-gray-700">
                                        <Flame className="w-4 h-4 text-orange-500" />
                                        <span className="font-semibold">Burns:</span> ~{exercise.calories_burned} cal
                                    </div>
                                    {exercise.equipment_needed && (
                                        <div className="flex items-center gap-2 text-gray-700">
                                            <Dumbbell className="w-4 h-4 text-blue-500" />
                                            <span className="font-semibold">Equipment:</span> {exercise.equipment_needed}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
