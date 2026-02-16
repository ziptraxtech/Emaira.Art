import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth, API } from "@/App";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
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
  UserPlus,
  Tag,
  StickyNote,
  TrendingUp,
  Clock,
  Crown,
  Menu,
  X,
  User,
  LogOut,
  ArrowLeft
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

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

  useEffect(() => {
    fetchData();
  }, [activeTab, currentPage, searchQuery, subscriptionFilter]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === "overview") {
        const [analyticsRes, segmentsRes] = await Promise.all([
          axios.get(`${API}/crm/analytics`),
          axios.get(`${API}/crm/segments`)
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
        
        const res = await axios.get(`${API}/crm/users?${params}`);
        setUsers(res.data.users);
        setTotalPages(res.data.total_pages);
      } else if (activeTab === "activity") {
        const res = await axios.get(`${API}/crm/activities?limit=100`);
        setActivities(res.data.activities);
      }
    } catch (error) {
      console.error("Error fetching CRM data:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserDetail = async (userId) => {
    try {
      const res = await axios.get(`${API}/crm/users/${userId}`);
      setUserDetail(res.data);
      setSelectedUser(userId);
    } catch (error) {
      console.error("Error fetching user detail:", error);
    }
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case "login": return <User className="w-4 h-4 text-green-500" />;
      case "purchase": return <DollarSign className="w-4 h-4 text-[#B8962F]" />;
      case "view_artwork": return <Eye className="w-4 h-4 text-[#1A365D]" />;
      case "forensic_analysis": return <Activity className="w-4 h-4 text-purple-500" />;
      default: return <Activity className="w-4 h-4 text-gray-400" />;
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
                <BarChart3 className="w-3 h-3 mr-1" /> CRM Admin
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
              CRM Dashboard
            </h1>
            <p className="text-[#4A4A45]">
              Manage users, track activities, and analyze business metrics
            </p>
          </div>

          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="bg-[#F5F5F0]">
              <TabsTrigger 
                value="overview" 
                className="data-[state=active]:bg-[#B8962F] data-[state=active]:text-white"
              >
                <BarChart3 className="w-4 h-4 mr-2" /> Overview
              </TabsTrigger>
              <TabsTrigger 
                value="users"
                className="data-[state=active]:bg-[#B8962F] data-[state=active]:text-white"
              >
                <Users className="w-4 h-4 mr-2" /> Users
              </TabsTrigger>
              <TabsTrigger 
                value="activity"
                className="data-[state=active]:bg-[#B8962F] data-[state=active]:text-white"
              >
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
                  {/* Stats Cards */}
                  <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                    <div className="card-ivory rounded-lg p-5" data-testid="stat-users">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-[#4A4A45] text-sm">Total Users</span>
                        <Users className="w-5 h-5 text-[#B8962F]" />
                      </div>
                      <p className="text-3xl font-display text-[#1A1A18]">{analytics?.total_users || 0}</p>
                      <p className="text-xs text-[#8A8A80] mt-1">
                        +{analytics?.recent_signups_30d || 0} this month
                      </p>
                    </div>

                    <div className="card-ivory rounded-lg p-5" data-testid="stat-revenue">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-[#4A4A45] text-sm">Total Revenue</span>
                        <DollarSign className="w-5 h-5 text-[#B8962F]" />
                      </div>
                      <p className="text-3xl font-display text-[#1A1A18]">
                        ${(analytics?.revenue?.total || 0).toLocaleString()}
                      </p>
                      <p className="text-xs text-[#8A8A80] mt-1">
                        {analytics?.revenue?.transaction_count || 0} transactions
                      </p>
                    </div>

                    <div className="card-ivory rounded-lg p-5" data-testid="stat-active">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-[#4A4A45] text-sm">Active Users (7d)</span>
                        <TrendingUp className="w-5 h-5 text-green-500" />
                      </div>
                      <p className="text-3xl font-display text-[#1A1A18]">{analytics?.active_users_7d || 0}</p>
                    </div>

                    <div className="card-ivory rounded-lg p-5" data-testid="stat-subscribers">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-[#4A4A45] text-sm">Subscribers</span>
                        <Crown className="w-5 h-5 text-[#B8962F]" />
                      </div>
                      <p className="text-3xl font-display text-[#1A1A18]">
                        {(analytics?.subscription_breakdown?.connoisseur || 0) + (analytics?.subscription_breakdown?.pro_collector || 0)}
                      </p>
                    </div>
                  </div>

                  {/* Segments & Subscription Breakdown */}
                  <div className="grid lg:grid-cols-2 gap-6">
                    {/* User Segments */}
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

                    {/* Subscription Breakdown */}
                    <div className="card-ivory rounded-lg p-6">
                      <h3 className="font-display text-xl text-[#1A1A18] mb-4">Subscription Breakdown</h3>
                      <div className="space-y-3">
                        {analytics?.subscription_breakdown && Object.entries(analytics.subscription_breakdown).map(([tier, count]) => (
                          <div key={tier} className="flex items-center justify-between p-3 bg-[#F5F5F0] rounded-lg">
                            <div className="flex items-center gap-2">
                              {tier === 'pro_collector' && <Crown className="w-4 h-4 text-[#B8962F]" />}
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
              {/* Filters */}
              <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#8A8A80]" />
                  <Input
                    type="text"
                    placeholder="Search by name or email..."
                    value={searchQuery}
                    onChange={(e) => { setSearchQuery(e.target.value); setCurrentPage(1); }}
                    className="input-light pl-10"
                  />
                </div>
                <Select value={subscriptionFilter} onValueChange={(v) => { setSubscriptionFilter(v); setCurrentPage(1); }}>
                  <SelectTrigger className="w-48 bg-white border-[#E8E8E0]">
                    <SelectValue placeholder="All Subscriptions" />
                  </SelectTrigger>
                  <SelectContent className="bg-white border-[#E8E8E0]">
                    <SelectItem value="all">All Users</SelectItem>
                    <SelectItem value="short_story">Short Story</SelectItem>
                    <SelectItem value="deep_dive">Deep Dive</SelectItem>
                    <SelectItem value="connoisseur">Connoisseur</SelectItem>
                    <SelectItem value="pro_collector">Pro Collector</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Users Table */}
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
                            <th className="text-left p-4 text-sm font-medium text-[#4A4A45]">Subscription</th>
                            <th className="text-left p-4 text-sm font-medium text-[#4A4A45]">Total Spent</th>
                            <th className="text-left p-4 text-sm font-medium text-[#4A4A45]">Last Active</th>
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
                                <Badge className={u.subscription_tier ? 'badge-gold' : 'bg-gray-100 text-gray-600'}>
                                  {u.subscription_tier?.replace(/_/g, ' ') || 'Free'}
                                </Badge>
                              </td>
                              <td className="p-4 text-sm text-[#1A1A18]">
                                ${(u.total_spent || 0).toFixed(2)}
                              </td>
                              <td className="p-4 text-sm text-[#8A8A80]">
                                {u.last_active ? new Date(u.last_active).toLocaleDateString() : 'Never'}
                              </td>
                              <td className="p-4">
                                <Dialog>
                                  <DialogTrigger asChild>
                                    <Button 
                                      variant="ghost" 
                                      size="sm"
                                      onClick={() => fetchUserDetail(u.user_id)}
                                      className="text-[#B8962F]"
                                    >
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
                                            <p className="text-xs text-[#8A8A80]">Forensic Markers</p>
                                            <p className="font-display text-lg">{userDetail.stats.forensic_markers_count}</p>
                                          </div>
                                        </div>

                                        {userDetail.activities.length > 0 && (
                                          <div>
                                            <h4 className="font-medium text-[#1A1A18] mb-2">Recent Activity</h4>
                                            <ScrollArea className="h-40">
                                              <div className="space-y-2">
                                                {userDetail.activities.slice(0, 10).map((act, i) => (
                                                  <div key={i} className="flex items-center gap-2 p-2 bg-[#F5F5F0] rounded">
                                                    {getActivityIcon(act.activity_type)}
                                                    <span className="text-sm text-[#4A4A45] capitalize">{act.activity_type.replace(/_/g, ' ')}</span>
                                                    <span className="text-xs text-[#8A8A80] ml-auto">
                                                      {new Date(act.created_at).toLocaleString()}
                                                    </span>
                                                  </div>
                                                ))}
                                              </div>
                                            </ScrollArea>
                                          </div>
                                        )}
                                      </div>
                                    )}
                                  </DialogContent>
                                </Dialog>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Pagination */}
                  {totalPages > 1 && (
                    <div className="flex items-center justify-center gap-2 mt-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                        disabled={currentPage === 1}
                        className="border-[#E8E8E0]"
                      >
                        <ChevronLeft className="w-4 h-4" />
                      </Button>
                      <span className="text-sm text-[#4A4A45]">
                        Page {currentPage} of {totalPages}
                      </span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                        disabled={currentPage === totalPages}
                        className="border-[#E8E8E0]"
                      >
                        <ChevronRight className="w-4 h-4" />
                      </Button>
                    </div>
                  )}
                </>
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
