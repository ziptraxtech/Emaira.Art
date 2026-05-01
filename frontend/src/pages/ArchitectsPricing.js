import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth, API } from "@/App";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Building2,
  Check,
  X,
  ArrowLeft,
  Mail,
  Video,
  Sparkles,
} from "lucide-react";
import { toast } from "sonner";

const FALLBACK_ARCHITECTS_TIERS = [
  {
    tier_id: "architects_starter",
    name: "Starter",
    price: 899.0,
    period: "month",
    inspection_limit: 15000,
    is_contact_only: false,
    features: [
      "Up to 15,000 sq ft",
      "Best for single villas and fit-outs",
      "Defect detection (cracks, spalling, misalignment)",
      "Safety monitoring (PPE checks)",
      "PDF/JSON report export",
      "Up to 500 MB per video clip",
      "Email support",
    ],
  },
  {
    tier_id: "architects_pro",
    name: "Pro",
    price: 2999.0,
    period: "month",
    inspection_limit: 60000,
    is_contact_only: false,
    features: [
      "Up to 60,000 sq ft",
      "Best for mid-rise commercial & residential",
      "All Starter features",
      "Reality vs. Design validation",
      "Custom safety rulesets",
      "Team workspace (up to 10 users)",
      "Priority Gemini 3 Pro analysis queue",
      "Slack / Teams webhook alerts",
      "Dedicated support",
    ],
  },
  {
    tier_id: "architects_premium",
    name: "Premium Plan",
    price: 0.0,
    period: "sq ft",
    inspection_limit: -1,
    is_contact_only: true,
    features: [
      "AED 9.50 – 15.00 / sq ft",
      "Target Assets: High-rise Commercial and Luxury Residential",
      "e.g., Business Bay, Saadiyat Island",
      "Everything in Pro",
      "Custom integrations (BIM, Procore, ACC)",
      "On-premise / private cloud deployment",
      "Custom CV model fine-tuning",
      "24/7 SLA",
      "Dedicated account manager",
    ],
  },
];

const ArchitectsPricing = () => {
  const { user, login } = useAuth();
  const [tiers, setTiers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/architects/tiers`)
      .then((r) => setTiers(Array.isArray(r.data) ? r.data : FALLBACK_ARCHITECTS_TIERS))
      .catch(() => setTiers(FALLBACK_ARCHITECTS_TIERS))
      .finally(() => setLoading(false));
  }, []);

  const handleSubscribe = async (tier) => {
    if (tier.is_contact_only) {
      window.location.href = "mailto:hello@emaira.art?subject=Enterprise%20inquiry";
      return;
    }
    if (!user) {
      login();
      return;
    }
    try {
      const { data } = await axios.post(
        `${API}/payments/checkout`,
        { tier_id: tier.tier_id },
        { withCredentials: true }
      );
      if (data.url) window.location.href = data.url;
    } catch {
      toast.error("Could not start checkout. Contact hello@emaira.art.");
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-[#F5F5F0]">
      <nav className="fixed top-0 left-0 right-0 z-50 glass-dark border-b border-[#1a1a1a]">
        <div className="max-w-7xl mx-auto px-6 h-16 lg:h-20 flex items-center justify-between">
          <Link to="/architects" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded bg-gradient-to-br from-[#D4AF37] to-[#B8860B] flex items-center justify-center">
              <span className="font-display text-[#050505] text-xl font-bold">E</span>
            </div>
            <div className="leading-tight hidden sm:block">
              <div className="font-display text-lg">Emaira<span className="text-[#D4AF37]">.</span>Architects</div>
              <div className="text-[10px] tracking-[0.2em] text-[#A8A8A0] uppercase">Construction QC · AI</div>
            </div>
          </Link>
          <Link to="/architects/dashboard">
            <Button className="btn-gold text-sm">Launch Studio</Button>
          </Link>
        </div>
      </nav>

      <div className="pt-32 pb-20">
        <div className="max-w-7xl mx-auto px-6">
          <Link to="/architects" className="inline-flex items-center text-[#A8A8A0] hover:text-[#F5F5F0] mb-4 text-sm">
            <ArrowLeft className="w-4 h-4 mr-1" /> Back
          </Link>
          <Badge className="bg-[#D4AF37]/15 text-[#D4AF37] border-[#D4AF37]/30 mb-4">
            <Sparkles className="w-3 h-3 mr-1" /> Emaira Architects Plans
          </Badge>
          <h1 className="font-display text-4xl lg:text-6xl mb-4">A profit-optimised, tier-capped SaaS engine.</h1>
          <p className="text-[#A8A8A0] max-w-2xl mb-12">Transitioning from pilot pricing to a highly scalable commercial structure tailored for the UAE market.</p>

          {loading ? (
            <div className="grid md:grid-cols-3 gap-6">
              {[0, 1, 2].map((i) => <div key={i} className="skeleton-dark h-96 rounded-xl" />)}
            </div>
          ) : (
            <div className="grid md:grid-cols-3 gap-6">
              {tiers.map((tier, idx) => {
                const featured = idx === 1;
                return (
                  <div
                    key={tier.tier_id}
                    data-testid={`architects-tier-${tier.tier_id}`}
                    className={`relative rounded-xl p-7 border flex flex-col ${featured ? "border-[#D4AF37] bg-gradient-to-br from-[#D4AF37]/10 to-transparent shadow-[0_0_60px_-20px_rgba(212,175,55,0.5)]" : "border-[#1a1a1a] bg-[#0a0a0a]"}`}
                  >
                    {featured && (
                      <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[#D4AF37] text-[#050505] border-0">MOST POPULAR</Badge>
                    )}
                    <h3 className="font-display text-2xl mb-1">{tier.name}</h3>
                    <div className="flex items-baseline gap-1 mb-2">
                      {tier.tier_id === "architects_premium" ? (
                        <span className="font-display text-3xl text-[#D4AF37]">AED 9.50 – 15.00 / sq ft</span>
                      ) : (
                        <>
                          <span className="font-display text-4xl">${tier.price.toLocaleString()}</span>
                          <span className="text-sm text-[#A8A8A0]">/ mo</span>
                        </>
                      )}
                    </div>
                    <p className="text-sm text-[#A8A8A0] mb-5">
                      {tier.tier_id === "architects_premium" ? "High-rise Commercial & Luxury Residential" : `Up to ${tier.inspection_limit.toLocaleString()} sq ft`}
                    </p>
                    <ul className="space-y-2 mb-6 flex-1">
                      {tier.features.map((f, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-[#F5F5F0]">
                          <Check className="w-4 h-4 text-[#D4AF37] mt-0.5 flex-shrink-0" />
                          {f}
                        </li>
                      ))}
                    </ul>
                    <Button
                      onClick={() => handleSubscribe(tier)}
                      className={featured ? "btn-gold" : "bg-[#1a1a1a] text-[#F5F5F0] hover:bg-[#222]"}
                      data-testid={`architects-subscribe-${tier.tier_id}`}
                    >
                      {tier.is_contact_only ? <><Mail className="w-4 h-4 mr-2" /> Contact Sales</> : <><Video className="w-4 h-4 mr-2" /> Get {tier.name}</>}
                    </Button>
                  </div>
                );
              })}
            </div>
          )}

          <div className="mt-16 text-center text-sm text-[#666660]">
            <Building2 className="w-5 h-5 mx-auto text-[#D4AF37] mb-2" />
            Running 5+ concurrent projects? <a href="mailto:hello@emaira.art" className="text-[#D4AF37] hover:underline">Talk to us</a>.
            <X className="hidden" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArchitectsPricing;
