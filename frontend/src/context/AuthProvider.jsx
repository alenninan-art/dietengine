import { useState, useEffect, useCallback } from 'react';
import api, { API_BASE, API_CONFIG_ERROR } from '../api';
import { AuthContext } from './AuthContext';

// Token logic moved to api.js

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const checkUser = useCallback(async () => {
        if (API_CONFIG_ERROR) {
            setUser(null);
            setLoading(false);
            return;
        }
        const token = localStorage.getItem('token');
        if (token) {
            try {
                const response = await api.get('/auth/me');
                setUser(response.data);
            } catch (error) {
                console.error("Auth check failed", error);
                localStorage.removeItem('token');
                setUser(null);
            }
        }
        setLoading(false);
    }, []);

    useEffect(() => {
        Promise.resolve().then(checkUser);
    }, [checkUser]);

    const login = async (email, password) => {
        if (API_CONFIG_ERROR) {
            return { success: false, message: API_CONFIG_ERROR };
        }

        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);

        try {
            console.log(`Attempting login for: ${email}`);
            const response = await api.post('/auth/login', params);
            localStorage.setItem('token', response.data.access_token);

            // Critical: Ensure checkUser updates the state before we return success
            // This prevents the "successful login but redirected back to login" loop
            await checkUser();

            // Re-fetch token to ensure it's set (safety check)
            const token = localStorage.getItem('token');
            if (token) {
                return { success: true };
            } else {
                return { success: false, message: 'Auth session could not be established.' };
            }
        } catch (error) {
            console.error('Login error details:', {
                status: error.response?.status,
                data: error.response?.data,
                message: error.message,
                code: error.code
            });

            let errorMessage = 'Network or server error';

            if (error.response && error.response.data) {
                const detail = error.response.data.detail;
                if (typeof detail === 'string') {
                    errorMessage = detail;
                } else if (Array.isArray(detail)) {
                    errorMessage = detail.map(d => d.msg || JSON.stringify(d)).join(', ');
                } else if (detail && typeof detail === 'object') {
                    errorMessage = detail.message || JSON.stringify(detail);
                }
            } else if (error.request && !error.response) {
                errorMessage = `API unreachable at ${API_BASE}. Please ensure your backend is deployed and VITE_API_URL is set correctly.`;
            }

            return { success: false, message: errorMessage };
        }
    };

    const register = async (email, password) => {
        if (API_CONFIG_ERROR) {
            return { success: false, message: API_CONFIG_ERROR };
        }

        try {
            await api.post('/auth/register', { email, password });
            return await login(email, password);
        } catch (error) {
            console.error('Registration error:', error);
            let errorMessage = 'Registration failed. Email may be taken or server is down.';

            if (error.response && error.response.data) {
                const detail = error.response.data.detail;
                if (typeof detail === 'string') {
                    errorMessage = detail;
                } else if (Array.isArray(detail)) {
                    errorMessage = detail.map(d => d.msg || JSON.stringify(d)).join(', ');
                }
            }
            return { success: false, message: errorMessage };
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading, checkUser }}>
            {children}
        </AuthContext.Provider>
    );
};


