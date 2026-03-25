import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth, API } from "@/App";
import { useTranslation } from "react-i18next";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import LanguageSelector from "@/components/LanguageSelector";
import { 
  Eye, 
  Fingerprint, 
  Play, 
  ChevronRight, 
  Sparkles,
  Shield,
  Palette,
  FileSignature,
  Grid3X3,
  Menu,
  X,
  User,
  LogOut
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const LandingPage = () => {
  const { user, login, logout, loading } = useAuth();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [featuredArtworks, setFeaturedArtworks] = useState([]);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    fetchFeaturedArtworks();
  }, []);

  const fetchFeaturedArtworks = async () => {
    try {
      const response = await axios.get(`${API}/artworks/?featured=true&limit=4`);
      setFeaturedArtworks(response.data);
    } catch (error) {
      console.error("Error fetching artworks:", error);
    }
  };

  const features = [
    {
      icon: <Eye className="w-6 h-6" />,
      title: "Narrative View",
      description: "Cinematic journeys through art history. Witness artists' studios and historic moments.",
      color: "gold"
    },
    {
      icon: <Fingerprint className="w-6 h-6" />,
      title: "AI Forensics",
      description: "Emaira deconstructs art with pigment mapping, signature analysis, and canvas weave detection.",
      color: "navy"
    },
    {
      icon: <Palette className="w-6 h-6" />,
      title: "Pigment Mapping",
      description: "Identify chemical makeup of colors used in specific eras for authentication.",
      color: "gold"
    },
    {
      icon: <FileSignature className="w-6 h-6" />,
      title: "Signature Authentication",
      description: "Comparative overlays of verified signatures with AI-powered analysis.",
      color: "navy"
    }
  ];

  return (
    <div className="min-h-screen bg-[#FAFAF8]">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass-light">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 lg:h-20">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-2" data-testid="logo">
              <div className="w-10 h-10 rounded bg-gradient-to-br from-[#D4AF37] to-[#B8962F] flex items-center justify-center">
                <span className="font-display text-white text-xl font-bold">E</span>
              </div>
              <span className="font-display text-xl text-[#1A1A18] hidden sm:block">Emaira.Art</span>
            </Link>

            {/* Desktop Nav */}
            <div className="hidden md:flex items-center gap-8">
              <Link to="/gallery" className="nav-link text-sm font-medium" data-testid="nav-gallery">{t('nav.gallery')}</Link>
              <Link to="/about" className="nav-link text-sm font-medium" data-testid="nav-about">{t('nav.about')}</Link>
              <Link to="/technology" className="nav-link text-sm font-medium" data-testid="nav-technology">{t('nav.technology')}</Link>
              <Link to="/events" className="nav-link text-sm font-medium" data-testid="nav-events">{t('nav.events')}</Link>
              <Link to="/pricing" className="nav-link text-sm font-medium" data-testid="nav-pricing">{t('nav.pricing')}</Link>
              {user && (
                <Link to="/dashboard" className="nav-link text-sm font-medium" data-testid="nav-dashboard">{t('nav.dashboard')}</Link>
              )}
            </div>

            {/* Auth Buttons */}
            <div className="hidden md:flex items-center gap-4">
              <LanguageSelector />
              {loading ? (
                <div className="w-8 h-8 border-2 border-[#B8962F] border-t-transparent rounded-full animate-spin"></div>
              ) : user ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="flex items-center gap-2 text-[#1A1A18]" data-testid="user-menu">
                      {user.picture ? (
                        <img src={user.picture} alt={user.name} className="w-8 h-8 rounded-full" />
                      ) : (
                        <User className="w-5 h-5" />
                      )}
                      <span className="hidden lg:block">{user.name}</span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="bg-white border-[#E8E8E0]">
                    <DropdownMenuItem onClick={() => navigate('/dashboard')} className="cursor-pointer">
                      <User className="w-4 h-4 mr-2" /> {t('nav.dashboard')}
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={logout} className="cursor-pointer" data-testid="logout-btn">
                      <LogOut className="w-4 h-4 mr-2" /> {t('nav.signOut')}
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <Button onClick={login} className="btn-gold text-sm" data-testid="login-btn">
                  {t('nav.signIn')}
                </Button>
              )}
            </div>

            {/* Mobile Menu Button */}
            <button 
              className="md:hidden text-[#1A1A18]"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              data-testid="mobile-menu-btn"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-[#E8E8E0] px-4 py-4">
            <div className="flex flex-col gap-4">
              <Link to="/gallery" className="text-[#1A1A18] py-2">Gallery</Link>
              <Link to="/about" className="text-[#1A1A18] py-2">About</Link>
              <Link to="/technology" className="text-[#1A1A18] py-2">Technology</Link>
              <Link to="/events" className="text-[#1A1A18] py-2">Events</Link>
              <Link to="/pricing" className="text-[#1A1A18] py-2">Pricing</Link>
              {user && <Link to="/dashboard" className="text-[#1A1A18] py-2">Dashboard</Link>}
              {user ? (
                <Button onClick={logout} variant="outline" className="border-[#B8962F] text-[#B8962F]">
                  Logout
                </Button>
              ) : (
                <Button onClick={login} className="btn-gold">Sign In</Button>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="hero-gradient min-h-screen flex items-center pt-20 lg:pt-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-24">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
            {/* Left Content */}
            <div className="space-y-8 animate-fade-in-up">
              <div className="space-y-4">
                <Badge className="badge-gold" data-testid="hero-badge">
                  <Sparkles className="w-3 h-3 mr-1" /> VR Art Experience
                </Badge>
                <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl xl:text-7xl text-[#1A1A18] leading-tight">
                  Where Art Meets
                  <span className="block text-gold-gradient">AI Forensics</span>
                </h1>
                <p className="text-base lg:text-lg text-[#4A4A45] max-w-lg font-body">
                  Emaira.Art doesn't just display art—she deconstructs it. Journey through provenance, 
                  authentication DNA, and the hidden stories within masterpieces.
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <Button 
                  onClick={() => navigate('/gallery')} 
                  className="btn-gold text-base"
                  data-testid="explore-gallery-btn"
                >
                  <Play className="w-4 h-4 mr-2" /> Explore Gallery
                </Button>
                <Button 
                  onClick={() => navigate('/pricing')} 
                  variant="outline" 
                  className="btn-outline-gold text-base"
                  data-testid="view-pricing-btn"
                >
                  View Pricing <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              </div>

              {/* Trust Indicators */}
              <div className="flex items-center gap-6 pt-4">
                <div className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-[#B8962F]" />
                  <span className="text-sm text-[#4A4A45]">Authentication DNA</span>
                </div>
                <div className="flex items-center gap-2">
                  <Grid3X3 className="w-5 h-5 text-[#1A365D]" />
                  <span className="text-sm text-[#4A4A45]">Canvas Analysis</span>
                </div>
              </div>
            </div>

            {/* Right - Featured Artwork Preview */}
            <div className="relative" data-testid="hero-artwork">
              <div className="relative aspect-[4/5] rounded-lg overflow-hidden card-ivory shadow-xl">
                <img 
                  src="https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=800"
                  alt="Featured Artwork"
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#1A1A18]/70 via-transparent to-transparent"></div>
                
                {/* Forensic Overlay */}
                <div className="absolute inset-0 border border-[#1A365D]/20 rounded-lg pointer-events-none">
                  <div className="absolute top-4 left-4 flex items-center gap-2">
                    <span className="badge-forensic flex items-center gap-1">
                      <Fingerprint className="w-3 h-3" /> Forensic Mode
                    </span>
                  </div>
                  
                  {/* Scan Lines */}
                  <div className="absolute top-1/4 left-0 right-0 h-px bg-[#1A365D]/20"></div>
                  <div className="absolute top-1/2 left-0 right-0 h-px bg-[#1A365D]/20"></div>
                  <div className="absolute top-3/4 left-0 right-0 h-px bg-[#1A365D]/20"></div>
                </div>

                {/* Info Card */}
                <div className="absolute bottom-4 left-4 right-4 glass-light rounded-lg p-4">
                  <p className="font-display text-lg text-[#1A1A18]">The Starry Night</p>
                  <p className="text-sm text-[#4A4A45]">Vincent van Gogh, 1889</p>
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-xs text-[#1A365D] font-mono">AUTHENTICITY: 98.7%</span>
                  </div>
                </div>
              </div>

              {/* Decorative Elements */}
              <div className="absolute -top-4 -right-4 w-24 h-24 border border-[#B8962F]/20 rounded-lg"></div>
              <div className="absolute -bottom-4 -left-4 w-32 h-32 border border-[#1A365D]/20 rounded-lg"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 lg:py-32 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Badge className="badge-gold mb-4">
              <Eye className="w-3 h-3 mr-1" /> Dual Experience
            </Badge>
            <h2 className="font-display text-3xl lg:text-4xl text-[#1A1A18] mb-4">
              Two Ways to Experience Art
            </h2>
            <p className="text-[#4A4A45] max-w-2xl mx-auto">
              Toggle between immersive storytelling and scientific authentication—all in VR.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <div 
                key={index}
                className="feature-card p-6 rounded-lg group"
                style={{ animationDelay: `${index * 100}ms` }}
                data-testid={`feature-card-${index}`}
              >
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center mb-4 ${
                  feature.color === 'gold' 
                    ? 'bg-[#B8962F]/10 text-[#B8962F]' 
                    : 'bg-[#1A365D]/10 text-[#1A365D]'
                }`}>
                  {feature.icon}
                </div>
                <h3 className="font-display text-lg text-[#1A1A18] mb-2">{feature.title}</h3>
                <p className="text-sm text-[#4A4A45]">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Artworks */}
      <section className="py-20 lg:py-32 bg-[#F5F5F0]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-12">
            <div>
              <h2 className="font-display text-3xl lg:text-4xl text-[#1A1A18] mb-2">
                Featured Masterpieces
              </h2>
              <p className="text-[#4A4A45]">Begin your journey with these iconic works</p>
            </div>
            <Button 
              onClick={() => navigate('/gallery')} 
              variant="outline" 
              className="btn-outline-gold"
              data-testid="view-all-btn"
            >
              View All <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {featuredArtworks.length > 0 ? (
              featuredArtworks.map((artwork) => (
                <Link 
                  key={artwork.artwork_id} 
                  to={`/story/${artwork.story_id}`}
                  className="artwork-card rounded-lg overflow-hidden aspect-[3/4] relative group shadow-lg"
                  data-testid={`artwork-${artwork.artwork_id}`}
                >
                  <img 
                    src={artwork.thumbnail_url || artwork.image_url}
                    alt={artwork.title}
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                  />
                  <div className="artwork-card-content text-white">
                    <Badge className="bg-white/20 text-white border-0 backdrop-blur-sm mb-2">{artwork.period}</Badge>
                    <h3 className="font-display text-lg">{artwork.title}</h3>
                    <p className="text-sm text-white/80">{artwork.artist}</p>
                  </div>
                </Link>
              ))
            ) : (
              // Skeleton loading
              [...Array(4)].map((_, i) => (
                <div key={i} className="skeleton-light rounded-lg aspect-[3/4]"></div>
              ))
            )}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 lg:py-32 hero-gradient">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="font-display text-3xl lg:text-5xl text-[#1A1A18] mb-6">
            Ready to See Art<br />
            <span className="text-gold-gradient">Like Never Before?</span>
          </h2>
          <p className="text-[#4A4A45] text-lg mb-8 max-w-2xl mx-auto">
            Join Emaira and discover the hidden DNA within every masterpiece. 
            Start with a single story or unlock unlimited access.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button onClick={login} className="btn-gold text-base px-8" data-testid="cta-start-btn">
              Start Your Journey
            </Button>
            <Button 
              onClick={() => navigate('/pricing')} 
              variant="outline" 
              className="btn-outline-gold text-base px-8"
            >
              Explore Plans
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t border-[#E8E8E0] py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded bg-gradient-to-br from-[#D4AF37] to-[#B8962F] flex items-center justify-center">
                <span className="font-display text-white text-sm font-bold">E</span>
              </div>
              <span className="font-display text-lg text-[#1A1A18]">Emaira.Art</span>
            </div>
            <div className="flex items-center gap-6 text-sm text-[#4A4A45]">
              <Link to="/gallery" className="hover:text-[#B8962F] transition-colors">Gallery</Link>
              <Link to="/about" className="hover:text-[#B8962F] transition-colors">About</Link>
              <Link to="/technology" className="hover:text-[#B8962F] transition-colors">Technology</Link>
              <Link to="/events" className="hover:text-[#B8962F] transition-colors">Events</Link>
              <Link to="/pricing" className="hover:text-[#B8962F] transition-colors">Pricing</Link>
              <span>© 2026 Emaira.Art</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
