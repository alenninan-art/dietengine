import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthProvider';
import { useAuth } from './hooks/useAuth';
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
  console.log("PrivateRoute check:", { user: !!user, loading });

  if (loading) return <div style={{ padding: '50px', background: 'yellow' }}>Loading Auth...</div>;

  if (!user) {
    console.log("PrivateRoute: No user, redirecting to login");
    return <Navigate to="/login" />;
  }

  console.log("PrivateRoute: Auth success, rendering children");
  return children;
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
          <Route path="/chat-test" element={<Chatbot />} />
          <Route path="/chatbot" element={<Navigate to="/chat" />} />
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
