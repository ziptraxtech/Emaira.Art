import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/App";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  ArrowLeft,
  Cpu,
  Eye,
  Fingerprint,
  Palette,
  FileSignature,
  Grid3X3,
  Sparkles,
  Brain,
  Layers,
  Scan,
  User,
  Menu,
  X,
  LogOut,
  ChevronRight
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const OurTechnology = () => {
  const { user, login, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeFeature, setActiveFeature] = useState("pigment");

  const technologies = [
    {
      id: "pigment",
      icon: <Palette className="w-6 h-6" />,
      title: "Pigment Spectroscopy",
      subtitle: "Chemical Composition Analysis",
      description: "Our AI analyzes the molecular structure of pigments, identifying era-specific materials like lapis lazuli, vermillion, and lead white. Each pigment has a unique chemical signature that reveals when and where it was likely made.",
      features: [
        "X-ray fluorescence simulation",
        "Infrared reflectography mapping",
        "UV fluorescence detection",
        "Historical pigment database matching"
      ],
      accuracy: "99.2%"
    },
    {
      id: "signature",
      icon: <FileSignature className="w-6 h-6" />,
      title: "Signature Authentication",
      subtitle: "Brushwork Pattern Recognition",
      description: "Using advanced computer vision, Emaira analyzes the pressure, speed, and style of brushstrokes in signatures. We compare against verified exemplars to detect forgeries or confirm authenticity.",
      features: [
        "Pressure point analysis",
        "Stroke velocity mapping",
        "Comparative overlay system",
        "Historical signature database"
      ],
      accuracy: "97.8%"
    },
    {
      id: "canvas",
      icon: <Grid3X3 className="w-6 h-6" />,
      title: "Canvas Weave Analysis",
      subtitle: "Support Structure Examination",
      description: "The weave pattern, thread count, and fiber composition of canvas tell a story of origin. Our AI measures these details at microscopic levels to date and authenticate artworks.",
      features: [
        "Thread density measurement",
        "Fiber type identification",
        "Weave pattern classification",
        "Age estimation algorithms"
      ],
      accuracy: "96.5%"
    },
    {
      id: "provenance",
      icon: <Layers className="w-6 h-6" />,
      title: "Provenance Tracking",
      subtitle: "Ownership History Verification",
      description: "Combining historical records, exhibition catalogs, and sale documentation, our system traces the complete journey of an artwork from creation to present day.",
      features: [
        "Historical document analysis",
        "Exhibition record matching",
        "Auction database integration",
        "Blockchain verification ready"
      ],
      accuracy: "94.3%"
    }
  ];

  const activetech = technologies.find(t => t.id === activeFeature);

  return (
    <div className="min-h-screen bg-[#FAFAF8]">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass-light">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 lg:h-20">
            <Link to="/" className="flex items-center gap-2" data-testid="logo">
              <div className="w-10 h-10 rounded bg-gradient-to-br from-[#D4AF37] to-[#B8962F] flex items-center justify-center">
                <span className="font-display text-white text-xl font-bold">E</span>
              </div>
              <span className="font-display text-xl text-[#1A1A18] hidden sm:block">Emaira.Art</span>
            </Link>

            <div className="hidden md:flex items-center gap-8">
              <Link to="/gallery" className="nav-link text-sm font-medium">Gallery</Link>
              <Link to="/about" className="nav-link text-sm font-medium">About</Link>
              <Link to="/technology" className="text-sm font-medium text-[#B8962F]">Technology</Link>
              <Link to="/events" className="nav-link text-sm font-medium">Events</Link>
              <Link to="/pricing" className="nav-link text-sm font-medium">Pricing</Link>
            </div>

            <div className="hidden md:flex items-center gap-4">
              {user ? (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="flex items-center gap-2 text-[#1A1A18]">
                      {user.picture ? (
                        <img src={user.picture} alt={user.name} className="w-8 h-8 rounded-full" />
                      ) : (
                        <User className="w-5 h-5" />
                      )}
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="bg-white border-[#E8E8E0]">
                    <DropdownMenuItem onClick={() => navigate('/dashboard')} className="cursor-pointer">
                      <User className="w-4 h-4 mr-2" /> Dashboard
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={logout} className="cursor-pointer">
                      <LogOut className="w-4 h-4 mr-2" /> Logout
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <Button onClick={login} className="btn-gold text-sm">Sign In</Button>
              )}
            </div>

            <button className="md:hidden text-[#1A1A18]" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-16 hero-gradient">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Button 
            variant="ghost" 
            onClick={() => navigate('/')} 
            className="text-[#4A4A45] hover:text-[#1A1A18] mb-6 -ml-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" /> Back to Home
          </Button>

          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <Badge className="badge-forensic mb-4">
                <Cpu className="w-3 h-3 mr-1" /> Our Technology
              </Badge>
              <h1 className="font-display text-4xl lg:text-5xl text-[#1A1A18] mb-6">
                AI-Powered Art
                <span className="block text-gold-gradient">Forensics</span>
              </h1>
              <p className="text-lg text-[#4A4A45] leading-relaxed mb-8">
                Emaira combines cutting-edge artificial intelligence with centuries of art expertise. 
                Our proprietary algorithms analyze artworks at a level previously possible only in 
                specialized conservation laboratories.
              </p>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 text-[#1A365D]">
                  <Brain className="w-5 h-5" />
                  <span className="text-sm font-medium">Gemini AI Powered</span>
                </div>
                <div className="flex items-center gap-2 text-[#B8962F]">
                  <Scan className="w-5 h-5" />
                  <span className="text-sm font-medium">Real-time Analysis</span>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="aspect-square bg-white rounded-lg shadow-xl p-8 border border-[#E8E8E0]">
                <div className="w-full h-full relative">
                  <img 
                    src="https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=500"
                    alt="Analysis Preview"
                    className="w-full h-full object-cover rounded"
                  />
                  {/* Overlay grid */}
                  <div className="absolute inset-0 grid grid-cols-4 grid-rows-4 pointer-events-none">
                    {[...Array(16)].map((_, i) => (
                      <div key={i} className="border border-[#1A365D]/10"></div>
                    ))}
                  </div>
                  {/* Scan line */}
                  <div className="absolute inset-0 overflow-hidden">
                    <div className="absolute left-0 right-0 h-0.5 bg-[#1A365D] animate-pulse" style={{ top: '40%' }}></div>
                  </div>
                  {/* Analysis badge */}
                  <div className="absolute top-4 left-4 bg-white/90 backdrop-blur px-3 py-1 rounded text-xs font-mono text-[#1A365D]">
                    ANALYZING...
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Deep Dive */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <Badge className="badge-gold mb-4">
              <Fingerprint className="w-3 h-3 mr-1" /> Core Technologies
            </Badge>
            <h2 className="font-display text-3xl lg:text-4xl text-[#1A1A18]">
              How Emaira Authenticates Art
            </h2>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Feature Selector */}
            <div className="space-y-3">
              {technologies.map((tech) => (
                <button
                  key={tech.id}
                  onClick={() => setActiveFeature(tech.id)}
                  className={`w-full text-left p-4 rounded-lg transition-all ${
                    activeFeature === tech.id 
                      ? 'bg-[#1A365D] text-white' 
                      : 'bg-[#F5F5F0] text-[#1A1A18] hover:bg-[#E8E8E0]'
                  }`}
                  data-testid={`tech-${tech.id}`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      activeFeature === tech.id ? 'bg-white/20' : 'bg-[#B8962F]/10 text-[#B8962F]'
                    }`}>
                      {tech.icon}
                    </div>
                    <div>
                      <p className="font-display">{tech.title}</p>
                      <p className={`text-xs ${activeFeature === tech.id ? 'text-white/70' : 'text-[#8A8A80]'}`}>
                        {tech.subtitle}
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>

            {/* Feature Detail */}
            <div className="lg:col-span-2 card-ivory rounded-lg p-8">
              {activeFeature && activeFeature && (
                <div className="animate-fade-in-up">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="font-display text-2xl text-[#1A1A18]">{activeFeature && activeFeature && technologies.find(t => t.id === activeFeature)?.title}</h3>
                    <Badge className="badge-forensic">
                      {activeFeature && activeFeature && technologies.find(t => t.id === activeFeature)?.accuracy} Accuracy
                    </Badge>
                  </div>
                  <p className="text-[#4A4A45] mb-6">
                    {activeFeature && activeFeature && technologies.find(t => t.id === activeFeature)?.description}
                  </p>
                  <h4 className="font-medium text-[#1A1A18] mb-3">Key Capabilities:</h4>
                  <ul className="grid sm:grid-cols-2 gap-3">
                    {activeFeature && activeFeature && technologies.find(t => t.id === activeFeature)?.features.map((feature, index) => (
                      <li key={index} className="flex items-center gap-2 text-sm text-[#4A4A45]">
                        <div className="w-1.5 h-1.5 rounded-full bg-[#B8962F]"></div>
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-[#F5F5F0]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Badge className="badge-gold mb-4">Process</Badge>
            <h2 className="font-display text-3xl lg:text-4xl text-[#1A1A18]">
              The Analysis Journey
            </h2>
          </div>

          <div className="grid md:grid-cols-4 gap-8">
            {[
              { step: "01", title: "Upload", desc: "Submit high-resolution artwork images" },
              { step: "02", title: "Scan", desc: "AI performs multi-spectral analysis" },
              { step: "03", title: "Compare", desc: "Cross-reference with historical databases" },
              { step: "04", title: "Report", desc: "Receive detailed authentication report" }
            ].map((item, index) => (
              <div key={index} className="text-center relative">
                <div className="w-16 h-16 rounded-full bg-[#B8962F]/10 flex items-center justify-center mx-auto mb-4">
                  <span className="font-display text-2xl text-[#B8962F]">{item.step}</span>
                </div>
                <h3 className="font-display text-lg text-[#1A1A18] mb-2">{item.title}</h3>
                <p className="text-sm text-[#4A4A45]">{item.desc}</p>
                {index < 3 && (
                  <ChevronRight className="hidden md:block absolute top-8 -right-4 w-6 h-6 text-[#E8E8E0]" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 hero-gradient">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="font-display text-3xl lg:text-4xl text-[#1A1A18] mb-6">
            Experience AI Art Forensics
          </h2>
          <p className="text-[#4A4A45] text-lg mb-8">
            See our technology in action with a free story preview.
          </p>
          <Button onClick={() => navigate('/gallery')} className="btn-gold text-base px-8">
            Try It Now
          </Button>
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
              <Link to="/about" className="hover:text-[#B8962F] transition-colors">About</Link>
              <Link to="/technology" className="hover:text-[#B8962F] transition-colors">Technology</Link>
              <Link to="/events" className="hover:text-[#B8962F] transition-colors">Events</Link>
              <span>© 2026 Emaira.Art</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default OurTechnology;
