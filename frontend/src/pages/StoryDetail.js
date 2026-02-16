import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useAuth, API } from "@/App";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { 
  ArrowLeft, 
  Play, 
  Clock, 
  MapPin, 
  Calendar,
  Fingerprint,
  Palette,
  FileSignature,
  Grid3X3,
  Lock,
  Check,
  User,
  Menu,
  X,
  LogOut
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const StoryDetail = () => {
  const { storyId } = useParams();
  const { user, login, logout } = useAuth();
  const navigate = useNavigate();
  const [story, setStory] = useState(null);
  const [artwork, setArtwork] = useState(null);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    fetchStoryAndArtwork();
  }, [storyId]);

  const fetchStoryAndArtwork = async () => {
    try {
      const storyResponse = await axios.get(`${API}/stories/${storyId}`, {
        withCredentials: true
      });
      setStory(storyResponse.data);

      if (storyResponse.data.artwork_id) {
        const artworkResponse = await axios.get(`${API}/artworks/${storyResponse.data.artwork_id}`);
        setArtwork(artworkResponse.data);
      }
    } catch (error) {
      console.error("Error fetching story:", error);
      toast.error("Failed to load story");
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (accessType) => {
    if (!user) {
      login();
      return;
    }

    setPurchasing(true);
    try {
      const response = await axios.post(
        `${API}/payments/stripe/checkout`,
        {
          story_id: storyId,
          access_type: accessType,
          origin_url: window.location.origin
        },
        { withCredentials: true }
      );

      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (error) {
      console.error("Payment error:", error);
      toast.error("Failed to initiate payment");
    } finally {
      setPurchasing(false);
    }
  };

  const handleStartExperience = () => {
    if (!user) {
      login();
      return;
    }
    navigate(`/experience/${storyId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-[#D4AF37] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-[#A8A8A0]">Loading story...</p>
        </div>
      </div>
    );
  }

  if (!story || !artwork) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <div className="text-center">
          <p className="text-[#A8A8A0] mb-4">Story not found</p>
          <Button onClick={() => navigate('/gallery')} className="btn-gold">
            Back to Gallery
          </Button>
        </div>
      </div>
    );
  }

  const hasAccess = story.has_access;

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
              <Link to="/pricing" className="nav-link text-sm font-medium">Pricing</Link>
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

      {/* Hero Section */}
      <div className="relative min-h-[60vh] flex items-end">
        <div className="absolute inset-0">
          <img 
            src={artwork.image_url}
            alt={artwork.title}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#050505] via-[#050505]/70 to-transparent"></div>
        </div>

        <div className="relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12 pt-32">
          <Button 
            variant="ghost" 
            onClick={() => navigate('/gallery')} 
            className="text-[#A8A8A0] hover:text-[#F5F5F0] mb-6 -ml-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" /> Back to Gallery
          </Button>

          <div className="flex flex-wrap gap-2 mb-4">
            <Badge className="badge-gold">{artwork.period}</Badge>
            <Badge className="badge-forensic">
              <Fingerprint className="w-3 h-3 mr-1" /> AI Forensics
            </Badge>
          </div>

          <h1 className="font-display text-4xl lg:text-5xl xl:text-6xl text-[#F5F5F0] mb-4" data-testid="story-title">
            {story.title}
          </h1>

          <div className="flex flex-wrap items-center gap-4 text-[#A8A8A0] mb-6">
            <span className="flex items-center gap-2">
              <Calendar className="w-4 h-4" /> {artwork.year}
            </span>
            <span className="flex items-center gap-2">
              <MapPin className="w-4 h-4" /> {artwork.location}
            </span>
            <span className="flex items-center gap-2">
              <Clock className="w-4 h-4" /> {story.duration_minutes} min experience
            </span>
          </div>

          <p className="text-lg text-[#A8A8A0] max-w-2xl">
            {story.description}
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Artwork Details */}
            <div className="card-obsidian rounded-lg p-6">
              <h2 className="font-display text-2xl text-[#F5F5F0] mb-4">About the Artwork</h2>
              <div className="grid sm:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-[#666660]">Artist</span>
                  <p className="text-[#F5F5F0]">{artwork.artist}</p>
                </div>
                <div>
                  <span className="text-[#666660]">Year</span>
                  <p className="text-[#F5F5F0]">{artwork.year}</p>
                </div>
                <div>
                  <span className="text-[#666660]">Medium</span>
                  <p className="text-[#F5F5F0]">{artwork.medium}</p>
                </div>
                <div>
                  <span className="text-[#666660]">Dimensions</span>
                  <p className="text-[#F5F5F0]">{artwork.dimensions}</p>
                </div>
              </div>
              <p className="text-[#A8A8A0] mt-4">{artwork.description}</p>
            </div>

            {/* Provenance */}
            {artwork.provenance && artwork.provenance.length > 0 && (
              <div className="card-obsidian rounded-lg p-6">
                <h2 className="font-display text-2xl text-[#F5F5F0] mb-4">Provenance</h2>
                <div className="space-y-4">
                  {artwork.provenance.map((item, index) => (
                    <div key={index} className="flex gap-4">
                      <div className="w-16 text-[#D4AF37] font-mono text-sm">{item.year}</div>
                      <div className="flex-1 text-[#A8A8A0]">{item.event}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Forensic Features Preview */}
            <div className="card-obsidian rounded-lg p-6">
              <h2 className="font-display text-2xl text-[#F5F5F0] mb-4">
                Forensic Analysis Features
              </h2>
              <div className="grid sm:grid-cols-3 gap-4">
                <div className="p-4 bg-[#00F0FF]/5 border border-[#00F0FF]/20 rounded-lg">
                  <Palette className="w-8 h-8 text-[#00F0FF] mb-3" />
                  <h3 className="font-display text-[#F5F5F0] mb-1">Pigment Mapping</h3>
                  <p className="text-xs text-[#A8A8A0]">Chemical composition analysis</p>
                </div>
                <div className="p-4 bg-[#00F0FF]/5 border border-[#00F0FF]/20 rounded-lg">
                  <FileSignature className="w-8 h-8 text-[#00F0FF] mb-3" />
                  <h3 className="font-display text-[#F5F5F0] mb-1">Signature Auth</h3>
                  <p className="text-xs text-[#A8A8A0]">Comparative overlays</p>
                </div>
                <div className="p-4 bg-[#00F0FF]/5 border border-[#00F0FF]/20 rounded-lg">
                  <Grid3X3 className="w-8 h-8 text-[#00F0FF] mb-3" />
                  <h3 className="font-display text-[#F5F5F0] mb-1">Canvas Analysis</h3>
                  <p className="text-xs text-[#A8A8A0]">Weave density mapping</p>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar - Purchase Options */}
          <div className="lg:col-span-1">
            <div className="sticky top-24 space-y-4">
              {hasAccess ? (
                <div className="card-obsidian rounded-lg p-6 border-[#D4AF37]">
                  <div className="flex items-center gap-2 text-[#D4AF37] mb-4">
                    <Check className="w-5 h-5" />
                    <span className="font-medium">Access Granted</span>
                  </div>
                  <Button 
                    onClick={handleStartExperience}
                    className="w-full btn-gold text-base"
                    data-testid="start-experience-btn"
                  >
                    <Play className="w-4 h-4 mr-2" /> Start Experience
                  </Button>
                </div>
              ) : (
                <>
                  {/* Narrative Only */}
                  <div className="card-obsidian rounded-lg p-6">
                    <h3 className="font-display text-xl text-[#F5F5F0] mb-2">The Short Story</h3>
                    <p className="text-sm text-[#A8A8A0] mb-4">
                      3-minute narrative VR experience through the artwork's history
                    </p>
                    <div className="flex items-baseline gap-1 mb-4">
                      <span className="text-3xl font-display text-[#D4AF37]">${story.price_narrative}</span>
                      <span className="text-[#666660]">/ story</span>
                    </div>
                    <ul className="space-y-2 mb-6 text-sm text-[#A8A8A0]">
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-[#D4AF37]" /> Full narrative experience
                      </li>
                      <li className="flex items-center gap-2">
                        <Lock className="w-4 h-4 text-[#666660]" /> Forensic view locked
                      </li>
                    </ul>
                    <Button 
                      onClick={() => handlePurchase("narrative")}
                      disabled={purchasing}
                      className="w-full btn-outline-gold"
                      data-testid="buy-narrative-btn"
                    >
                      {purchasing ? "Processing..." : "Get Narrative Access"}
                    </Button>
                  </div>

                  {/* Deep Dive */}
                  <div className="card-obsidian rounded-lg p-6 border-[#D4AF37] relative overflow-hidden">
                    <div className="absolute top-0 right-0 bg-[#D4AF37] text-[#050505] text-xs font-bold px-3 py-1">
                      RECOMMENDED
                    </div>
                    <h3 className="font-display text-xl text-[#F5F5F0] mb-2">The Deep Dive</h3>
                    <p className="text-sm text-[#A8A8A0] mb-4">
                      Complete experience with AI forensic analysis
                    </p>
                    <div className="flex items-baseline gap-1 mb-4">
                      <span className="text-3xl font-display text-[#D4AF37]">${story.price_full}</span>
                      <span className="text-[#666660]">/ story</span>
                    </div>
                    <ul className="space-y-2 mb-6 text-sm text-[#A8A8A0]">
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-[#D4AF37]" /> Full narrative experience
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-[#00F0FF]" /> Complete forensic view
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-[#00F0FF]" /> AI pigment analysis
                      </li>
                      <li className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-[#00F0FF]" /> Signature authentication
                      </li>
                    </ul>
                    <Button 
                      onClick={() => handlePurchase("full")}
                      disabled={purchasing}
                      className="w-full btn-gold"
                      data-testid="buy-full-btn"
                    >
                      {purchasing ? "Processing..." : "Get Full Access"}
                    </Button>
                  </div>

                  {/* Subscription Upsell */}
                  <div className="glass-gold rounded-lg p-4 text-center">
                    <p className="text-sm text-[#D4AF37] mb-2">Want unlimited access?</p>
                    <Button 
                      onClick={() => navigate('/pricing')}
                      variant="link"
                      className="text-[#F5F5F0] hover:text-[#D4AF37]"
                    >
                      View Subscription Plans →
                    </Button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StoryDetail;
