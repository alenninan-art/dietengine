import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import ProfileSetup from './pages/ProfileSetup';
import Recommendations from './pages/Recommendations';
import AIAnalysis from './pages/AIAnalysis';
import Chatbot from './pages/Chatbot';

function Dashboard() {
  const { user } = useAuth();

  // Redirect to profile if profile is incomplete
  if (!user?.height || !user?.weight || !user?.age) {
    return <Navigate to="/profile" />;
  }

  // Redirect to recommendations if profile is complete
  return <Navigate to="/recommendations" />;
}

function PrivateRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) return <div className="flex justify-center items-center h-screen">Loading...</div>;

  return user ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/profile" element={
            <PrivateRoute>
              <ProfileSetup />
            </PrivateRoute>
          } />
          <Route path="/recommendations" element={
            <PrivateRoute>
              <Recommendations />
            </PrivateRoute>
          } />
          <Route path="/ai" element={
            <PrivateRoute>
              <AIAnalysis />
            </PrivateRoute>
          } />
          <Route path="/chat" element={
            <PrivateRoute>
              <Chatbot />
            </PrivateRoute>
          } />
          <Route path="/dashboard" element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          } />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
