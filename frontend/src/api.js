import axios from 'axios';

const normalizeUrl = (value) => value?.trim().replace(/\/+$/, '') || '';

const getBaseURL = () => {
    const configuredApiUrl = normalizeUrl(import.meta.env.VITE_API_URL);
    if (configuredApiUrl) return configuredApiUrl;

    // In local development, the React app runs on Vite while the API runs on FastAPI.
    if (import.meta.env.DEV) {
        const protocol = window.location.protocol;
        const hostname = window.location.hostname;
        return `${protocol}//${hostname}:8000`;
    }

    // Production needs an explicit API URL unless the app is intentionally served from the same origin.
    if (import.meta.env.VITE_USE_SAME_ORIGIN_API === 'true') {
        return window.location.origin;
    }

    return '';
};

// Compute and export the base URL so the app can show diagnostics when network errors occur.
const API_BASE = getBaseURL();
const API_CONFIG_ERROR = API_BASE
    ? ''
    : 'Missing VITE_API_URL for production deployment. Set it to your Render backend URL.';

const api = axios.create({
    baseURL: API_BASE || undefined,
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
    if (!API_BASE) {
        return false;
    }
    try {
        await api.get('/diagnostics');
        return true;
    } catch {
        return false;
    }
};

export { API_BASE, API_CONFIG_ERROR, checkBackendHealth };
export default api;
