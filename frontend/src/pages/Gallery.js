import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth, API } from "@/App";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { 
  Search, 
  Filter, 
  ArrowLeft,
  Play,
  Clock,
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

const Gallery = () => {
  const { user, login, logout } = useAuth();
  const navigate = useNavigate();
  const [artworks, setArtworks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [periodFilter, setPeriodFilter] = useState("all");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    fetchArtworks();
  }, []);

  const fetchArtworks = async () => {
    try {
      const response = await axios.get(`${API}/artworks/?limit=20`);
      setArtworks(response.data);
    } catch (error) {
      console.error("Error fetching artworks:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredArtworks = artworks.filter(artwork => {
    const matchesSearch = artwork.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         artwork.artist.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesPeriod = periodFilter === "all" || artwork.period === periodFilter;
    return matchesSearch && matchesPeriod;
  });

  const periods = [...new Set(artworks.map(a => a.period))];

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
              <Link to="/gallery" className="text-sm font-medium text-[#B8962F]">Gallery</Link>
              <Link to="/about" className="nav-link text-sm font-medium">About</Link>
              <Link to="/technology" className="nav-link text-sm font-medium">Technology</Link>
              <Link to="/events" className="nav-link text-sm font-medium">Events</Link>
              <Link to="/pricing" className="nav-link text-sm font-medium">Pricing</Link>
              {user && <Link to="/dashboard" className="nav-link text-sm font-medium">Dashboard</Link>}
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

            <button 
              className="md:hidden text-[#1A1A18]"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-[#E8E8E0] px-4 py-4">
            <div className="flex flex-col gap-4">
              <Link to="/gallery" className="text-[#B8962F] py-2">Gallery</Link>
              <Link to="/about" className="text-[#1A1A18] py-2">About</Link>
              <Link to="/technology" className="text-[#1A1A18] py-2">Technology</Link>
              <Link to="/events" className="text-[#1A1A18] py-2">Events</Link>
              <Link to="/pricing" className="text-[#1A1A18] py-2">Pricing</Link>
              {user && <Link to="/dashboard" className="text-[#1A1A18] py-2">Dashboard</Link>}
              {user ? (
                <Button onClick={logout} variant="outline" className="border-[#B8962F] text-[#B8962F]">Logout</Button>
              ) : (
                <Button onClick={login} className="btn-gold">Sign In</Button>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* Content */}
      <div className="pt-24 lg:pt-28 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <Button 
              variant="ghost" 
              onClick={() => navigate('/')} 
              className="text-[#4A4A45] hover:text-[#1A1A18] mb-4 -ml-4"
            >
              <ArrowLeft className="w-4 h-4 mr-2" /> Back to Home
            </Button>
            <h1 className="font-display text-3xl lg:text-4xl text-[#1A1A18] mb-2">
              Art Gallery
            </h1>
            <p className="text-[#4A4A45]">
              Explore masterpieces and their stories
            </p>
          </div>

          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4 mb-8">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#8A8A80]" />
              <Input
                type="text"
                placeholder="Search artworks or artists..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input-light pl-10 w-full"
                data-testid="search-input"
              />
            </div>
            <Select value={periodFilter} onValueChange={setPeriodFilter}>
              <SelectTrigger className="w-full sm:w-48 bg-white border-[#E8E8E0] text-[#1A1A18]" data-testid="period-filter">
                <Filter className="w-4 h-4 mr-2 text-[#4A4A45]" />
                <SelectValue placeholder="All Periods" />
              </SelectTrigger>
              <SelectContent className="bg-white border-[#E8E8E0]">
                <SelectItem value="all">All Periods</SelectItem>
                {periods.map(period => (
                  <SelectItem key={period} value={period}>
                    {period}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Artworks Grid */}
          {loading ? (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="skeleton-light rounded-lg aspect-[3/4]"></div>
              ))}
            </div>
          ) : filteredArtworks.length > 0 ? (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredArtworks.map((artwork) => (
                <Link 
                  key={artwork.artwork_id} 
                  to={`/story/${artwork.story_id}`}
                  className="group"
                  data-testid={`artwork-card-${artwork.artwork_id}`}
                >
                  <div className="card-ivory rounded-lg overflow-hidden">
                    <div className="relative aspect-[3/4] bg-[#1a1a18]">
                      <img 
                        src={artwork.thumbnail_url || artwork.image_url}
                        alt={artwork.title}
                        loading="lazy"
                        referrerPolicy="no-referrer"
                        className="w-full h-full object-contain transition-transform duration-500 group-hover:scale-105"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-[#1A1A18]/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                      
                      {/* Hover Overlay */}
                      <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        <div className="w-14 h-14 rounded-full bg-[#B8962F] flex items-center justify-center">
                          <Play className="w-6 h-6 text-white ml-1" />
                        </div>
                      </div>
                    </div>
                    
                    <div className="p-4">
                      <Badge className="badge-gold text-xs mb-2">{artwork.period}</Badge>
                      <h3 className="font-display text-lg text-[#1A1A18] mb-1 group-hover:text-[#B8962F] transition-colors">
                        {artwork.title}
                      </h3>
                      <p className="text-sm text-[#4A4A45] mb-2">{artwork.artist}, {artwork.year}</p>
                      <div className="flex items-center gap-3 text-xs text-[#8A8A80]">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" /> 3-5 min
                        </span>
                        <span>{artwork.location}</span>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-20">
              <p className="text-[#4A4A45] text-lg">No artworks found matching your criteria</p>
              <Button 
                onClick={() => { setSearchQuery(""); setPeriodFilter("all"); }}
                variant="outline"
                className="mt-4 border-[#B8962F] text-[#B8962F]"
              >
                Clear Filters
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Gallery;
