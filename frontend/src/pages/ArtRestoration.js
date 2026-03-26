import { useState, useEffect, useRef } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth, API } from "@/App";
import { useTranslation } from "react-i18next";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
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
  DialogFooter,
} from "@/components/ui/dialog";
import { toast } from "sonner";
import {
  Camera,
  Upload,
  FileText,
  Sparkles,
  ArrowLeft,
  Image,
  AlertTriangle,
  CheckCircle,
  Clock,
  Loader2,
  Eye,
  Download,
  Trash2,
  RefreshCw,
  Menu,
  X,
  User,
  LogOut,
  Shield,
  Palette,
  Layers,
  Droplets,
  Wand2
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import LanguageSelector from "@/components/LanguageSelector";

const ArtRestoration = () => {
  const { user, login, logout } = useAuth();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);
  
  // State
  const [activeTab, setActiveTab] = useState("upload");
  const [scans, setScans] = useState([]);
  const [reports, setReports] = useState([]);
  const [simulations, setSimulations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  // Upload state
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [artworkInfo, setArtworkInfo] = useState({ title: "", artist: "", notes: "" });
  
  // Analysis state
  const [analyzing, setAnalyzing] = useState(false);
  const [selectedScan, setSelectedScan] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);
  const [showReportDialog, setShowReportDialog] = useState(false);
  
  // Simulation state
  const [simulating, setSimulating] = useState(false);
  const [restorationtype, setRestorationType] = useState("full_restoration");
  const [showSimulationDialog, setShowSimulationDialog] = useState(false);
  const [currentSimulation, setCurrentSimulation] = useState(null);

  useEffect(() => {
    if (user) {
      fetchData();
    }
  }, [user, activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === "upload" || activeTab === "scans") {
        const res = await axios.get(`${API}/restoration/scans`, { withCredentials: true });
        setScans(res.data.scans || []);
      } else if (activeTab === "reports") {
        const res = await axios.get(`${API}/restoration/condition-reports`, { withCredentials: true });
        setReports(res.data.reports || []);
      } else if (activeTab === "simulations") {
        const res = await axios.get(`${API}/restoration/simulations`, { withCredentials: true });
        setSimulations(res.data.simulations || []);
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.size > 50 * 1024 * 1024) {
        toast.error("File size must be under 50MB");
        return;
      }
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !user) return;
    
    setUploading(true);
    setUploadProgress(0);
    
    try {
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64 = reader.result.split(',')[1];
        
        // Simulate progress
        const progressInterval = setInterval(() => {
          setUploadProgress(prev => Math.min(prev + 10, 90));
        }, 200);
        
        const res = await axios.post(`${API}/restoration/upload-scan`, {
          image_data: base64,
          mime_type: selectedFile.type,
          title: artworkInfo.title || "Untitled Scan",
          artist: artworkInfo.artist,
          notes: artworkInfo.notes,
          resolution: `${selectedFile.width || 'Unknown'}x${selectedFile.height || 'Unknown'}`
        }, { withCredentials: true });
        
        clearInterval(progressInterval);
        setUploadProgress(100);
        
        toast.success("Artwork scan uploaded successfully!");
        setSelectedFile(null);
        setPreviewUrl(null);
        setArtworkInfo({ title: "", artist: "", notes: "" });
        fetchData();
        setActiveTab("scans");
      };
      reader.readAsDataURL(selectedFile);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const generateConditionReport = async (scan) => {
    if (!user) return;
    
    // Check subscription
    if (!["pro_collector", "collectors_advisory"].includes(user.subscription_tier)) {
      toast.error("Digital Condition Reports require Pro Collector or Collector's Advisory subscription");
      navigate("/pricing");
      return;
    }
    
    setSelectedScan(scan);
    setAnalyzing(true);
    
    try {
      const res = await axios.post(`${API}/restoration/condition-report`, {
        image_id: scan.image_id
      }, { withCredentials: true });
      
      toast.success("Condition report generated!");
      fetchData();
      setActiveTab("reports");
      
      // Fetch and show the report
      const reportRes = await axios.get(`${API}/restoration/condition-report/${res.data.report_id}`, { withCredentials: true });
      setSelectedReport(reportRes.data);
      setShowReportDialog(true);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to generate report");
    } finally {
      setAnalyzing(false);
      setSelectedScan(null);
    }
  };

  const startRestorationSimulation = async () => {
    if (!selectedReport || !user) return;
    
    setSimulating(true);
    
    try {
      const res = await axios.post(`${API}/restoration/simulate-restoration`, {
        report_id: selectedReport.report_id,
        restoration_type: restorationtype
      }, { withCredentials: true });
      
      toast.success("Restoration simulation completed!");
      setShowReportDialog(false);
      
      // Fetch and show simulation
      const simRes = await axios.get(`${API}/restoration/simulation/${res.data.simulation_id}`, { withCredentials: true });
      setCurrentSimulation(simRes.data);
      setShowSimulationDialog(true);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Simulation failed");
    } finally {
      setSimulating(false);
    }
  };

  const viewReport = async (report) => {
    try {
      const res = await axios.get(`${API}/restoration/condition-report/${report.report_id}`, { withCredentials: true });
      setSelectedReport(res.data);
      setShowReportDialog(true);
    } catch (error) {
      toast.error("Failed to load report");
    }
  };

  const viewSimulation = async (simulation) => {
    try {
      const res = await axios.get(`${API}/restoration/simulation/${simulation.simulation_id}`, { withCredentials: true });
      setCurrentSimulation(res.data);
      setShowSimulationDialog(true);
    } catch (error) {
      toast.error("Failed to load simulation");
    }
  };

  const getConditionColor = (condition) => {
    switch (condition) {
      case "excellent": return "text-green-400 bg-green-900/30";
      case "good": return "text-blue-400 bg-blue-900/30";
      case "fair": return "text-yellow-400 bg-yellow-900/30";
      case "poor": return "text-orange-400 bg-orange-900/30";
      case "critical": return "text-red-400 bg-red-900/30";
      default: return "text-gray-400 bg-gray-900/30";
    }
  };

  const getConditionIcon = (condition) => {
    switch (condition) {
      case "excellent":
      case "good":
        return <CheckCircle className="w-4 h-4" />;
      case "fair":
        return <AlertTriangle className="w-4 h-4" />;
      case "poor":
      case "critical":
        return <AlertTriangle className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-8">
          <Wand2 className="w-16 h-16 mx-auto text-[#D4AF37] mb-6" />
          <h1 className="font-display text-3xl text-[#F5F5F0] mb-4">Art Restoration Studio</h1>
          <p className="text-[#A8A8A0] mb-6">
            Access AI-powered condition reports and restoration simulations. Sign in to get started.
          </p>
          <Button onClick={login} className="btn-gold">
            Sign In with Google
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505]">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass-dark border-b border-[#1a1a1a]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 lg:h-20">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-10 h-10 rounded bg-gradient-to-br from-[#D4AF37] to-[#B8860B] flex items-center justify-center">
                <span className="font-display text-white text-xl font-bold">E</span>
              </div>
              <span className="font-display text-xl text-[#F5F5F0] hidden sm:block">Emaira.Art</span>
            </Link>

            <div className="hidden md:flex items-center gap-4">
              <Badge className="badge-forensic">
                <Wand2 className="w-3 h-3 mr-1" /> Restoration Studio
              </Badge>
            </div>

            <div className="hidden md:flex items-center gap-4">
              <LanguageSelector variant="dark" />
              {user && (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="flex items-center gap-2 text-[#A8A8A0]">
                      {user.picture ? (
                        <img src={user.picture} alt={user.name} className="w-8 h-8 rounded-full" />
                      ) : (
                        <User className="w-5 h-5" />
                      )}
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="bg-[#0a0a0a] border-[#1a1a1a]">
                    <DropdownMenuItem onClick={() => navigate('/dashboard')} className="cursor-pointer text-[#F5F5F0]">
                      <User className="w-4 h-4 mr-2" /> Dashboard
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={logout} className="cursor-pointer text-[#F5F5F0]">
                      <LogOut className="w-4 h-4 mr-2" /> Logout
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              )}
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
            <Button 
              variant="ghost" 
              onClick={() => navigate('/dashboard')} 
              className="text-[#A8A8A0] hover:text-[#F5F5F0] mb-4 -ml-4"
            >
              <ArrowLeft className="w-4 h-4 mr-2" /> Back to Dashboard
            </Button>
            <h1 className="font-display text-3xl lg:text-4xl text-[#F5F5F0] mb-2" data-testid="restoration-title">
              Art Restoration Studio
            </h1>
            <p className="text-[#A8A8A0]">
              Upload high-resolution scans for AI-powered condition reports and restoration simulations
            </p>
            
            {/* Subscription Badge */}
            {user.subscription_tier && (
              <Badge className={`mt-3 ${
                user.subscription_tier === "collectors_advisory" 
                  ? "bg-purple-900/30 text-purple-400" 
                  : user.subscription_tier === "pro_collector"
                  ? "bg-[#D4AF37]/20 text-[#D4AF37]"
                  : "bg-gray-900/30 text-gray-400"
              }`}>
                <Shield className="w-3 h-3 mr-1" />
                {user.subscription_tier === "collectors_advisory" 
                  ? "Unlimited Restorations" 
                  : user.subscription_tier === "pro_collector"
                  ? "5 Simulations/Month"
                  : "Upgrade for Full Access"}
              </Badge>
            )}
          </div>

          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="bg-[#111] border border-[#1a1a1a]">
              <TabsTrigger value="upload" className="data-[state=active]:bg-[#D4AF37] data-[state=active]:text-black" data-testid="tab-upload">
                <Upload className="w-4 h-4 mr-2" /> Upload Scan
              </TabsTrigger>
              <TabsTrigger value="scans" className="data-[state=active]:bg-[#D4AF37] data-[state=active]:text-black" data-testid="tab-scans">
                <Image className="w-4 h-4 mr-2" /> My Scans
              </TabsTrigger>
              <TabsTrigger value="reports" className="data-[state=active]:bg-[#D4AF37] data-[state=active]:text-black" data-testid="tab-reports">
                <FileText className="w-4 h-4 mr-2" /> Condition Reports
              </TabsTrigger>
              <TabsTrigger value="simulations" className="data-[state=active]:bg-[#D4AF37] data-[state=active]:text-black" data-testid="tab-simulations">
                <Sparkles className="w-4 h-4 mr-2" /> Restorations
              </TabsTrigger>
            </TabsList>

            {/* Upload Tab */}
            <TabsContent value="upload">
              <div className="grid lg:grid-cols-2 gap-8">
                {/* Upload Area */}
                <div className="card-obsidian rounded-xl p-6">
                  <h3 className="font-display text-xl text-[#F5F5F0] mb-4">Upload Artwork Scan</h3>
                  <p className="text-sm text-[#A8A8A0] mb-6">
                    For best results, use a high-resolution camera (12MP+) with good lighting. 
                    Supported formats: JPEG, PNG, HEIC.
                  </p>
                  
                  {previewUrl ? (
                    <div className="relative mb-6">
                      <img 
                        src={previewUrl} 
                        alt="Preview" 
                        className="w-full h-64 object-contain bg-[#0a0a0a] rounded-lg"
                      />
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => { setSelectedFile(null); setPreviewUrl(null); }}
                        className="absolute top-2 right-2 bg-black/50 text-white"
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  ) : (
                    <div 
                      className="border-2 border-dashed border-[#333] rounded-lg p-8 text-center mb-6 hover:border-[#D4AF37] transition-colors cursor-pointer"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      <Upload className="w-12 h-12 mx-auto text-[#666] mb-4" />
                      <p className="text-[#A8A8A0] mb-2">Drag & drop or click to upload</p>
                      <p className="text-xs text-[#666]">Max 50MB • JPEG, PNG, HEIC</p>
                    </div>
                  )}
                  
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/jpeg,image/png,image/heic,image/heif"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  
                  <div className="flex gap-3 mb-6">
                    <Button
                      variant="outline"
                      onClick={() => fileInputRef.current?.click()}
                      className="flex-1 border-[#333] text-[#A8A8A0]"
                    >
                      <Upload className="w-4 h-4 mr-2" /> Choose File
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => cameraInputRef.current?.click()}
                      className="flex-1 border-[#333] text-[#A8A8A0]"
                    >
                      <Camera className="w-4 h-4 mr-2" /> Take Photo
                    </Button>
                    <input
                      ref={cameraInputRef}
                      type="file"
                      accept="image/*"
                      capture="environment"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                  </div>
                  
                  {uploading && (
                    <div className="mb-6">
                      <Progress value={uploadProgress} className="h-2" />
                      <p className="text-xs text-[#666] mt-2 text-center">Uploading... {uploadProgress}%</p>
                    </div>
                  )}
                </div>

                {/* Artwork Info */}
                <div className="card-obsidian rounded-xl p-6">
                  <h3 className="font-display text-xl text-[#F5F5F0] mb-4">Artwork Information</h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm text-[#A8A8A0]">Artwork Title *</label>
                      <Input
                        value={artworkInfo.title}
                        onChange={(e) => setArtworkInfo({ ...artworkInfo, title: e.target.value })}
                        placeholder="e.g., Portrait of a Lady"
                        className="mt-1 bg-[#111] border-[#1a1a1a] text-[#F5F5F0]"
                      />
                    </div>
                    <div>
                      <label className="text-sm text-[#A8A8A0]">Artist (if known)</label>
                      <Input
                        value={artworkInfo.artist}
                        onChange={(e) => setArtworkInfo({ ...artworkInfo, artist: e.target.value })}
                        placeholder="e.g., Unknown, 19th Century"
                        className="mt-1 bg-[#111] border-[#1a1a1a] text-[#F5F5F0]"
                      />
                    </div>
                    <div>
                      <label className="text-sm text-[#A8A8A0]">Notes / Concerns</label>
                      <Textarea
                        value={artworkInfo.notes}
                        onChange={(e) => setArtworkInfo({ ...artworkInfo, notes: e.target.value })}
                        placeholder="Any visible damage, concerns, or context..."
                        className="mt-1 bg-[#111] border-[#1a1a1a] text-[#F5F5F0] min-h-[100px]"
                      />
                    </div>
                  </div>
                  
                  <Button
                    onClick={handleUpload}
                    disabled={!selectedFile || uploading}
                    className="w-full mt-6 btn-gold"
                    data-testid="upload-btn"
                  >
                    {uploading ? (
                      <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Uploading...</>
                    ) : (
                      <><Upload className="w-4 h-4 mr-2" /> Upload Scan</>
                    )}
                  </Button>
                </div>
              </div>
            </TabsContent>

            {/* Scans Tab */}
            <TabsContent value="scans">
              {loading ? (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="skeleton-dark h-64 rounded-lg"></div>
                  ))}
                </div>
              ) : scans.length === 0 ? (
                <div className="card-obsidian rounded-xl p-12 text-center">
                  <Image className="w-16 h-16 mx-auto text-[#333] mb-4" />
                  <p className="text-[#A8A8A0] mb-4">No artwork scans yet</p>
                  <Button onClick={() => setActiveTab("upload")} className="btn-gold">
                    Upload Your First Scan
                  </Button>
                </div>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {scans.map((scan) => (
                    <div key={scan.image_id} className="card-obsidian rounded-xl overflow-hidden">
                      <img
                        src={scan.image_url}
                        alt={scan.title}
                        className="w-full h-48 object-cover"
                      />
                      <div className="p-4">
                        <h4 className="font-medium text-[#F5F5F0] mb-1">{scan.title}</h4>
                        {scan.artist && <p className="text-sm text-[#A8A8A0] mb-2">{scan.artist}</p>}
                        <p className="text-xs text-[#666] mb-4">
                          {new Date(scan.created_at).toLocaleDateString()}
                        </p>
                        <Button
                          onClick={() => generateConditionReport(scan)}
                          disabled={analyzing && selectedScan?.image_id === scan.image_id}
                          className="w-full btn-gold"
                          data-testid={`analyze-${scan.image_id}`}
                        >
                          {analyzing && selectedScan?.image_id === scan.image_id ? (
                            <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Analyzing...</>
                          ) : (
                            <><FileText className="w-4 h-4 mr-2" /> Generate Report</>
                          )}
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* Reports Tab */}
            <TabsContent value="reports">
              {loading ? (
                <div className="space-y-4">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="skeleton-dark h-24 rounded-lg"></div>
                  ))}
                </div>
              ) : reports.length === 0 ? (
                <div className="card-obsidian rounded-xl p-12 text-center">
                  <FileText className="w-16 h-16 mx-auto text-[#333] mb-4" />
                  <p className="text-[#A8A8A0] mb-4">No condition reports yet</p>
                  <Button onClick={() => setActiveTab("scans")} className="btn-gold">
                    Analyze an Artwork
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {reports.map((report) => (
                    <div key={report.report_id} className="card-obsidian rounded-xl p-6">
                      <div className="flex items-start gap-4">
                        <img
                          src={report.image_url}
                          alt={report.title}
                          className="w-24 h-24 object-cover rounded-lg"
                        />
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h4 className="font-display text-lg text-[#F5F5F0]">{report.title}</h4>
                            <Badge className={getConditionColor(report.overall_condition)}>
                              {getConditionIcon(report.overall_condition)}
                              <span className="ml-1 capitalize">{report.overall_condition || "Pending"}</span>
                            </Badge>
                          </div>
                          {report.artist && <p className="text-sm text-[#A8A8A0]">{report.artist}</p>}
                          <div className="flex items-center gap-4 mt-2">
                            <span className="text-sm text-[#666]">
                              Score: <span className="text-[#D4AF37] font-mono">{report.condition_score || "—"}/100</span>
                            </span>
                            <span className="text-sm text-[#666]">
                              {report.damage_assessment?.length || 0} issues found
                            </span>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() => viewReport(report)}
                            className="btn-gold"
                          >
                            <Eye className="w-4 h-4 mr-1" /> View
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* Simulations Tab */}
            <TabsContent value="simulations">
              {loading ? (
                <div className="grid md:grid-cols-2 gap-4">
                  {[...Array(2)].map((_, i) => (
                    <div key={i} className="skeleton-dark h-48 rounded-lg"></div>
                  ))}
                </div>
              ) : simulations.length === 0 ? (
                <div className="card-obsidian rounded-xl p-12 text-center">
                  <Sparkles className="w-16 h-16 mx-auto text-[#333] mb-4" />
                  <p className="text-[#A8A8A0] mb-4">No restoration simulations yet</p>
                  <Button onClick={() => setActiveTab("reports")} className="btn-gold">
                    Start from a Condition Report
                  </Button>
                </div>
              ) : (
                <div className="grid md:grid-cols-2 gap-6">
                  {simulations.map((sim) => (
                    <div key={sim.simulation_id} className="card-obsidian rounded-xl overflow-hidden">
                      <div className="grid grid-cols-2">
                        <div className="relative">
                          <img
                            src={sim.original_image_url}
                            alt="Before"
                            className="w-full h-48 object-cover"
                          />
                          <span className="absolute bottom-2 left-2 bg-black/70 px-2 py-1 text-xs text-white rounded">Before</span>
                        </div>
                        <div className="relative">
                          {sim.restored_image_url ? (
                            <img
                              src={sim.restored_image_url}
                              alt="After"
                              className="w-full h-48 object-cover"
                            />
                          ) : (
                            <div className="w-full h-48 bg-[#111] flex items-center justify-center">
                              <Loader2 className="w-8 h-8 text-[#666] animate-spin" />
                            </div>
                          )}
                          <span className="absolute bottom-2 left-2 bg-[#D4AF37]/90 px-2 py-1 text-xs text-black rounded">After</span>
                        </div>
                      </div>
                      <div className="p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge className="bg-[#D4AF37]/20 text-[#D4AF37] capitalize">
                            {sim.restoration_type?.replace("_", " ")}
                          </Badge>
                          <Badge className={sim.status === "completed" ? "bg-green-900/30 text-green-400" : "bg-yellow-900/30 text-yellow-400"}>
                            {sim.status}
                          </Badge>
                        </div>
                        <p className="text-xs text-[#666] mb-3">
                          AI Confidence: {((sim.ai_confidence || 0) * 100).toFixed(0)}%
                        </p>
                        <Button
                          size="sm"
                          onClick={() => viewSimulation(sim)}
                          className="w-full btn-gold"
                        >
                          <Eye className="w-4 h-4 mr-1" /> View Details
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* Condition Report Dialog */}
      <Dialog open={showReportDialog} onOpenChange={setShowReportDialog}>
        <DialogContent className="bg-[#0a0a0a] border-[#1a1a1a] text-[#F5F5F0] max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="font-display text-2xl">Digital Condition Report</DialogTitle>
          </DialogHeader>
          
          {selectedReport && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex gap-4">
                <img
                  src={selectedReport.image_url}
                  alt={selectedReport.title}
                  className="w-32 h-32 object-cover rounded-lg"
                />
                <div>
                  <h3 className="font-display text-xl">{selectedReport.title}</h3>
                  {selectedReport.artist && <p className="text-[#A8A8A0]">{selectedReport.artist}</p>}
                  <div className="flex gap-2 mt-2">
                    <Badge className={getConditionColor(selectedReport.overall_condition)}>
                      {getConditionIcon(selectedReport.overall_condition)}
                      <span className="ml-1 capitalize">{selectedReport.overall_condition}</span>
                    </Badge>
                    <Badge className="bg-[#D4AF37]/20 text-[#D4AF37]">
                      Score: {selectedReport.condition_score}/100
                    </Badge>
                  </div>
                </div>
              </div>

              {/* Damage Assessment */}
              {selectedReport.damage_assessment?.length > 0 && (
                <div>
                  <h4 className="font-medium text-[#F5F5F0] mb-3 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-orange-400" /> Damage Assessment
                  </h4>
                  <div className="space-y-2">
                    {selectedReport.damage_assessment.map((damage, i) => (
                      <div key={i} className="p-3 bg-[#111] rounded-lg border border-[#1a1a1a]">
                        <div className="flex items-center gap-2">
                          <Badge className={
                            damage.severity === "high" ? "bg-red-900/30 text-red-400" :
                            damage.severity === "medium" ? "bg-yellow-900/30 text-yellow-400" :
                            "bg-blue-900/30 text-blue-400"
                          }>
                            {damage.severity || "Unknown"} severity
                          </Badge>
                          <span className="text-sm text-[#F5F5F0]">{damage.type}</span>
                        </div>
                        <p className="text-xs text-[#A8A8A0] mt-1">{damage.description}</p>
                        {damage.location && <p className="text-xs text-[#666] mt-1">Location: {damage.location}</p>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {selectedReport.recommendations?.length > 0 && (
                <div>
                  <h4 className="font-medium text-[#F5F5F0] mb-3 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-400" /> Conservation Recommendations
                  </h4>
                  <ul className="space-y-2">
                    {selectedReport.recommendations.map((rec, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-[#A8A8A0]">
                        <span className="text-[#D4AF37]">•</span> {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Estimated Cost */}
              {selectedReport.estimated_restoration_cost && (
                <div className="p-4 bg-[#D4AF37]/10 border border-[#D4AF37]/30 rounded-lg">
                  <p className="text-sm text-[#A8A8A0]">Estimated Restoration Cost</p>
                  <p className="font-display text-xl text-[#D4AF37]">{selectedReport.estimated_restoration_cost}</p>
                </div>
              )}

              {/* Restoration Simulation */}
              <div className="border-t border-[#1a1a1a] pt-6">
                <h4 className="font-medium text-[#F5F5F0] mb-4 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-[#D4AF37]" /> AI Restoration Simulation
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                  {[
                    { value: "cleaning", label: "Cleaning", icon: Droplets },
                    { value: "inpainting", label: "Inpainting", icon: Palette },
                    { value: "color_correction", label: "Color Fix", icon: Layers },
                    { value: "full_restoration", label: "Full Restore", icon: Wand2 }
                  ].map((type) => (
                    <button
                      key={type.value}
                      onClick={() => setRestorationType(type.value)}
                      className={`p-3 rounded-lg border text-center transition-colors ${
                        restorationtype === type.value
                          ? "border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]"
                          : "border-[#1a1a1a] text-[#A8A8A0] hover:border-[#333]"
                      }`}
                    >
                      <type.icon className="w-5 h-5 mx-auto mb-1" />
                      <span className="text-xs">{type.label}</span>
                    </button>
                  ))}
                </div>
                <Button
                  onClick={startRestorationSimulation}
                  disabled={simulating}
                  className="w-full btn-gold"
                >
                  {simulating ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Generating Simulation...</>
                  ) : (
                    <><Sparkles className="w-4 h-4 mr-2" /> Generate Restoration Preview</>
                  )}
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Simulation Dialog */}
      <Dialog open={showSimulationDialog} onOpenChange={setShowSimulationDialog}>
        <DialogContent className="bg-[#0a0a0a] border-[#1a1a1a] text-[#F5F5F0] max-w-4xl">
          <DialogHeader>
            <DialogTitle className="font-display text-2xl">Restoration Simulation</DialogTitle>
          </DialogHeader>
          
          {currentSimulation && (
            <div className="space-y-6">
              {/* Before/After Comparison */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-[#A8A8A0] mb-2 text-center">Before</p>
                  <img
                    src={currentSimulation.original_image_url}
                    alt="Before"
                    className="w-full h-64 object-contain bg-[#111] rounded-lg"
                  />
                </div>
                <div>
                  <p className="text-sm text-[#A8A8A0] mb-2 text-center">After (AI Simulation)</p>
                  {currentSimulation.restored_image_url ? (
                    <img
                      src={currentSimulation.restored_image_url}
                      alt="After"
                      className="w-full h-64 object-contain bg-[#111] rounded-lg"
                    />
                  ) : (
                    <div className="w-full h-64 bg-[#111] rounded-lg flex items-center justify-center">
                      <p className="text-[#666]">Visualization pending</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Details */}
              <div className="grid md:grid-cols-2 gap-4">
                <div className="p-4 bg-[#111] rounded-lg">
                  <p className="text-sm text-[#A8A8A0] mb-1">Restoration Type</p>
                  <p className="font-medium text-[#F5F5F0] capitalize">
                    {currentSimulation.restoration_type?.replace("_", " ")}
                  </p>
                </div>
                <div className="p-4 bg-[#111] rounded-lg">
                  <p className="text-sm text-[#A8A8A0] mb-1">AI Confidence</p>
                  <p className="font-medium text-[#D4AF37]">
                    {((currentSimulation.ai_confidence || 0) * 100).toFixed(0)}%
                  </p>
                </div>
              </div>

              {/* Techniques Applied */}
              {currentSimulation.techniques_applied?.length > 0 && (
                <div>
                  <p className="text-sm text-[#A8A8A0] mb-2">Techniques Applied</p>
                  <div className="flex flex-wrap gap-2">
                    {currentSimulation.techniques_applied.map((tech, i) => (
                      <Badge key={i} className="bg-[#1a1a1a] text-[#F5F5F0]">
                        {typeof tech === 'string' ? tech : tech.name || tech}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Notes */}
              {currentSimulation.notes && (
                <div className="p-4 bg-[#111] rounded-lg">
                  <p className="text-sm text-[#A8A8A0] mb-2">AI Analysis Notes</p>
                  <p className="text-sm text-[#F5F5F0] whitespace-pre-wrap">
                    {currentSimulation.notes.substring(0, 500)}
                    {currentSimulation.notes.length > 500 && "..."}
                  </p>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ArtRestoration;
