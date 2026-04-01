import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import { Apple, Dumbbell, TrendingUp, Clock, Flame, ArrowLeft, Brain, MessageSquare, LogOut, UserPlus, Sparkles } from 'lucide-react';
import api from '../api';

export default function Recommendations() {
    const { logout } = useAuth();
    const navigate = useNavigate();
    const [dietPlans, setDietPlans] = useState([]);
    const [exercises, setExercises] = useState([]);
    const [trackingSummary, setTrackingSummary] = useState({ total_tracked: 0, this_week: 0, average_price: 0, latest_selection: null });
    const [trackingHistory, setTrackingHistory] = useState([]);
    const [selectedAlternatives, setSelectedAlternatives] = useState({});
    const [savingMealId, setSavingMealId] = useState(null);
    const [selectedTab, setSelectedTab] = useState('diet');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchRecommendations();
    }, []);

    const fetchRecommendations = async () => {
        try {
            const [dietResponse, exerciseResponse, trackingSummaryResponse, trackingHistoryResponse] = await Promise.all([
                api.get('/recommendations/diet'),
                api.get('/recommendations/exercise'),
                api.get('/tracking/foods/summary'),
                api.get('/tracking/foods?limit=6'),
            ]);
            setDietPlans(dietResponse.data);
            setExercises(exerciseResponse.data);
            setTrackingSummary(trackingSummaryResponse.data);
            setTrackingHistory(trackingHistoryResponse.data);
            setError(null);
        } catch (err) {
            console.error('Failed to fetch recommendations:', err);
            setError(err.response?.data?.detail || 'Failed to load recommendations. Please complete your profile first.');
        } finally {
            setLoading(false);
        }
    };

    const refreshTracking = async () => {
        const [trackingSummaryResponse, trackingHistoryResponse] = await Promise.all([
            api.get('/tracking/foods/summary'),
            api.get('/tracking/foods?limit=6'),
        ]);
        setTrackingSummary(trackingSummaryResponse.data);
        setTrackingHistory(trackingHistoryResponse.data);
    };

    const getSelectedOption = (meal) => {
        const selected = selectedAlternatives[meal.id];
        if (selected) return selected;
        return {
            name: meal.name,
            price_estimate: meal.price_estimate,
        };
    };

    const handleAlternativeChange = (meal, optionName) => {
        if (optionName === meal.name) {
            setSelectedAlternatives((prev) => ({
                ...prev,
                [meal.id]: { name: meal.name, price_estimate: meal.price_estimate },
            }));
            return;
        }

        const option = meal.alternative_foods.find((item) => item.name === optionName);
        if (!option) return;

        setSelectedAlternatives((prev) => ({
            ...prev,
            [meal.id]: option,
        }));
    };

    const handleTrackMeal = async (plan, meal) => {
        const selected = getSelectedOption(meal);
        try {
            setSavingMealId(meal.id);
            await api.post('/tracking/foods', {
                meal_name: meal.name,
                meal_type: meal.meal_type,
                selected_option: selected.name,
                source_plan: plan.name,
                price_estimate: selected.price_estimate ?? meal.price_estimate,
                notes: selected.name === meal.name ? 'Saved original recommendation' : 'Saved alternative food selection',
            });
            await refreshTracking();
        } catch (err) {
            console.error('Failed to track meal selection:', err);
        } finally {
            setSavingMealId(null);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center">
                <div className="relative">
                    <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
                    <div className="mt-6 text-lg font-semibold text-gray-700 animate-pulse text-center">
                        Personalizing your plans...
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-slate-50 p-8 flex items-center justify-center">
                <div className="max-w-md w-full glass p-8 bg-white/40 border border-white/50 rounded-2xl shadow-xl text-center">
                    <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 text-left animate-fade-in">
                        <p className="text-red-700 text-sm font-medium">{error}</p>
                    </div>
                    <button
                        onClick={() => navigate('/profile')}
                        className="w-full py-3 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 transition shadow-lg shadow-blue-200 transform hover:-translate-y-0.5 active:scale-95 flex items-center justify-center gap-2"
                    >
                        <UserPlus className="w-5 h-5" />
                        Complete Profile
                    </button>
                    <p className="mt-6 text-sm text-gray-500">
                        You need to set your height, weight, and age to get accurate recommendations.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
            <div className="max-w-7xl mx-auto">
                <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-sm p-6 mb-6 border border-white/50 animate-slide-up">
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                        <div>
                            <div className="flex items-center gap-2 mb-1">
                                <Sparkles className="w-5 h-5 text-blue-600" />
                                <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Personalized Recommendations</h1>
                            </div>
                            <p className="text-gray-600 font-medium">Tailored diet plans, alternatives, and food tracking built around your profile</p>
                        </div>
                        <div className="flex flex-wrap gap-2">
                            <button
                                onClick={() => navigate('/ai')}
                                className="px-4 py-2.5 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-all flex items-center gap-2 font-semibold shadow-md shadow-indigo-100 active:scale-95"
                            >
                                <Brain className="w-4 h-4" />
                                AI Scan
                            </button>
                            <button
                                onClick={() => navigate('/chat')}
                                className="px-4 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all flex items-center gap-2 font-semibold shadow-md shadow-blue-100 active:scale-95"
                            >
                                <MessageSquare className="w-4 h-4" />
                                AI Chat
                            </button>
                            <button
                                onClick={() => navigate('/profile')}
                                className="px-4 py-2.5 bg-white border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 transition-all flex items-center gap-2 font-semibold active:scale-95"
                            >
                                <ArrowLeft className="w-4 h-4" />
                                Profile
                            </button>
                            <button
                                onClick={logout}
                                className="px-4 py-2.5 bg-white border border-red-100 text-red-600 rounded-xl hover:bg-red-50 transition-all flex items-center gap-2 font-semibold active:scale-95"
                            >
                                <LogOut className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                </div>

                <div className="grid md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
                        <div className="text-xs uppercase tracking-wider text-slate-500 font-semibold">Tracked Foods</div>
                        <div className="text-3xl font-black text-slate-900 mt-2">{trackingSummary.total_tracked}</div>
                    </div>
                    <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
                        <div className="text-xs uppercase tracking-wider text-slate-500 font-semibold">This Week</div>
                        <div className="text-3xl font-black text-emerald-600 mt-2">{trackingSummary.this_week}</div>
                    </div>
                    <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
                        <div className="text-xs uppercase tracking-wider text-slate-500 font-semibold">Avg Price</div>
                        <div className="text-3xl font-black text-amber-600 mt-2">Rs {Number(trackingSummary.average_price || 0).toFixed(0)}</div>
                    </div>
                    <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
                        <div className="text-xs uppercase tracking-wider text-slate-500 font-semibold">Latest Pick</div>
                        <div className="text-sm font-bold text-indigo-700 mt-3">{trackingSummary.latest_selection || 'No selection yet'}</div>
                    </div>
                </div>

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
                                                Rs {plan.meals.reduce((sum, meal) => sum + meal.price_estimate, 0).toFixed(0)}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <h3 className="text-xl font-semibold text-gray-800 mb-4">Meal Plan</h3>
                                <div className="grid md:grid-cols-2 gap-4">
                                    {plan.meals.map((meal, mealIdx) => {
                                        const selectedOption = getSelectedOption(meal);
                                        const selectedAlternative = meal.alternative_foods.find((item) => item.name === selectedOption.name);

                                        return (
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
                                                <div className="flex justify-between items-center mb-2">
                                                    <div className="flex gap-3 text-xs">
                                                        <span className="bg-green-100 text-green-700 px-2 py-1 rounded">P: {meal.protein_g}g</span>
                                                        <span className="bg-yellow-100 text-yellow-700 px-2 py-1 rounded">C: {meal.carbs_g}g</span>
                                                        <span className="bg-orange-100 text-orange-700 px-2 py-1 rounded">F: {meal.fats_g}g</span>
                                                    </div>
                                                    <div className="text-sm border-l pl-3 font-semibold text-gray-700">
                                                        Rs {meal.price_estimate.toFixed(0)}
                                                    </div>
                                                </div>
                                                <div className="flex items-center justify-between gap-3 mt-3">
                                                    <span className={`text-xs font-bold uppercase tracking-wider px-2 py-1 rounded-full ${meal.price_level === 'budget' ? 'bg-emerald-100 text-emerald-700' : meal.price_level === 'moderate' ? 'bg-blue-100 text-blue-700' : 'bg-rose-100 text-rose-700'}`}>
                                                        {meal.price_level} price
                                                    </span>
                                                    <button
                                                        onClick={() => handleTrackMeal(plan, meal)}
                                                        disabled={savingMealId === meal.id}
                                                        className="px-3 py-2 rounded-lg bg-slate-900 text-white text-sm font-semibold hover:bg-slate-800 transition disabled:opacity-60"
                                                    >
                                                        {savingMealId === meal.id ? 'Saving...' : 'Track Choice'}
                                                    </button>
                                                </div>

                                                {meal.alternative_foods?.length > 0 && (
                                                    <div className="mt-4 rounded-xl bg-slate-50 border border-slate-200 p-3">
                                                        <div className="text-xs uppercase tracking-wider text-slate-500 font-bold mb-2">Alternative Foods</div>
                                                        <select
                                                            value={selectedOption.name}
                                                            onChange={(e) => handleAlternativeChange(meal, e.target.value)}
                                                            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 outline-none"
                                                        >
                                                            <option value={meal.name}>Keep original: {meal.name}</option>
                                                            {meal.alternative_foods.map((option) => (
                                                                <option key={option.name} value={option.name}>
                                                                    {option.name} - Rs {option.price_estimate.toFixed(0)} - {option.price_level}
                                                                </option>
                                                            ))}
                                                        </select>
                                                        <div className="mt-2 text-sm text-slate-600">
                                                            {selectedAlternative ? selectedAlternative.reason : 'Choose an alternative if you want a similar meal at a different budget or style.'}
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        ))}
                    </div>
                )}

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

                <div className="mt-8 bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
                    <h3 className="text-xl font-bold text-slate-900 mb-4">Recent Food Tracking</h3>
                    {trackingHistory.length === 0 ? (
                        <p className="text-slate-500 text-sm">Tracked meals will appear here after you save a recommendation or alternative.</p>
                    ) : (
                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {trackingHistory.map((entry) => (
                                <div key={entry.id} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                                    <div className="text-xs uppercase tracking-wider text-slate-500 font-semibold">{entry.meal_type || 'meal'}</div>
                                    <div className="text-base font-bold text-slate-900 mt-1">{entry.selected_option}</div>
                                    <div className="text-sm text-slate-600 mt-1">From {entry.meal_name}</div>
                                    <div className="text-sm text-slate-600 mt-1">Plan: {entry.source_plan || 'Custom'}</div>
                                    <div className="text-sm font-semibold text-amber-700 mt-2">Rs {entry.price_estimate.toFixed(0)}</div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
