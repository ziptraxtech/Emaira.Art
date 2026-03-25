import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth, API } from "@/App";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Users,
  BarChart3,
  Activity,
  DollarSign,
  Search,
  Eye,
  ChevronLeft,
  ChevronRight,
  Tag,
  TrendingUp,
  Crown,
  Menu,
  X,
  User,
  LogOut,
  ArrowLeft,
  Mail,
  Send,
  Building2,
  Shield,
  Plus,
  Trash2,
  Upload,
  Image,
  ExternalLink
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { toast } from "sonner";

const CRMDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("overview");
  const [analytics, setAnalytics] = useState(null);
  const [users, setUsers] = useState([]);
  const [activities, setActivities] = useState([]);
  const [segments, setSegments] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [subscriptionFilter, setSubscriptionFilter] = useState("all");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userDetail, setUserDetail] = useState(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  // Email Campaigns State
  const [campaigns, setCampaigns] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [newCampaign, setNewCampaign] = useState({ name: "", subject: "", body: "", segment: "all_users" });
  const [showCampaignDialog, setShowCampaignDialog] = useState(false);
  
  // Admin Roles State
  const [admins, setAdmins] = useState([]);
  const [availableRoles, setAvailableRoles] = useState({});
  const [showRoleDialog, setShowRoleDialog] = useState(false);
  const [selectedUserForRole, setSelectedUserForRole] = useState(null);
  const [selectedRole, setSelectedRole] = useState("");
  
  // Museum State
  const [metSearchQuery, setMetSearchQuery] = useState("");
  const [metResults, setMetResults] = useState([]);
  const [metSearching, setMetSearching] = useState(false);
  
  // Organizations State
  const [organizations, setOrganizations] = useState([]);
  const [showOrgDialog, setShowOrgDialog] = useState(false);
  const [newOrg, setNewOrg] = useState({ name: "", type: "gallery", contact_email: "", contact_name: "", website: "", country: "" });

  useEffect(() => {
    fetchData();
  }, [activeTab, currentPage, searchQuery, subscriptionFilter]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === "overview") {
        const [analyticsRes, segmentsRes] = await Promise.all([
          axios.get(`${API}/crm/analytics`, { withCredentials: true }),
          axios.get(`${API}/crm/segments`, { withCredentials: true })
        ]);
        setAnalytics(analyticsRes.data);
        setSegments(segmentsRes.data);
      } else if (activeTab === "users") {
        const params = new URLSearchParams({
          page: currentPage.toString(),
          limit: "20"
        });
        if (searchQuery) params.append("search", searchQuery);
        if (subscriptionFilter !== "all") params.append("subscription", subscriptionFilter);
        
        const res = await axios.get(`${API}/crm/users?${params}`, { withCredentials: true });
        setUsers(res.data.users);
        setTotalPages(res.data.total_pages);
      } else if (activeTab === "activity") {
        const res = await axios.get(`${API}/crm/activities?limit=100`, { withCredentials: true });
        setActivities(res.data.activities);
      } else if (activeTab === "campaigns") {
        const [campaignsRes, templatesRes] = await Promise.all([
          axios.get(`${API}/campaigns/`, { withCredentials: true }),
          axios.get(`${API}/campaigns/templates`, { withCredentials: true })
        ]);
        setCampaigns(campaignsRes.data.campaigns || []);
        setTemplates(templatesRes.data.templates || []);
      } else if (activeTab === "admins") {
        const res = await axios.get(`${API}/admin/users/admins`, { withCredentials: true });
        setAdmins(res.data.admins || []);
        setAvailableRoles(res.data.available_roles || {});
      } else if (activeTab === "organizations") {
        try {
          const res = await axios.get(`${API}/organizations/`, { withCredentials: true });
          setOrganizations(res.data.organizations || []);
        } catch (e) {
          if (e.response?.status === 403) {
            toast.error("Only Super Admins can manage organizations");
          }
        }
      }
    } catch (error) {
      console.error("Error fetching CRM data:", error);
      if (error.response?.status === 403) {
        toast.error("You don't have permission to access this section");
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchUserDetail = async (userId) => {
    try {
      const res = await axios.get(`${API}/crm/users/${userId}`, { withCredentials: true });
      setUserDetail(res.data);
      setSelectedUser(userId);
    } catch (error) {
      console.error("Error fetching user detail:", error);
    }
  };

  const createOrganization = async () => {
    try {
      await axios.post(`${API}/organizations/`, newOrg, { withCredentials: true });
      toast.success("Organization created successfully");
      setShowOrgDialog(false);
      setNewOrg({ name: "", type: "gallery", contact_email: "", contact_name: "", website: "", country: "" });
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to create organization");
    }
  };

  const deleteOrganization = async (orgId) => {
    if (!window.confirm("Are you sure you want to delete this organization?")) return;
    try {
      await axios.delete(`${API}/organizations/${orgId}`, { withCredentials: true });
      toast.success("Organization deleted");
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to delete organization");
    }
  };

  const createCampaign = async () => {
    try {
      await axios.post(`${API}/campaigns/`, newCampaign, { withCredentials: true });
      toast.success("Campaign created successfully");
      setShowCampaignDialog(false);
      setNewCampaign({ name: "", subject: "", body: "", segment: "all_users" });
      fetchData();
    } catch (error) {
      toast.error("Failed to create campaign");
    }
  };

  const sendCampaign = async (campaignId, testMode = false) => {
    try {
      const res = await axios.post(`${API}/campaigns/${campaignId}/send`, { test_mode: testMode }, { withCredentials: true });
      toast.success(res.data.message);
      fetchData();
    } catch (error) {
      toast.error("Failed to send campaign");
    }
  };

  const deleteCampaign = async (campaignId) => {
    try {
      await axios.delete(`${API}/campaigns/${campaignId}`, { withCredentials: true });
      toast.success("Campaign deleted");
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to delete campaign");
    }
  };

  const assignRole = async () => {
    if (!selectedUserForRole || !selectedRole) return;
    try {
      await axios.post(`${API}/admin/assign-role/${selectedUserForRole}`, { role: selectedRole }, { withCredentials: true });
      toast.success("Role assigned successfully");
      setShowRoleDialog(false);
      setSelectedUserForRole(null);
      setSelectedRole("");
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to assign role");
    }
  };

  const searchMetMuseum = async () => {
    if (!metSearchQuery.trim()) return;
    setMetSearching(true);
    try {
      const res = await axios.get(`${API}/museums/met/search?q=${encodeURIComponent(metSearchQuery)}&limit=10`, { withCredentials: true });
      setMetResults(res.data.artworks || []);
      if (res.data.artworks?.length === 0) {
        toast.info("No artworks found");
      }
    } catch (error) {
      toast.error("Search failed - Met Museum API may be temporarily unavailable");
      setMetResults([]);
    } finally {
      setMetSearching(false);
    }
  };

  const importMetArtwork = async (objectId) => {
    try {
      const res = await axios.post(`${API}/museums/met/import/${objectId}`, {}, { withCredentials: true });
      toast.success(res.data.message);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to import artwork");
    }
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case "login": return <User className="w-4 h-4 text-green-500" />;
      case "purchase": return <DollarSign className="w-4 h-4 text-[#B8962F]" />;
      case "view_artwork": return <Eye className="w-4 h-4 text-[#1A365D]" />;
      case "forensic_analysis": return <Activity className="w-4 h-4 text-purple-500" />;
      case "send_campaign": return <Mail className="w-4 h-4 text-blue-500" />;
      case "admin_action": return <Shield className="w-4 h-4 text-red-500" />;
      default: return <Activity className="w-4 h-4 text-gray-400" />;
    }
  };

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case "super_admin": return "bg-red-100 text-red-700";
      case "admin": return "bg-purple-100 text-purple-700";
      case "content_curator": return "bg-blue-100 text-blue-700";
      case "marketing_admin": return "bg-green-100 text-green-700";
      default: return "bg-gray-100 text-gray-700";
    }
  };

  return (
    <div className="min-h-screen bg-[#FAFAF8]">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass-light">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 lg:h-20">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-10 h-10 rounded bg-gradient-to-br from-[#D4AF37] to-[#B8962F] flex items-center justify-center">
                <span className="font-display text-white text-xl font-bold">E</span>
              </div>
              <span className="font-display text-xl text-[#1A1A18] hidden sm:block">Emaira.Art</span>
            </Link>

            <div className="hidden md:flex items-center gap-4">
              <Badge className="badge-forensic">
                <BarChart3 className="w-3 h-3 mr-1" /> Admin Panel
              </Badge>
            </div>

            <div className="hidden md:flex items-center gap-4">
              {user && (
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
              )}
            </div>

            <button className="md:hidden text-[#1A1A18]" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
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
            <Button 
              variant="ghost" 
              onClick={() => navigate('/dashboard')} 
              className="text-[#4A4A45] hover:text-[#1A1A18] mb-4 -ml-4"
            >
              <ArrowLeft className="w-4 h-4 mr-2" /> Back to Dashboard
            </Button>
            <h1 className="font-display text-3xl lg:text-4xl text-[#1A1A18] mb-2" data-testid="crm-title">
              Admin Panel
            </h1>
            <p className="text-[#4A4A45]">
              Manage users, campaigns, admin roles, and museum integrations
            </p>
          </div>

          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="bg-[#F5F5F0] flex-wrap">
              <TabsTrigger value="overview" className="data-[state=active]:bg-[#B8962F] data-[state=active]:text-white" data-testid="tab-overview">
                <BarChart3 className="w-4 h-4 mr-2" /> Overview
              </TabsTrigger>
              <TabsTrigger value="users" className="data-[state=active]:bg-[#B8962F] data-[state=active]:text-white" data-testid="tab-users">
                <Users className="w-4 h-4 mr-2" /> Users
              </TabsTrigger>
              <TabsTrigger value="campaigns" className="data-[state=active]:bg-[#B8962F] data-[state=active]:text-white" data-testid="tab-campaigns">
                <Mail className="w-4 h-4 mr-2" /> Campaigns
              </TabsTrigger>
              <TabsTrigger value="admins" className="data-[state=active]:bg-[#B8962F] data-[state=active]:text-white" data-testid="tab-admins">
                <Shield className="w-4 h-4 mr-2" /> Admins
              </TabsTrigger>
              <TabsTrigger value="organizations" className="data-[state=active]:bg-[#B8962F] data-[state=active]:text-white" data-testid="tab-organizations">
                <Building2 className="w-4 h-4 mr-2" /> Organizations
              </TabsTrigger>
              <TabsTrigger value="museums" className="data-[state=active]:bg-[#B8962F] data-[state=active]:text-white" data-testid="tab-museums">
                <Building2 className="w-4 h-4 mr-2" /> Museums
              </TabsTrigger>
              <TabsTrigger value="activity" className="data-[state=active]:bg-[#B8962F] data-[state=active]:text-white" data-testid="tab-activity">
                <Activity className="w-4 h-4 mr-2" /> Activity
              </TabsTrigger>
            </TabsList>

            {/* Overview Tab */}
            <TabsContent value="overview">
              {loading ? (
                <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  {[...Array(4)].map((_, i) => (
                    <div key={i} className="skeleton-light h-32 rounded-lg"></div>
                  ))}
                </div>
              ) : (
                <>
                  <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    <div className="card-ivory rounded-lg p-5" data-testid="stat-users">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-[#4A4A45] text-sm">Total Users</span>
                        <Users className="w-5 h-5 text-[#B8962F]" />
                      </div>
                      <p className="text-3xl font-display text-[#1A1A18]">{analytics?.total_users || 0}</p>
                      <p className="text-xs text-[#8A8A80] mt-1">+{analytics?.recent_signups_30d || 0} this month</p>
                    </div>

                    <div className="card-ivory rounded-lg p-5" data-testid="stat-revenue">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-[#4A4A45] text-sm">Total Revenue</span>
                        <DollarSign className="w-5 h-5 text-[#B8962F]" />
                      </div>
                      <p className="text-3xl font-display text-[#1A1A18]">${(analytics?.revenue?.total || 0).toLocaleString()}</p>
                      <p className="text-xs text-[#8A8A80] mt-1">{analytics?.revenue?.transaction_count || 0} transactions</p>
                    </div>

                    <div className="card-ivory rounded-lg p-5" data-testid="stat-active">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-[#4A4A45] text-sm">Active Users (7d)</span>
                        <TrendingUp className="w-5 h-5 text-green-500" />
                      </div>
                      <p className="text-3xl font-display text-[#1A1A18]">{analytics?.active_users_7d || 0}</p>
                    </div>

                    <div className="card-ivory rounded-lg p-5" data-testid="stat-advisory">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-[#4A4A45] text-sm">Advisory Members</span>
                        <Crown className="w-5 h-5 text-[#B8962F]" />
                      </div>
                      <p className="text-3xl font-display text-[#1A1A18]">{analytics?.advisory_subscribers || 0}</p>
                    </div>
                  </div>

                  <div className="grid lg:grid-cols-2 gap-6">
                    <div className="card-ivory rounded-lg p-6">
                      <h3 className="font-display text-xl text-[#1A1A18] mb-4">User Segments</h3>
                      <div className="space-y-3">
                        {segments && Object.entries(segments).map(([key, value]) => (
                          <div key={key} className="flex items-center justify-between p-3 bg-[#F5F5F0] rounded-lg">
                            <span className="text-sm text-[#4A4A45] capitalize">{key.replace(/_/g, ' ')}</span>
                            <span className="font-medium text-[#1A1A18]">{value}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="card-ivory rounded-lg p-6">
                      <h3 className="font-display text-xl text-[#1A1A18] mb-4">Subscription Breakdown</h3>
                      <div className="space-y-3">
                        {analytics?.subscription_breakdown && Object.entries(analytics.subscription_breakdown).map(([tier, count]) => (
                          <div key={tier} className="flex items-center justify-between p-3 bg-[#F5F5F0] rounded-lg">
                            <div className="flex items-center gap-2">
                              {tier === 'pro_collector' && <Crown className="w-4 h-4 text-[#B8962F]" />}
                              {tier === 'collectors_advisory' && <Crown className="w-4 h-4 text-purple-500" />}
                              {tier === 'connoisseur' && <Tag className="w-4 h-4 text-[#B8962F]" />}
                              <span className="text-sm text-[#4A4A45] capitalize">{tier?.replace(/_/g, ' ') || 'Free'}</span>
                            </div>
                            <span className="font-medium text-[#1A1A18]">{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </>
              )}
            </TabsContent>

            {/* Users Tab */}
            <TabsContent value="users">
              <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#8A8A80]" />
                  <Input
                    type="text"
                    placeholder="Search by name or email..."
                    value={searchQuery}
                    onChange={(e) => { setSearchQuery(e.target.value); setCurrentPage(1); }}
                    className="input-light pl-10"
                    data-testid="user-search"
                  />
                </div>
                <Select value={subscriptionFilter} onValueChange={(v) => { setSubscriptionFilter(v); setCurrentPage(1); }}>
                  <SelectTrigger className="w-48 bg-white border-[#E8E8E0]">
                    <SelectValue placeholder="All Subscriptions" />
                  </SelectTrigger>
                  <SelectContent className="bg-white border-[#E8E8E0]">
                    <SelectItem value="all">All Users</SelectItem>
                    <SelectItem value="collectors_advisory">Collector's Advisory</SelectItem>
                    <SelectItem value="pro_collector">Pro Collector</SelectItem>
                    <SelectItem value="connoisseur">Connoisseur</SelectItem>
                    <SelectItem value="deep_dive">Deep Dive</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {loading ? (
                <div className="space-y-4">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="skeleton-light h-16 rounded-lg"></div>
                  ))}
                </div>
              ) : (
                <>
                  <div className="card-ivory rounded-lg overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="bg-[#F5F5F0]">
                          <tr>
                            <th className="text-left p-4 text-sm font-medium text-[#4A4A45]">User</th>
                            <th className="text-left p-4 text-sm font-medium text-[#4A4A45]">Role</th>
                            <th className="text-left p-4 text-sm font-medium text-[#4A4A45]">Subscription</th>
                            <th className="text-left p-4 text-sm font-medium text-[#4A4A45]">Total Spent</th>
                            <th className="text-left p-4 text-sm font-medium text-[#4A4A45]">Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {users.map((u) => (
                            <tr key={u.user_id} className="border-t border-[#E8E8E0] hover:bg-[#F5F5F0]">
                              <td className="p-4">
                                <div className="flex items-center gap-3">
                                  {u.picture ? (
                                    <img src={u.picture} alt={u.name} className="w-8 h-8 rounded-full" />
                                  ) : (
                                    <div className="w-8 h-8 rounded-full bg-[#B8962F]/20 flex items-center justify-center">
                                      <User className="w-4 h-4 text-[#B8962F]" />
                                    </div>
                                  )}
                                  <div>
                                    <p className="text-sm font-medium text-[#1A1A18]">{u.name}</p>
                                    <p className="text-xs text-[#8A8A80]">{u.email}</p>
                                  </div>
                                </div>
                              </td>
                              <td className="p-4">
                                <Badge className={getRoleBadgeColor(u.role)}>
                                  {u.role?.replace(/_/g, ' ') || 'user'}
                                </Badge>
                              </td>
                              <td className="p-4">
                                <Badge className={u.subscription_tier ? 'badge-gold' : 'bg-gray-100 text-gray-600'}>
                                  {u.subscription_tier?.replace(/_/g, ' ') || 'Free'}
                                </Badge>
                              </td>
                              <td className="p-4 text-sm text-[#1A1A18]">${(u.total_spent || 0).toFixed(2)}</td>
                              <td className="p-4">
                                <div className="flex gap-2">
                                  <Dialog>
                                    <DialogTrigger asChild>
                                      <Button variant="ghost" size="sm" onClick={() => fetchUserDetail(u.user_id)} className="text-[#B8962F]">
                                        <Eye className="w-4 h-4" />
                                      </Button>
                                    </DialogTrigger>
                                    <DialogContent className="bg-white max-w-2xl max-h-[80vh] overflow-y-auto">
                                      <DialogHeader>
                                        <DialogTitle className="font-display text-xl">User Details</DialogTitle>
                                      </DialogHeader>
                                      {userDetail && (
                                        <div className="space-y-4">
                                          <div className="flex items-center gap-4">
                                            {userDetail.user.picture ? (
                                              <img src={userDetail.user.picture} alt="" className="w-16 h-16 rounded-full" />
                                            ) : (
                                              <div className="w-16 h-16 rounded-full bg-[#B8962F]/20 flex items-center justify-center">
                                                <User className="w-8 h-8 text-[#B8962F]" />
                                              </div>
                                            )}
                                            <div>
                                              <h3 className="font-display text-lg">{userDetail.user.name}</h3>
                                              <p className="text-sm text-[#8A8A80]">{userDetail.user.email}</p>
                                              <Badge className={getRoleBadgeColor(userDetail.user.role)}>{userDetail.user.role}</Badge>
                                            </div>
                                          </div>
                                          <div className="grid grid-cols-2 gap-4">
                                            <div className="p-3 bg-[#F5F5F0] rounded-lg">
                                              <p className="text-xs text-[#8A8A80]">Total Spent</p>
                                              <p className="font-display text-lg">${userDetail.stats.total_spent.toFixed(2)}</p>
                                            </div>
                                            <div className="p-3 bg-[#F5F5F0] rounded-lg">
                                              <p className="text-xs text-[#8A8A80]">Purchases</p>
                                              <p className="font-display text-lg">{userDetail.stats.total_purchases}</p>
                                            </div>
                                            <div className="p-3 bg-[#F5F5F0] rounded-lg">
                                              <p className="text-xs text-[#8A8A80]">Stories Owned</p>
                                              <p className="font-display text-lg">{userDetail.stats.purchased_stories_count}</p>
                                            </div>
                                            <div className="p-3 bg-[#F5F5F0] rounded-lg">
                                              <p className="text-xs text-[#8A8A80]">Uploaded Artworks</p>
                                              <p className="font-display text-lg">{userDetail.stats.uploaded_artworks_count}</p>
                                            </div>
                                          </div>
                                        </div>
                                      )}
                                    </DialogContent>
                                  </Dialog>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => {
                                      setSelectedUserForRole(u.user_id);
                                      setShowRoleDialog(true);
                                    }}
                                    className="text-[#1A365D]"
                                  >
                                    <Shield className="w-4 h-4" />
                                  </Button>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {totalPages > 1 && (
                    <div className="flex items-center justify-center gap-2 mt-4">
                      <Button variant="outline" size="sm" onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1} className="border-[#E8E8E0]">
                        <ChevronLeft className="w-4 h-4" />
                      </Button>
                      <span className="text-sm text-[#4A4A45]">Page {currentPage} of {totalPages}</span>
                      <Button variant="outline" size="sm" onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages} className="border-[#E8E8E0]">
                        <ChevronRight className="w-4 h-4" />
                      </Button>
                    </div>
                  )}
                </>
              )}
            </TabsContent>

            {/* Campaigns Tab */}
            <TabsContent value="campaigns">
              <div className="flex justify-between items-center mb-6">
                <h3 className="font-display text-xl text-[#1A1A18]">Email Campaigns</h3>
                <Button onClick={() => setShowCampaignDialog(true)} className="btn-gold" data-testid="create-campaign-btn">
                  <Plus className="w-4 h-4 mr-2" /> New Campaign
                </Button>
              </div>

              {loading ? (
                <div className="space-y-4">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="skeleton-light h-24 rounded-lg"></div>
                  ))}
                </div>
              ) : (
                <div className="space-y-4">
                  {campaigns.length === 0 ? (
                    <div className="card-ivory rounded-lg p-8 text-center">
                      <Mail className="w-12 h-12 mx-auto text-[#8A8A80] mb-4" />
                      <p className="text-[#4A4A45]">No campaigns yet. Create your first email campaign!</p>
                    </div>
                  ) : (
                    campaigns.map((campaign) => (
                      <div key={campaign.campaign_id} className="card-ivory rounded-lg p-6" data-testid={`campaign-${campaign.campaign_id}`}>
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-display text-lg text-[#1A1A18]">{campaign.name}</h4>
                            <p className="text-sm text-[#4A4A45] mt-1">{campaign.subject}</p>
                            <div className="flex gap-2 mt-2">
                              <Badge className="bg-[#F5F5F0] text-[#4A4A45]">{campaign.segment?.replace(/_/g, ' ')}</Badge>
                              <Badge className={campaign.status === 'sent' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}>
                                {campaign.status}
                              </Badge>
                            </div>
                            {campaign.status === 'sent' && (
                              <p className="text-xs text-[#8A8A80] mt-2">Sent to {campaign.recipients_count} recipients</p>
                            )}
                          </div>
                          <div className="flex gap-2">
                            {campaign.status === 'draft' && (
                              <>
                                <Button size="sm" variant="outline" onClick={() => sendCampaign(campaign.campaign_id, true)} className="border-[#B8962F] text-[#B8962F]">
                                  Test
                                </Button>
                                <Button size="sm" onClick={() => sendCampaign(campaign.campaign_id)} className="btn-gold">
                                  <Send className="w-4 h-4 mr-1" /> Send
                                </Button>
                                <Button size="sm" variant="ghost" onClick={() => deleteCampaign(campaign.campaign_id)} className="text-red-500">
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* Campaign Templates */}
              <div className="mt-8">
                <h3 className="font-display text-xl text-[#1A1A18] mb-4">Email Templates</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  {templates.map((template) => (
                    <div key={template.id} className="card-ivory rounded-lg p-4">
                      <h4 className="font-medium text-[#1A1A18]">{template.name}</h4>
                      <p className="text-sm text-[#8A8A80] mt-1">{template.subject}</p>
                      <Button
                        size="sm"
                        variant="outline"
                        className="mt-3 border-[#B8962F] text-[#B8962F]"
                        onClick={() => {
                          setNewCampaign({
                            name: template.name,
                            subject: template.subject,
                            body: template.body,
                            segment: "all_users"
                          });
                          setShowCampaignDialog(true);
                        }}
                      >
                        Use Template
                      </Button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Create Campaign Dialog */}
              <Dialog open={showCampaignDialog} onOpenChange={setShowCampaignDialog}>
                <DialogContent className="bg-white max-w-lg">
                  <DialogHeader>
                    <DialogTitle className="font-display text-xl">Create Campaign</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-[#4A4A45]">Campaign Name</label>
                      <Input
                        value={newCampaign.name}
                        onChange={(e) => setNewCampaign({...newCampaign, name: e.target.value})}
                        placeholder="e.g., Monthly Newsletter"
                        className="input-light mt-1"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium text-[#4A4A45]">Subject Line</label>
                      <Input
                        value={newCampaign.subject}
                        onChange={(e) => setNewCampaign({...newCampaign, subject: e.target.value})}
                        placeholder="Your email subject"
                        className="input-light mt-1"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium text-[#4A4A45]">Target Segment</label>
                      <Select value={newCampaign.segment} onValueChange={(v) => setNewCampaign({...newCampaign, segment: v})}>
                        <SelectTrigger className="bg-white border-[#E8E8E0] mt-1">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-white border-[#E8E8E0]">
                          <SelectItem value="all_users">All Users</SelectItem>
                          <SelectItem value="subscribers">Subscribers Only</SelectItem>
                          <SelectItem value="advisory_members">Collector's Advisory</SelectItem>
                          <SelectItem value="high_value">High Value ($200+)</SelectItem>
                          <SelectItem value="free_users">Free Users</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-[#4A4A45]">Email Body</label>
                      <Textarea
                        value={newCampaign.body}
                        onChange={(e) => setNewCampaign({...newCampaign, body: e.target.value})}
                        placeholder="Write your email content... Use {{name}} for personalization"
                        className="input-light mt-1 min-h-[150px]"
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setShowCampaignDialog(false)}>Cancel</Button>
                    <Button onClick={createCampaign} className="btn-gold">Create Campaign</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </TabsContent>

            {/* Admins Tab */}
            <TabsContent value="admins">
              <div className="mb-6">
                <h3 className="font-display text-xl text-[#1A1A18] mb-2">Admin Roles</h3>
                <p className="text-[#4A4A45] text-sm">Manage team members and their permissions</p>
              </div>

              {loading ? (
                <div className="space-y-4">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="skeleton-light h-20 rounded-lg"></div>
                  ))}
                </div>
              ) : (
                <>
                  {/* Role Descriptions */}
                  <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    {Object.entries(availableRoles).map(([roleKey, roleInfo]) => (
                      <div key={roleKey} className="card-ivory rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Shield className="w-4 h-4 text-[#B8962F]" />
                          <span className="font-medium text-[#1A1A18]">{roleInfo.name}</span>
                        </div>
                        <p className="text-xs text-[#8A8A80]">{roleInfo.description}</p>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {roleInfo.permissions.slice(0, 3).map((perm) => (
                            <Badge key={perm} className="bg-[#F5F5F0] text-[#4A4A45] text-xs">
                              {perm.replace(/_/g, ' ')}
                            </Badge>
                          ))}
                          {roleInfo.permissions.length > 3 && (
                            <Badge className="bg-[#F5F5F0] text-[#4A4A45] text-xs">
                              +{roleInfo.permissions.length - 3} more
                            </Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Admin List */}
                  <div className="card-ivory rounded-lg overflow-hidden">
                    <div className="p-4 bg-[#F5F5F0] flex justify-between items-center">
                      <h4 className="font-medium text-[#1A1A18]">Current Admins</h4>
                    </div>
                    <div className="divide-y divide-[#E8E8E0]">
                      {admins.length === 0 ? (
                        <div className="p-8 text-center">
                          <Shield className="w-12 h-12 mx-auto text-[#8A8A80] mb-4" />
                          <p className="text-[#4A4A45]">No admin users found</p>
                        </div>
                      ) : (
                        admins.map((admin) => (
                          <div key={admin.user_id} className="p-4 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              {admin.picture ? (
                                <img src={admin.picture} alt={admin.name} className="w-10 h-10 rounded-full" />
                              ) : (
                                <div className="w-10 h-10 rounded-full bg-[#B8962F]/20 flex items-center justify-center">
                                  <User className="w-5 h-5 text-[#B8962F]" />
                                </div>
                              )}
                              <div>
                                <p className="font-medium text-[#1A1A18]">{admin.name}</p>
                                <p className="text-sm text-[#8A8A80]">{admin.email}</p>
                              </div>
                            </div>
                            <div className="flex items-center gap-3">
                              <Badge className={getRoleBadgeColor(admin.role)}>
                                {admin.role?.replace(/_/g, ' ')}
                              </Badge>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  setSelectedUserForRole(admin.user_id);
                                  setShowRoleDialog(true);
                                }}
                                className="text-[#B8962F]"
                              >
                                Edit
                              </Button>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </>
              )}

              {/* Assign Role Dialog */}
              <Dialog open={showRoleDialog} onOpenChange={setShowRoleDialog}>
                <DialogContent className="bg-white">
                  <DialogHeader>
                    <DialogTitle className="font-display text-xl">Assign Role</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-[#4A4A45]">Select Role</label>
                      <Select value={selectedRole} onValueChange={setSelectedRole}>
                        <SelectTrigger className="bg-white border-[#E8E8E0] mt-1">
                          <SelectValue placeholder="Choose a role" />
                        </SelectTrigger>
                        <SelectContent className="bg-white border-[#E8E8E0]">
                          <SelectItem value="user">User (No Admin Access)</SelectItem>
                          <SelectItem value="support_admin">Support Admin</SelectItem>
                          <SelectItem value="marketing_admin">Marketing Admin</SelectItem>
                          <SelectItem value="content_curator">Content Curator</SelectItem>
                          <SelectItem value="super_admin">Super Admin</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setShowRoleDialog(false)}>Cancel</Button>
                    <Button onClick={assignRole} className="btn-gold" disabled={!selectedRole}>
                      Assign Role
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </TabsContent>

            {/* Organizations Tab */}
            <TabsContent value="organizations">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="font-display text-xl text-[#1A1A18] mb-2">Organizations</h3>
                  <p className="text-[#4A4A45] text-sm">Manage museums, galleries, and collector organizations</p>
                </div>
                <Button onClick={() => setShowOrgDialog(true)} className="btn-gold" data-testid="create-org-btn">
                  <Plus className="w-4 h-4 mr-2" /> New Organization
                </Button>
              </div>

              {loading ? (
                <div className="space-y-4">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="skeleton-light h-24 rounded-lg"></div>
                  ))}
                </div>
              ) : (
                <div className="space-y-4">
                  {organizations.length === 0 ? (
                    <div className="card-ivory rounded-lg p-8 text-center">
                      <Building2 className="w-12 h-12 mx-auto text-[#8A8A80] mb-4" />
                      <p className="text-[#4A4A45]">No organizations yet. Create your first organization!</p>
                    </div>
                  ) : (
                    organizations.map((org) => (
                      <div key={org.org_id} className="card-ivory rounded-lg p-6" data-testid={`org-${org.org_id}`}>
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="flex items-center gap-2 mb-2">
                              <h4 className="font-display text-lg text-[#1A1A18]">{org.name}</h4>
                              <Badge className={org.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}>
                                {org.is_active ? 'Active' : 'Inactive'}
                              </Badge>
                            </div>
                            <p className="text-sm text-[#4A4A45]">{org.contact_email}</p>
                            <div className="flex gap-2 mt-2">
                              <Badge className="bg-[#F5F5F0] text-[#4A4A45]">{org.type}</Badge>
                              <Badge className="bg-[#F5F5F0] text-[#4A4A45]">{org.subscription_plan}</Badge>
                              {org.country && <Badge className="bg-[#F5F5F0] text-[#4A4A45]">{org.country}</Badge>}
                            </div>
                            <p className="text-xs text-[#8A8A80] mt-2">
                              {org.members?.length || 0} members • {org.admin_users?.length || 0} admins
                            </p>
                          </div>
                          <div className="flex gap-2">
                            {org.website && (
                              <Button size="sm" variant="outline" className="border-[#E8E8E0]" onClick={() => window.open(org.website, '_blank')}>
                                <ExternalLink className="w-4 h-4" />
                              </Button>
                            )}
                            <Button size="sm" variant="ghost" onClick={() => deleteOrganization(org.org_id)} className="text-red-500">
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}

              {/* Create Organization Dialog */}
              <Dialog open={showOrgDialog} onOpenChange={setShowOrgDialog}>
                <DialogContent className="bg-white max-w-lg">
                  <DialogHeader>
                    <DialogTitle className="font-display text-xl">Create Organization</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-[#4A4A45]">Organization Name *</label>
                      <Input
                        value={newOrg.name}
                        onChange={(e) => setNewOrg({...newOrg, name: e.target.value})}
                        placeholder="e.g., Metropolitan Museum"
                        className="input-light mt-1"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium text-[#4A4A45]">Type</label>
                      <Select value={newOrg.type} onValueChange={(v) => setNewOrg({...newOrg, type: v})}>
                        <SelectTrigger className="bg-white border-[#E8E8E0] mt-1">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-white border-[#E8E8E0]">
                          <SelectItem value="museum">Museum</SelectItem>
                          <SelectItem value="gallery">Gallery</SelectItem>
                          <SelectItem value="collector">Collector</SelectItem>
                          <SelectItem value="auction_house">Auction House</SelectItem>
                          <SelectItem value="educational">Educational</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-[#4A4A45]">Contact Email *</label>
                      <Input
                        type="email"
                        value={newOrg.contact_email}
                        onChange={(e) => setNewOrg({...newOrg, contact_email: e.target.value})}
                        placeholder="contact@organization.com"
                        className="input-light mt-1"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium text-[#4A4A45]">Contact Name</label>
                      <Input
                        value={newOrg.contact_name}
                        onChange={(e) => setNewOrg({...newOrg, contact_name: e.target.value})}
                        placeholder="John Doe"
                        className="input-light mt-1"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium text-[#4A4A45]">Website</label>
                      <Input
                        value={newOrg.website}
                        onChange={(e) => setNewOrg({...newOrg, website: e.target.value})}
                        placeholder="https://www.organization.com"
                        className="input-light mt-1"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium text-[#4A4A45]">Country</label>
                      <Input
                        value={newOrg.country}
                        onChange={(e) => setNewOrg({...newOrg, country: e.target.value})}
                        placeholder="United States"
                        className="input-light mt-1"
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setShowOrgDialog(false)}>Cancel</Button>
                    <Button onClick={createOrganization} className="btn-gold" disabled={!newOrg.name || !newOrg.contact_email}>
                      Create Organization
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </TabsContent>

            {/* Museums Tab */}
            <TabsContent value="museums">
              <div className="mb-6">
                <h3 className="font-display text-xl text-[#1A1A18] mb-2">Museum Integration</h3>
                <p className="text-[#4A4A45] text-sm">Search and import artworks from The Metropolitan Museum of Art</p>
              </div>

              <div className="card-ivory rounded-lg p-6 mb-6">
                <h4 className="font-medium text-[#1A1A18] mb-4 flex items-center gap-2">
                  <Building2 className="w-5 h-5 text-[#B8962F]" />
                  The Met Museum Open Access
                </h4>
                <div className="flex gap-4">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#8A8A80]" />
                    <Input
                      type="text"
                      placeholder="Search artworks (e.g., Van Gogh, Impressionism, Portrait)"
                      value={metSearchQuery}
                      onChange={(e) => setMetSearchQuery(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && searchMetMuseum()}
                      className="input-light pl-10"
                      data-testid="met-search-input"
                    />
                  </div>
                  <Button onClick={searchMetMuseum} disabled={metSearching} className="btn-gold" data-testid="met-search-btn">
                    {metSearching ? "Searching..." : "Search"}
                  </Button>
                </div>
                <p className="text-xs text-[#8A8A80] mt-2">
                  Access over 470,000 artworks from The Met's open access collection
                </p>
              </div>

              {metResults.length > 0 && (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {metResults.map((artwork) => (
                    <div key={artwork.met_object_id} className="card-ivory rounded-lg overflow-hidden">
                      {artwork.thumbnail_url ? (
                        <img
                          src={artwork.thumbnail_url}
                          alt={artwork.title}
                          className="w-full h-48 object-cover"
                        />
                      ) : (
                        <div className="w-full h-48 bg-[#F5F5F0] flex items-center justify-center">
                          <Image className="w-12 h-12 text-[#8A8A80]" />
                        </div>
                      )}
                      <div className="p-4">
                        <h5 className="font-medium text-[#1A1A18] line-clamp-1">{artwork.title}</h5>
                        <p className="text-sm text-[#4A4A45]">{artwork.artist}</p>
                        <p className="text-xs text-[#8A8A80] mt-1">{artwork.period} • {artwork.year}</p>
                        <div className="flex gap-2 mt-3">
                          <Button
                            size="sm"
                            onClick={() => importMetArtwork(artwork.met_object_id)}
                            className="btn-gold flex-1"
                            data-testid={`import-${artwork.met_object_id}`}
                          >
                            <Upload className="w-4 h-4 mr-1" /> Import
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="border-[#E8E8E0]"
                            onClick={() => window.open(`https://www.metmuseum.org/art/collection/search/${artwork.met_object_id}`, '_blank')}
                          >
                            <ExternalLink className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {metResults.length === 0 && metSearchQuery && !metSearching && (
                <div className="card-ivory rounded-lg p-8 text-center">
                  <Building2 className="w-12 h-12 mx-auto text-[#8A8A80] mb-4" />
                  <p className="text-[#4A4A45]">No results found. Try a different search term.</p>
                  <p className="text-sm text-[#8A8A80] mt-2">Note: The Met API may occasionally be unavailable</p>
                </div>
              )}
            </TabsContent>

            {/* Activity Tab */}
            <TabsContent value="activity">
              {loading ? (
                <div className="space-y-4">
                  {[...Array(10)].map((_, i) => (
                    <div key={i} className="skeleton-light h-12 rounded-lg"></div>
                  ))}
                </div>
              ) : (
                <div className="card-ivory rounded-lg p-6">
                  <h3 className="font-display text-xl text-[#1A1A18] mb-4">Recent Activity</h3>
                  <ScrollArea className="h-[500px]">
                    <div className="space-y-3">
                      {activities.map((activity, index) => (
                        <div key={index} className="flex items-center gap-4 p-3 bg-[#F5F5F0] rounded-lg">
                          <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center">
                            {getActivityIcon(activity.activity_type)}
                          </div>
                          <div className="flex-1">
                            <p className="text-sm text-[#1A1A18] capitalize">
                              {activity.activity_type.replace(/_/g, ' ')}
                            </p>
                            <p className="text-xs text-[#8A8A80]">
                              User: {activity.user_id}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-[#8A8A80]">
                              {new Date(activity.created_at).toLocaleString()}
                            </p>
                          </div>
                        </div>
                      ))}
                      {activities.length === 0 && (
                        <p className="text-center text-[#8A8A80] py-8">No activities recorded yet</p>
                      )}
                    </div>
                  </ScrollArea>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default CRMDashboard;
