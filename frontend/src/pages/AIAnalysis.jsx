import { useState, useRef } from 'react';
import { Camera, Upload, Send, Brain, Flame, Info, ArrowLeft, RefreshCw } from 'lucide-react';
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

export default function AIAnalysis() {
    const navigate = useNavigate();
    const [selectedImage, setSelectedImage] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [analyzing, setAnalyzing] = useState(false);
    const [result, setResult] = useState(null);
    const fileInputRef = useRef(null);

    const handleImageSelect = (e) => {
        const file = e.target.files[0];
        if (file && file.type.startsWith('image/')) {
            setSelectedImage(file);
            setPreviewUrl(URL.createObjectURL(file));
            setResult(null);
        }
    };

    const handleAnalyze = async () => {
        if (!selectedImage) return;

        setAnalyzing(true);
        const formData = new FormData();
        formData.append('file', selectedImage);

        try {
            const response = await api.post('/ai/estimate', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setResult(response.data);
        } catch (error) {
            console.error('AI Analysis failed:', error);
            alert('Failed to analyze image. Please try again.');
        } finally {
            setAnalyzing(false);
        }
    };

    const reset = () => {
        setSelectedImage(null);
        setPreviewUrl(null);
        setResult(null);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-100 p-8 animate-fade-in">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="bg-white rounded-lg shadow-md p-6 mb-6 animate-slide-up">
                    <div className="flex justify-between items-center">
                        <div className="flex items-center gap-3">
                            <div className="bg-indigo-600 p-2 rounded-lg animate-pop">
                                <Brain className="text-white w-6 h-6" />
                            </div>
                            <div>
                                <h1 className="text-3xl font-bold text-gray-800">AI Food Analysis</h1>
                                <p className="text-gray-600">Snap a photo of your meal for instant calorie estimation</p>
                            </div>
                        </div>
                        <button
                            onClick={() => navigate('/recommendations')}
                            className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition flex items-center gap-2"
                        >
                            <ArrowLeft className="w-4 h-4" />
                            Back
                        </button>
                    </div>
                </div>

                <div className="grid md:grid-cols-2 gap-8">
                    {/* Upload Section */}
                    <div className="bg-white rounded-lg shadow-md p-6 flex flex-col items-center justify-center border-2 border-dashed border-gray-200 min-h-[400px] animate-slide-up" style={{ animationDelay: '100ms' }}>
                        {!previewUrl ? (
                            <div className="text-center">
                                <div className="bg-indigo-50 p-6 rounded-full inline-block mb-4 animate-pop" style={{ animationDelay: '200ms' }}>
                                    <Camera className="w-12 h-12 text-indigo-600" />
                                </div>
                                <h3 className="text-xl font-semibold mb-2 text-gray-800">Choose an Image</h3>
                                <p className="text-gray-500 mb-6">Upload a photo of your food to analyze</p>
                                <input
                                    type="file"
                                    accept="image/*"
                                    className="hidden"
                                    ref={fileInputRef}
                                    onChange={handleImageSelect}
                                />
                                <button
                                    onClick={() => fileInputRef.current?.click()}
                                    className="px-6 py-3 bg-indigo-600 text-white rounded-full font-semibold hover:bg-indigo-700 transition shadow-lg flex items-center gap-2 mx-auto"
                                >
                                    <Upload className="w-5 h-5" />
                                    Choose Photo
                                </button>
                            </div>
                        ) : (
                            <div className="relative w-full h-full animate-fade-in">
                                <img
                                    src={previewUrl}
                                    alt="Food preview"
                                    className="w-full h-full object-cover rounded-lg"
                                />
                                {!result && !analyzing && (
                                    <button
                                        onClick={reset}
                                        className="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full hover:bg-red-600 shadow-md animate-pop"
                                    >
                                        <RefreshCw className="w-4 h-4" />
                                    </button>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Analysis Result */}
                    <div className="bg-white rounded-lg shadow-md p-6 animate-slide-up" style={{ animationDelay: '200ms' }}>
                        <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                            <Info className="w-6 h-6 text-indigo-600" />
                            Analysis Result
                        </h2>

                        {!selectedImage ? (
                            <div className="text-center py-20 text-gray-400">
                                <Send className="w-12 h-12 mx-auto mb-4 opacity-20" />
                                <p>Select an image to start analysis</p>
                            </div>
                        ) : !result ? (
                            <div className="text-center py-20">
                                <button
                                    onClick={handleAnalyze}
                                    disabled={analyzing}
                                    className={`px-8 py-4 bg-green-600 text-white rounded-full font-bold text-lg hover:bg-green-700 transition shadow-xl flex items-center gap-2 mx-auto ${analyzing ? 'opacity-50 cursor-not-allowed' : ''}`}
                                >
                                    {analyzing ? (
                                        <>
                                            <RefreshCw className="w-6 h-6 animate-spin" />
                                            AI is Thinking...
                                        </>
                                    ) : (
                                        <>
                                            <Send className="w-6 h-6" />
                                            Analyze Now
                                        </>
                                    )}
                                </button>
                                <p className="text-gray-400 mt-4 text-sm">Our AI will detect ingredients and estimate calories</p>
                            </div>
                        ) : (
                            <div className="space-y-6 animate-fade-in">
                                <div className="bg-indigo-50 p-4 rounded-lg flex justify-between items-center animate-slide-up" style={{ animationDelay: '300ms' }}>
                                    <div>
                                        <span className="text-xs font-bold text-indigo-600 uppercase tracking-widest">Detected Item</span>
                                        <div className="text-2xl font-bold text-gray-800">{result.food_name}</div>
                                    </div>
                                    <div className="text-right">
                                        <span className="text-xs font-bold text-gray-500 uppercase tracking-widest">Confidence</span>
                                        <div className="text-xl font-bold text-green-600">{Math.round(result.confidence * 100)}%</div>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-orange-50 p-6 rounded-2xl flex flex-col items-center justify-center border-b-4 border-orange-200 animate-pop" style={{ animationDelay: '400ms' }}>
                                        <Flame className="w-8 h-8 text-orange-500 mb-2" />
                                        <div className="text-3xl font-black text-orange-600">{result.nutrition.calories}</div>
                                        <div className="text-sm font-bold text-orange-400 uppercase">kcal</div>
                                    </div>
                                    <div className="bg-emerald-50 p-6 rounded-2xl flex flex-col items-center justify-center border-b-4 border-emerald-200 animate-pop" style={{ animationDelay: '500ms' }}>
                                        <div className="text-3xl font-black text-emerald-600">{result.nutrition.protein}g</div>
                                        <div className="text-sm font-bold text-emerald-400 uppercase">Protein</div>
                                    </div>
                                    <div className="bg-amber-50 p-6 rounded-2xl flex flex-col items-center justify-center border-b-4 border-amber-200 animate-pop" style={{ animationDelay: '600ms' }}>
                                        <div className="text-3xl font-black text-amber-600">{result.nutrition.carbs}g</div>
                                        <div className="text-sm font-bold text-amber-400 uppercase">Carbs</div>
                                    </div>
                                    <div className="bg-rose-50 p-6 rounded-2xl flex flex-col items-center justify-center border-b-4 border-rose-200 animate-pop" style={{ animationDelay: '700ms' }}>
                                        <div className="text-3xl font-black text-rose-600">{result.nutrition.fats}g</div>
                                        <div className="text-sm font-bold text-rose-400 uppercase">Fats</div>
                                    </div>
                                </div>

                                <p className="text-gray-500 text-sm italic py-4 border-t border-dashed animate-fade-in" style={{ animationDelay: '800ms' }}>
                                    * {result.message} These are estimates for typical portions. Use as a general guide.
                                </p>

                                <button
                                    onClick={reset}
                                    className="w-full py-4 bg-gray-800 text-white rounded-xl font-bold hover:bg-gray-900 transition flex items-center justify-center gap-2 animate-slide-up" style={{ animationDelay: '900ms' }}
                                >
                                    <RefreshCw className="w-5 h-5" />
                                    Analyze Another
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
