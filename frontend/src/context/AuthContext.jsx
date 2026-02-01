import { createContext, useContext, useState, useEffect } from 'react';
import api from '../api';

const AuthContext = createContext();

// Token logic moved to api.js

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        checkUser();
    }, []);

    const checkUser = async () => {
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
    };

    const login = async (email, password) => {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);

        try {
            const response = await api.post('/auth/login', formData);
            localStorage.setItem('token', response.data.access_token);
            await checkUser();
            return true;
        } catch (error) {
            console.error(error);
            return false;
        }
    };

    const register = async (email, password) => {
        try {
            await api.post('/auth/register', { email, password });
            return await login(email, password);
        } catch (error) {
            console.error(error);
            return false;
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
