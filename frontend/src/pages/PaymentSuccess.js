import { useState, useEffect } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";
import { useAuth, API } from "@/App";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { CheckCircle, XCircle, Loader2, ArrowRight } from "lucide-react";

const PaymentSuccess = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [status, setStatus] = useState("loading"); // loading, success, error
  const [paymentInfo, setPaymentInfo] = useState(null);

  useEffect(() => {
    const sessionId = searchParams.get("session_id");
    if (sessionId) {
      pollPaymentStatus(sessionId);
    } else {
      setStatus("error");
    }
  }, [searchParams]);

  const pollPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 5;
    const pollInterval = 2000;

    if (attempts >= maxAttempts) {
      setStatus("error");
      return;
    }

    try {
      const response = await axios.get(
        `${API}/payments/stripe/status/${sessionId}`,
        { withCredentials: true }
      );

      if (response.data.payment_status === "paid") {
        setStatus("success");
        setPaymentInfo(response.data);
        return;
      } else if (response.data.status === "expired") {
        setStatus("error");
        return;
      }

      // Continue polling
      setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), pollInterval);
    } catch (error) {
      console.error("Payment status error:", error);
      if (attempts >= maxAttempts - 1) {
        setStatus("error");
      } else {
        setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), pollInterval);
      }
    }
  };

  return (
    <div className="min-h-screen bg-[#080d1c] flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {status === "loading" && (
          <div className="card-obsidian rounded-lg p-8 text-center">
            <Loader2 className="w-16 h-16 text-[#D4AF37] animate-spin mx-auto mb-6" />
            <h1 className="font-display text-2xl text-[#F5F5F0] mb-2">
              Processing Payment
            </h1>
            <p className="text-[#A8A8A0]">
              Please wait while we confirm your payment...
            </p>
          </div>
        )}

        {status === "success" && (
          <div className="card-obsidian rounded-lg p-8 text-center border border-[#D4AF37]/30">
            <div className="w-20 h-20 rounded-full bg-[#D4AF37]/10 flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-12 h-12 text-[#D4AF37]" />
            </div>
            <h1 className="font-display text-3xl text-[#F5F5F0] mb-2">
              Payment Successful!
            </h1>
            <p className="text-[#A8A8A0] mb-6">
              Thank you for your purchase. Your access has been unlocked.
            </p>
            
            {paymentInfo && (
              <div className="bg-[#111] rounded-lg p-4 mb-6 text-left">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-[#A8A8A0]">Amount</span>
                  <span className="text-[#F5F5F0] font-mono">
                    ${(paymentInfo.amount_total / 100).toFixed(2)} {paymentInfo.currency?.toUpperCase()}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-[#A8A8A0]">Status</span>
                  <span className="text-[#D4AF37] capitalize">{paymentInfo.payment_status}</span>
                </div>
              </div>
            )}

            <div className="space-y-3">
              <Button 
                onClick={() => navigate('/dashboard')} 
                className="w-full btn-gold"
                data-testid="go-dashboard-btn"
              >
                Go to Dashboard <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
              <Button 
                onClick={() => navigate('/gallery')} 
                variant="outline"
                className="w-full btn-outline-gold"
              >
                Explore Gallery
              </Button>
            </div>
          </div>
        )}

        {status === "error" && (
          <div className="card-obsidian rounded-lg p-8 text-center border border-red-500/30">
            <div className="w-20 h-20 rounded-full bg-red-500/10 flex items-center justify-center mx-auto mb-6">
              <XCircle className="w-12 h-12 text-red-500" />
            </div>
            <h1 className="font-display text-3xl text-[#F5F5F0] mb-2">
              Payment Issue
            </h1>
            <p className="text-[#A8A8A0] mb-6">
              We couldn't confirm your payment. Please try again or contact support.
            </p>
            
            <div className="space-y-3">
              <Button 
                onClick={() => navigate('/pricing')} 
                className="w-full btn-gold"
              >
                Try Again
              </Button>
              <Button 
                onClick={() => navigate('/')} 
                variant="outline"
                className="w-full btn-outline-gold"
              >
                Return Home
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PaymentSuccess;
