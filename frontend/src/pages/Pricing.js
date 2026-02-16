import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth, API } from "@/App";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import {
  Check,
  X,
  ArrowLeft,
  Crown,
  Sparkles,
  Eye,
  Fingerprint,
  Palette,
  User,
  Menu,
  LogOut,
  CreditCard
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";

const Pricing = () => {
  const { user, login, logout } = useAuth();
  const navigate = useNavigate();
  const [tiers, setTiers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState("stripe");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    fetchTiers();
  }, []);

  const fetchTiers = async () => {
    try {
      const response = await axios.get(`${API}/payments/tiers`);
      setTiers(response.data);
    } catch (error) {
      console.error("Error fetching tiers:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (tierId) => {
    if (!user) {
      login();
      return;
    }

    setPurchasing(tierId);

    try {
      if (paymentMethod === "stripe") {
        const response = await axios.post(
          `${API}/payments/stripe/checkout`,
          {
            tier_id: tierId,
            origin_url: window.location.origin
          },
          { withCredentials: true }
        );

        if (response.data.url) {
          window.location.href = response.data.url;
        }
      } else {
        // Razorpay
        const response = await axios.post(
          `${API}/payments/razorpay/order`,
          { tier_id: tierId },
          { withCredentials: true }
        );

        const options = {
          key: response.data.key_id,
          amount: response.data.amount,
          currency: response.data.currency,
          order_id: response.data.order_id,
          name: "Emaira.Art",
          description: `${tierId} Subscription`,
          handler: function (rzpResponse) {
            toast.success("Payment successful!");
            navigate('/dashboard');
          },
          prefill: {
            email: user.email,
            name: user.name
          },
          theme: {
            color: "#D4AF37"
          }
        };

        const rzp = new window.Razorpay(options);
        rzp.open();
      }
    } catch (error) {
      console.error("Payment error:", error);
      toast.error("Failed to initiate payment");
    } finally {
      setPurchasing(null);
    }
  };

  const tierConfig = {
    short_story: {
      icon: <Eye className="w-6 h-6" />,
      featured: false,
      color: "gold"
    },
    deep_dive: {
      icon: <Fingerprint className="w-6 h-6" />,
      featured: false,
      color: "cyan"
    },
    connoisseur: {
      icon: <Sparkles className="w-6 h-6" />,
      featured: true,
      color: "gold"
    },
    pro_collector: {
      icon: <Crown className="w-6 h-6" />,
      featured: false,
      color: "gold"
    }
  };

  return (
    <div className="min-h-screen bg-[#050505]">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass-dark">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 lg:h-20">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-10 h-10 rounded bg-gradient-to-br from-[#D4AF37] to-[#B8962F] flex items-center justify-center">
                <span className="font-display text-[#050505] text-xl font-bold">E</span>
              </div>
              <span className="font-display text-xl text-[#F5F5F0] hidden sm:block">Emaira.Art</span>
            </Link>

            <div className="hidden md:flex items-center gap-8">
              <Link to="/gallery" className="nav-link text-sm font-medium">Gallery</Link>
              <Link to="/pricing" className="text-sm font-medium text-[#D4AF37]">Pricing</Link>
              {user && <Link to="/dashboard" className="nav-link text-sm font-medium">Dashboard</Link>}
            </div>

            <div className="hidden md:flex items-center gap-4">
              {user ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="flex items-center gap-2 text-[#F5F5F0]">
                      {user.picture ? (
                        <img src={user.picture} alt={user.name} className="w-8 h-8 rounded-full" />
                      ) : (
                        <User className="w-5 h-5" />
                      )}
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="bg-[#0a0a0a] border-[#1a1a1a]">
                    <DropdownMenuItem onClick={() => navigate('/dashboard')} className="text-[#F5F5F0] focus:bg-[#111] cursor-pointer">
                      <User className="w-4 h-4 mr-2" /> Dashboard
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={logout} className="text-[#F5F5F0] focus:bg-[#111] cursor-pointer">
                      <LogOut className="w-4 h-4 mr-2" /> Logout
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <Button onClick={login} className="btn-gold text-sm">Sign In</Button>
              )}
            </div>

            <button className="md:hidden text-[#F5F5F0]" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <div className="pt-24 lg:pt-32 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="text-center mb-12">
            <Button 
              variant="ghost" 
              onClick={() => navigate('/')} 
              className="text-[#A8A8A0] hover:text-[#F5F5F0] mb-4"
            >
              <ArrowLeft className="w-4 h-4 mr-2" /> Back to Home
            </Button>
            <Badge className="badge-gold mb-4">
              <Sparkles className="w-3 h-3 mr-1" /> Choose Your Experience
            </Badge>
            <h1 className="font-display text-4xl lg:text-5xl text-[#F5F5F0] mb-4">
              Subscription Plans
            </h1>
            <p className="text-[#A8A8A0] text-lg max-w-2xl mx-auto">
              From single story experiences to unlimited access with AI forensics—choose the plan that fits your passion.
            </p>
          </div>

          {/* Payment Method Toggle */}
          <div className="flex justify-center mb-8">
            <Tabs value={paymentMethod} onValueChange={setPaymentMethod}>
              <TabsList className="bg-[#111]">
                <TabsTrigger 
                  value="stripe" 
                  className="data-[state=active]:bg-[#D4AF37] data-[state=active]:text-[#050505]"
                >
                  <CreditCard className="w-4 h-4 mr-2" /> Card (Stripe)
                </TabsTrigger>
                <TabsTrigger 
                  value="razorpay"
                  className="data-[state=active]:bg-[#D4AF37] data-[state=active]:text-[#050505]"
                >
                  <CreditCard className="w-4 h-4 mr-2" /> Razorpay (India)
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>

          {/* Pricing Cards */}
          {loading ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="skeleton-dark h-96 rounded-lg"></div>
              ))}
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {tiers.map((tier) => {
                const config = tierConfig[tier.tier_id] || {};
                const isSubscription = tier.period === "year";

                return (
                  <div
                    key={tier.tier_id}
                    className={`tier-card rounded-lg p-6 flex flex-col ${config.featured ? 'featured' : ''}`}
                    data-testid={`tier-${tier.tier_id}`}
                  >
                    {config.featured && (
                      <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 badge-gold">
                        MOST POPULAR
                      </Badge>
                    )}

                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center mb-4 ${
                      config.color === 'cyan' 
                        ? 'bg-[#00F0FF]/10 text-[#00F0FF]' 
                        : 'bg-[#D4AF37]/10 text-[#D4AF37]'
                    }`}>
                      {config.icon}
                    </div>

                    <h3 className="font-display text-xl text-[#F5F5F0] mb-2">{tier.name}</h3>
                    
                    <div className="flex items-baseline gap-1 mb-4">
                      <span className="text-4xl font-display text-[#D4AF37]">${tier.price}</span>
                      <span className="text-[#666660]">/ {tier.period}</span>
                    </div>

                    <ul className="space-y-3 mb-6 flex-1">
                      {tier.features.map((feature, index) => (
                        <li key={index} className="flex items-start gap-2 text-sm">
                          <Check className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                            config.color === 'cyan' ? 'text-[#00F0FF]' : 'text-[#D4AF37]'
                          }`} />
                          <span className="text-[#A8A8A0]">{feature}</span>
                        </li>
                      ))}
                    </ul>

                    <Button
                      onClick={() => handleSubscribe(tier.tier_id)}
                      disabled={purchasing === tier.tier_id}
                      className={config.featured ? 'btn-gold' : 'btn-outline-gold'}
                      data-testid={`subscribe-${tier.tier_id}`}
                    >
                      {purchasing === tier.tier_id ? (
                        "Processing..."
                      ) : isSubscription ? (
                        "Subscribe Now"
                      ) : (
                        "Get Started"
                      )}
                    </Button>
                  </div>
                );
              })}
            </div>
          )}

          {/* Features Comparison */}
          <div className="mt-20">
            <h2 className="font-display text-2xl text-[#F5F5F0] text-center mb-8">
              What's Included
            </h2>
            
            <div className="grid md:grid-cols-3 gap-6">
              <div className="card-obsidian rounded-lg p-6">
                <div className="w-12 h-12 rounded-lg bg-[#D4AF37]/10 flex items-center justify-center mb-4">
                  <Eye className="w-6 h-6 text-[#D4AF37]" />
                </div>
                <h3 className="font-display text-lg text-[#F5F5F0] mb-2">Narrative Experience</h3>
                <p className="text-sm text-[#A8A8A0]">
                  Immersive cinematic journeys through art history. Witness artists' studios, historical moments, and the stories behind masterpieces.
                </p>
              </div>

              <div className="card-obsidian rounded-lg p-6">
                <div className="w-12 h-12 rounded-lg bg-[#00F0FF]/10 flex items-center justify-center mb-4">
                  <Fingerprint className="w-6 h-6 text-[#00F0FF]" />
                </div>
                <h3 className="font-display text-lg text-[#F5F5F0] mb-2">AI Forensics</h3>
                <p className="text-sm text-[#A8A8A0]">
                  Emaira AI analyzes pigments, signatures, and canvas weave to reveal authentication DNA and hidden details.
                </p>
              </div>

              <div className="card-obsidian rounded-lg p-6">
                <div className="w-12 h-12 rounded-lg bg-[#D4AF37]/10 flex items-center justify-center mb-4">
                  <Palette className="w-6 h-6 text-[#D4AF37]" />
                </div>
                <h3 className="font-display text-lg text-[#F5F5F0] mb-2">Knowledge Dashboard</h3>
                <p className="text-sm text-[#A8A8A0]">
                  Track your learned forensic markers, build expertise, and train yourself to see what experts see.
                </p>
              </div>
            </div>
          </div>

          {/* Trust Badges */}
          <div className="mt-16 text-center">
            <p className="text-[#666660] text-sm mb-4">Trusted payment processing</p>
            <div className="flex justify-center gap-8 items-center opacity-50">
              <span className="text-[#A8A8A0] font-mono text-sm">STRIPE</span>
              <span className="text-[#A8A8A0] font-mono text-sm">RAZORPAY</span>
              <span className="text-[#A8A8A0] font-mono text-sm">256-BIT SSL</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Pricing;
