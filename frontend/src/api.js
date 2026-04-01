import axios from 'axios';

const getBaseURL = () => {
    if (import.meta.env.VITE_API_URL) return import.meta.env.VITE_API_URL;

    // In local development, the React app runs on Vite while the API runs on FastAPI.
    if (import.meta.env.DEV) {
        const protocol = window.location.protocol;
        const hostname = window.location.hostname;
        return `${protocol}//${hostname}:8000`;
    }

    // Default to same origin for deployed setups where the API is served from the same domain.
    const protocol = window.location.protocol;
    const hostname = window.location.hostname;
    const port = window.location.port ? `:${window.location.port}` : '';
    return `${protocol}//${hostname}${port}`;
};

// Compute and export the base URL so the app can show diagnostics when network errors occur.
const API_BASE = getBaseURL();

const api = axios.create({
    baseURL: API_BASE,
});

// Add token to requests automatically
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

const checkBackendHealth = async () => {
    try {
        await api.get('/diagnostics');
        return true;
    } catch {
        return false;
    }
};

export { API_BASE, checkBackendHealth };
export default api;
