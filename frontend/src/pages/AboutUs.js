import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/App";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Footer from "@/components/Footer";
import {
  ArrowLeft,
  Users,
  Target,
  Award,
  Globe,
  Heart,
  Sparkles,
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

const AboutUs = () => {
  const { user, login, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const team = [
    {
      name: "Dr. Elena Vasquez",
      role: "Founder & Chief Art Historian",
      bio: "Former curator at the Prado Museum with 20+ years in art authentication.",
      image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300"
    },
    {
      name: "Marcus Chen",
      role: "CTO & AI Research Lead",
      bio: "PhD in Computer Vision from MIT, pioneering AI in cultural heritage preservation.",
      image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300"
    },
    {
      name: "Isabelle Fontaine",
      role: "Creative Director",
      bio: "Award-winning VR experience designer, previously at Oculus Studios.",
      image: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=300"
    },
    {
      name: "Dr. Raj Patel",
      role: "Head of Forensic Analysis",
      bio: "Leading expert in pigment spectroscopy and canvas fiber analysis.",
      image: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=300"
    }
  ];

  const values = [
    {
      icon: <Target className="w-6 h-6" />,
      title: "Precision",
      description: "Every analysis meets museum-grade authentication standards."
    },
    {
      icon: <Heart className="w-6 h-6" />,
      title: "Passion",
      description: "We believe art education should be accessible and captivating."
    },
    {
      icon: <Globe className="w-6 h-6" />,
      title: "Global Reach",
      description: "Partnering with galleries and collectors across 40+ countries."
    },
    {
      icon: <Award className="w-6 h-6" />,
      title: "Excellence",
      description: "Recognized by the International Art Authentication Council."
    }
  ];

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
              <Link to="/about" className="text-sm font-medium text-[#B8962F]">About</Link>
              <Link to="/technology" className="nav-link text-sm font-medium">Technology</Link>
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

          <div className="max-w-3xl">
            <Badge className="badge-gold mb-4">
              <Sparkles className="w-3 h-3 mr-1" /> Our Story
            </Badge>
            <h1 className="font-display text-4xl lg:text-5xl xl:text-6xl text-[#1A1A18] mb-6">
              Redefining How the World
              <span className="block text-gold-gradient">Experiences Art</span>
            </h1>
            <p className="text-lg text-[#4A4A45] leading-relaxed">
              Founded in 2023, Emaira.Art emerged from a simple belief: that the stories behind 
              masterpieces are as valuable as the art itself. We combine cutting-edge AI forensics 
              with immersive VR storytelling to democratize art expertise.
            </p>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <Badge className="badge-forensic mb-4">
                <Target className="w-3 h-3 mr-1" /> Our Mission
              </Badge>
              <h2 className="font-display text-3xl lg:text-4xl text-[#1A1A18] mb-6">
                Making Art Authentication Accessible to Everyone
              </h2>
              <p className="text-[#4A4A45] mb-6">
                For centuries, understanding the authenticity and provenance of art required years 
                of specialized training or expensive consultations. Emaira.Art changes that paradigm.
              </p>
              <p className="text-[#4A4A45] mb-6">
                Our AI-powered platform, guided by the expertise of Emaira—your personal art forensics 
                specialist—teaches you to see what experts see: the subtle brushstrokes, the chemical 
                signatures of pigments, the weave patterns that tell a story spanning centuries.
              </p>
              <div className="flex items-center gap-4 pt-4">
                <div className="text-center">
                  <p className="text-3xl font-display text-[#B8962F]">500+</p>
                  <p className="text-sm text-[#8A8A80]">Masterpieces Analyzed</p>
                </div>
                <div className="w-px h-12 bg-[#E8E8E0]"></div>
                <div className="text-center">
                  <p className="text-3xl font-display text-[#B8962F]">40+</p>
                  <p className="text-sm text-[#8A8A80]">Partner Museums</p>
                </div>
                <div className="w-px h-12 bg-[#E8E8E0]"></div>
                <div className="text-center">
                  <p className="text-3xl font-display text-[#B8962F]">98.7%</p>
                  <p className="text-sm text-[#8A8A80]">Authentication Accuracy</p>
                </div>
              </div>
            </div>
            <div className="relative">
              <img 
                src="https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=600"
                alt="Art Gallery"
                className="rounded-lg shadow-xl"
              />
              <div className="absolute -bottom-6 -left-6 w-48 h-48 border-2 border-[#B8962F]/30 rounded-lg"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-20 bg-[#F5F5F0]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Badge className="badge-gold mb-4">Our Values</Badge>
            <h2 className="font-display text-3xl lg:text-4xl text-[#1A1A18]">
              What Drives Us
            </h2>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {values.map((value, index) => (
              <div key={index} className="feature-card p-6 rounded-lg text-center" data-testid={`value-${index}`}>
                <div className="w-14 h-14 rounded-full bg-[#B8962F]/10 flex items-center justify-center mx-auto mb-4 text-[#B8962F]">
                  {value.icon}
                </div>
                <h3 className="font-display text-lg text-[#1A1A18] mb-2">{value.title}</h3>
                <p className="text-sm text-[#4A4A45]">{value.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Badge className="badge-forensic mb-4">
              <Users className="w-3 h-3 mr-1" /> Leadership
            </Badge>
            <h2 className="font-display text-3xl lg:text-4xl text-[#1A1A18]">
              Meet Our Team
            </h2>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {team.map((member, index) => (
              <div key={index} className="text-center group" data-testid={`team-member-${index}`}>
                <div className="relative mb-4 overflow-hidden rounded-lg">
                  <img 
                    src={member.image}
                    alt={member.name}
                    className="w-full aspect-square object-cover transition-transform duration-500 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-[#1A1A18]/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                </div>
                <h3 className="font-display text-lg text-[#1A1A18]">{member.name}</h3>
                <p className="text-sm text-[#B8962F] mb-2">{member.role}</p>
                <p className="text-sm text-[#4A4A45]">{member.bio}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 hero-gradient">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="font-display text-3xl lg:text-4xl text-[#1A1A18] mb-6">
            Ready to See Art Through New Eyes?
          </h2>
          <p className="text-[#4A4A45] text-lg mb-8">
            Join thousands of art lovers discovering the hidden stories within masterpieces.
          </p>
          <Button onClick={() => navigate('/gallery')} className="btn-gold text-base px-8">
            Explore the Gallery
          </Button>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default AboutUs;
