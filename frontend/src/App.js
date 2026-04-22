import { useState, useEffect, createContext, useContext } from "react";
import "@/App.css";
import "@/i18n"; // Initialize i18n
import { BrowserRouter, Routes, Route, Navigate, useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import { Toaster } from "@/components/ui/sonner";

// Pages
import LandingPage from "@/pages/LandingPage";
import AuthCallback from "@/pages/AuthCallback";
import Gallery from "@/pages/Gallery";
import StoryDetail from "@/pages/StoryDetail";
import VRExperience from "@/pages/VRExperience";
import Pricing from "@/pages/Pricing";
import Dashboard from "@/pages/Dashboard";
import PaymentSuccess from "@/pages/PaymentSuccess";
import AboutUs from "@/pages/AboutUs";
import OurTechnology from "@/pages/OurTechnology";
import Events from "@/pages/Events";
import CRMDashboard from "@/pages/CRMDashboard";
import ArtRestoration from "@/pages/ArtRestoration";
import ArchitectsLanding from "@/pages/ArchitectsLanding";
import ArchitectsPricing from "@/pages/ArchitectsPricing";
import ArchitectsDashboard from "@/pages/ArchitectsDashboard";
import ArchitectsInspection from "@/pages/ArchitectsInspection";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const checkAuth = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`, {
        withCredentials: true,
      });
      setUser(response.data);
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const login = () => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + '/dashboard';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  const logout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
      setUser(null);
      window.location.href = '/';
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  return (
    <AuthContext.Provider value={{ user, setUser, loading, login, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-[#D4AF37] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-[#A8A8A0] font-body">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/" state={{ from: location }} replace />;
  }

  return children;
};

// App Router with session_id detection
function AppRouter() {
  const location = useLocation();

  // Check URL fragment for session_id synchronously during render
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/gallery" element={<Gallery />} />
      <Route path="/story/:storyId" element={<StoryDetail />} />
      <Route path="/pricing" element={<Pricing />} />
      <Route path="/about" element={<AboutUs />} />
      <Route path="/technology" element={<OurTechnology />} />
      <Route path="/events" element={<Events />} />
      <Route path="/payment/success" element={<PaymentSuccess />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/crm"
        element={
          <ProtectedRoute>
            <CRMDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/experience/:storyId"
        element={
          <ProtectedRoute>
            <VRExperience />
          </ProtectedRoute>
        }
      />
      <Route
        path="/restoration"
        element={
          <ProtectedRoute>
            <ArtRestoration />
          </ProtectedRoute>
        }
      />
      <Route path="/architects" element={<ArchitectsLanding />} />
      <Route path="/architects/pricing" element={<ArchitectsPricing />} />
      <Route
        path="/architects/dashboard"
        element={
          <ProtectedRoute>
            <ArchitectsDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/architects/inspection/:inspectionId"
        element={
          <ProtectedRoute>
            <ArchitectsInspection />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="App min-h-screen bg-[#FAFAF8]">
          <AppRouter />
          <Toaster position="bottom-right" theme="light" />
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
