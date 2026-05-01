import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const AuthCallback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    navigate("/dashboard", { replace: true });
  }, [navigate]);

  return (
    <div className="min-h-screen bg-[#080d1c] flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-2 border-[#D4AF37] border-t-transparent rounded-full animate-spin mx-auto mb-6"></div>
        <h2 className="font-display text-2xl text-[#F5F5F0] mb-2">Authenticating</h2>
        <p className="text-[#A8A8A0]">Please wait while we sign you in...</p>
      </div>
    </div>
  );
};

export default AuthCallback;
