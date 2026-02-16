import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth, API } from "@/App";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  User,
  LogOut,
  Play,
  Crown,
  Sparkles,
  Fingerprint,
  Palette,
  FileSignature,
  Grid3X3,
  Clock,
  Calendar,
  ChevronRight,
  Menu,
  X
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [knowledgeData, setKnowledgeData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [dashResponse, knowledgeResponse] = await Promise.all([
        axios.get(`${API}/dashboard/`, { withCredentials: true }),
        axios.get(`${API}/dashboard/knowledge`, { withCredentials: true })
      ]);
      setDashboardData(dashResponse.data);
      setKnowledgeData(knowledgeResponse.data);
    } catch (error) {
      console.error("Error fetching dashboard:", error);
    } finally {
      setLoading(false);
    }
  };

  const getMarkerIcon = (type) => {
    switch (type) {
      case 'pigment': return <Palette className="w-4 h-4 text-[#D4AF37]" />;
      case 'signature': return <FileSignature className="w-4 h-4 text-[#00F0FF]" />;
      case 'canvas': return <Grid3X3 className="w-4 h-4 text-[#D4AF37]" />;
      default: return <Fingerprint className="w-4 h-4 text-[#00F0FF]" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-[#D4AF37] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-[#A8A8A0]">Loading dashboard...</p>
        </div>
      </div>
    );
  }

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
              <Link to="/dashboard" className="text-sm font-medium text-[#D4AF37]">Dashboard</Link>
            </div>

            <div className="hidden md:flex items-center gap-4">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center gap-2 text-[#F5F5F0]">
                    {user?.picture ? (
                      <img src={user.picture} alt={user.name} className="w-8 h-8 rounded-full" />
                    ) : (
                      <User className="w-5 h-5" />
                    )}
                    <span className="hidden lg:block">{user?.name}</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="bg-[#0a0a0a] border-[#1a1a1a]">
                  <DropdownMenuItem onClick={logout} className="text-[#F5F5F0] focus:bg-[#111] cursor-pointer">
                    <LogOut className="w-4 h-4 mr-2" /> Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            <button className="md:hidden text-[#F5F5F0]" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <div className="pt-24 lg:pt-28 pb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="font-display text-3xl lg:text-4xl text-[#F5F5F0] mb-2" data-testid="dashboard-title">
              Welcome back, {user?.name?.split(' ')[0]}
            </h1>
            <p className="text-[#A8A8A0]">
              Your art journey continues. Explore new stories or review your knowledge.
            </p>
          </div>

          {/* Stats Cards */}
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div className="card-obsidian rounded-lg p-5">
              <div className="flex items-center justify-between mb-3">
                <span className="text-[#A8A8A0] text-sm">Purchased Stories</span>
                <Play className="w-5 h-5 text-[#D4AF37]" />
              </div>
              <p className="text-3xl font-display text-[#F5F5F0]">
                {dashboardData?.purchased_stories?.length || 0}
              </p>
            </div>

            <div className="card-obsidian rounded-lg p-5">
              <div className="flex items-center justify-between mb-3">
                <span className="text-[#A8A8A0] text-sm">Forensic Markers</span>
                <Fingerprint className="w-5 h-5 text-[#00F0FF]" />
              </div>
              <p className="text-3xl font-display text-[#F5F5F0]">
                {knowledgeData?.total_markers || 0}
              </p>
            </div>

            <div className="card-obsidian rounded-lg p-5">
              <div className="flex items-center justify-between mb-3">
                <span className="text-[#A8A8A0] text-sm">Subscription</span>
                <Crown className="w-5 h-5 text-[#D4AF37]" />
              </div>
              <p className="text-lg font-display text-[#F5F5F0]">
                {dashboardData?.subscription?.tier?.name || "Free"}
              </p>
            </div>

            <div className="card-obsidian rounded-lg p-5">
              <div className="flex items-center justify-between mb-3">
                <span className="text-[#A8A8A0] text-sm">Expertise Level</span>
                <Sparkles className="w-5 h-5 text-[#D4AF37]" />
              </div>
              <div>
                <p className="text-lg font-display text-[#F5F5F0] mb-2">
                  {(knowledgeData?.total_markers || 0) < 5 ? "Novice" : 
                   (knowledgeData?.total_markers || 0) < 15 ? "Apprentice" :
                   (knowledgeData?.total_markers || 0) < 30 ? "Connoisseur" : "Expert"}
                </p>
                <Progress 
                  value={Math.min(((knowledgeData?.total_markers || 0) / 30) * 100, 100)} 
                  className="h-1.5 bg-[#1a1a1a]"
                />
              </div>
            </div>
          </div>

          {/* Main Content */}
          <Tabs defaultValue="stories" className="space-y-6">
            <TabsList className="bg-[#111] p-1">
              <TabsTrigger 
                value="stories" 
                className="data-[state=active]:bg-[#D4AF37] data-[state=active]:text-[#050505]"
              >
                <Play className="w-4 h-4 mr-2" /> My Stories
              </TabsTrigger>
              <TabsTrigger 
                value="knowledge"
                className="data-[state=active]:bg-[#00F0FF] data-[state=active]:text-[#050505]"
              >
                <Fingerprint className="w-4 h-4 mr-2" /> Knowledge
              </TabsTrigger>
            </TabsList>

            {/* Stories Tab */}
            <TabsContent value="stories">
              {dashboardData?.purchased_stories?.length > 0 ? (
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
                  {dashboardData.purchased_stories.map((story) => (
                    <Link
                      key={story.story_id}
                      to={`/experience/${story.story_id}`}
                      className="card-obsidian rounded-lg overflow-hidden group"
                      data-testid={`story-card-${story.story_id}`}
                    >
                      <div className="aspect-video bg-[#111] relative">
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="w-14 h-14 rounded-full bg-[#D4AF37]/20 flex items-center justify-center group-hover:bg-[#D4AF37] transition-colors">
                            <Play className="w-6 h-6 text-[#D4AF37] group-hover:text-[#050505] ml-1" />
                          </div>
                        </div>
                        <Badge className="absolute top-3 left-3 badge-gold">
                          Owned
                        </Badge>
                      </div>
                      <div className="p-4">
                        <h3 className="font-display text-lg text-[#F5F5F0] mb-1 group-hover:text-[#D4AF37] transition-colors">
                          {story.title}
                        </h3>
                        <p className="text-sm text-[#A8A8A0] line-clamp-2">{story.description}</p>
                        <div className="flex items-center gap-3 mt-3 text-xs text-[#666660]">
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" /> {story.duration_minutes} min
                          </span>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="card-obsidian rounded-lg p-12 text-center">
                  <Play className="w-12 h-12 text-[#666660] mx-auto mb-4" />
                  <h3 className="font-display text-xl text-[#F5F5F0] mb-2">No Stories Yet</h3>
                  <p className="text-[#A8A8A0] mb-6">Start your journey by exploring our gallery</p>
                  <Button onClick={() => navigate('/gallery')} className="btn-gold">
                    Browse Gallery <ChevronRight className="w-4 h-4 ml-1" />
                  </Button>
                </div>
              )}
            </TabsContent>

            {/* Knowledge Tab */}
            <TabsContent value="knowledge">
              <div className="grid lg:grid-cols-3 gap-6">
                {/* Markers by Type */}
                <div className="lg:col-span-2 card-obsidian rounded-lg p-6">
                  <h3 className="font-display text-xl text-[#F5F5F0] mb-6">Forensic Markers Learned</h3>
                  
                  {knowledgeData?.by_type && Object.keys(knowledgeData.by_type).length > 0 ? (
                    <div className="grid sm:grid-cols-3 gap-4 mb-6">
                      <div className="p-4 bg-[#D4AF37]/5 border border-[#D4AF37]/20 rounded-lg">
                        <Palette className="w-8 h-8 text-[#D4AF37] mb-2" />
                        <p className="text-2xl font-display text-[#F5F5F0]">
                          {knowledgeData.by_type.pigment?.length || 0}
                        </p>
                        <p className="text-xs text-[#A8A8A0]">Pigment Analysis</p>
                      </div>
                      <div className="p-4 bg-[#00F0FF]/5 border border-[#00F0FF]/20 rounded-lg">
                        <FileSignature className="w-8 h-8 text-[#00F0FF] mb-2" />
                        <p className="text-2xl font-display text-[#F5F5F0]">
                          {knowledgeData.by_type.signature?.length || 0}
                        </p>
                        <p className="text-xs text-[#A8A8A0]">Signature Auth</p>
                      </div>
                      <div className="p-4 bg-[#D4AF37]/5 border border-[#D4AF37]/20 rounded-lg">
                        <Grid3X3 className="w-8 h-8 text-[#D4AF37] mb-2" />
                        <p className="text-2xl font-display text-[#F5F5F0]">
                          {knowledgeData.by_type.canvas?.length || 0}
                        </p>
                        <p className="text-xs text-[#A8A8A0]">Canvas Analysis</p>
                      </div>
                    </div>
                  ) : null}

                  {/* Recent Markers */}
                  <h4 className="text-sm text-[#A8A8A0] mb-3">Recent Activity</h4>
                  <ScrollArea className="h-48">
                    {knowledgeData?.recent_markers?.length > 0 ? (
                      <div className="space-y-3">
                        {knowledgeData.recent_markers.map((marker, index) => (
                          <div key={index} className="flex items-center gap-3 p-3 bg-[#111] rounded-lg">
                            {getMarkerIcon(marker.analysis_type)}
                            <div className="flex-1">
                              <p className="text-sm text-[#F5F5F0] capitalize">
                                {marker.analysis_type} Analysis
                              </p>
                              <p className="text-xs text-[#666660]">
                                {new Date(marker.learned_at).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-[#666660] text-sm text-center py-8">
                        No markers learned yet. Start analyzing artworks!
                      </p>
                    )}
                  </ScrollArea>
                </div>

                {/* Subscription Info */}
                <div className="card-obsidian rounded-lg p-6">
                  <h3 className="font-display text-xl text-[#F5F5F0] mb-4">Your Plan</h3>
                  
                  {dashboardData?.subscription ? (
                    <div className="space-y-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-[#D4AF37]/10 flex items-center justify-center">
                          <Crown className="w-5 h-5 text-[#D4AF37]" />
                        </div>
                        <div>
                          <p className="font-display text-[#F5F5F0]">
                            {dashboardData.subscription.tier.name}
                          </p>
                          <p className="text-xs text-[#A8A8A0]">Active Subscription</p>
                        </div>
                      </div>
                      
                      {dashboardData.subscription.expires && (
                        <div className="flex items-center gap-2 text-sm text-[#A8A8A0]">
                          <Calendar className="w-4 h-4" />
                          Expires: {new Date(dashboardData.subscription.expires).toLocaleDateString()}
                        </div>
                      )}

                      <div className="pt-4 border-t border-[#1a1a1a]">
                        <p className="text-xs text-[#666660] mb-2">Included Features:</p>
                        <ul className="space-y-1">
                          {dashboardData.subscription.tier.features.map((feature, i) => (
                            <li key={i} className="text-xs text-[#A8A8A0] flex items-start gap-2">
                              <Sparkles className="w-3 h-3 text-[#D4AF37] mt-0.5 flex-shrink-0" />
                              {feature}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-6">
                      <p className="text-[#A8A8A0] mb-4">Unlock unlimited access</p>
                      <Button onClick={() => navigate('/pricing')} className="btn-gold w-full">
                        Upgrade Plan
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
