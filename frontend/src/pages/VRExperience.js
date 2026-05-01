import { useState, useEffect, useRef, useCallback } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useAuth, API } from "@/App";
import { useTranslation } from "react-i18next";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Progress } from "@/components/ui/progress";
import {
  ArrowLeft,
  Eye,
  Fingerprint,
  Palette,
  FileSignature,
  Grid3X3,
  Play,
  Pause,
  Volume2,
  VolumeX,
  Maximize,
  Minimize,
  RotateCcw,
  Loader2,
  Sparkles,
  X,
  ChevronRight,
  ChevronLeft,
  Smartphone,
  Monitor,
  Glasses,
  ZoomIn,
  ZoomOut,
  RotateCw,
  Info,
  Download,
  Share2,
  Bookmark,
  BookmarkCheck
} from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";

const VRExperience = () => {
  const { storyId } = useParams();
  const { user } = useAuth();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const containerRef = useRef(null);
  const imageRef = useRef(null);
  
  // Core state
  const [story, setStory] = useState(null);
  const [artwork, setArtwork] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState("narrative");
  
  // Playback state
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentScene, setCurrentScene] = useState(0);
  const [progress, setProgress] = useState(0);
  
  // Forensic state
  const [analysisType, setAnalysisType] = useState("pigment");
  const [forensicResult, setForensicResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [generatingViz, setGeneratingViz] = useState(false);
  const [visualization, setVisualization] = useState(null);
  const [forensicReport, setForensicReport] = useState(null);
  
  // UI state
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [showMobilePanel, setShowMobilePanel] = useState(false);
  const [vrMode, setVrMode] = useState("desktop"); // desktop, mobile, vr
  const [isBookmarked, setIsBookmarked] = useState(false);
  
  // Image manipulation state
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [imagePosition, setImagePosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // Check for VR support and mobile
  useEffect(() => {
    const checkDevice = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      
      // Check for WebXR support (VR headsets)
      if (navigator.xr) {
        navigator.xr.isSessionSupported('immersive-vr').then((supported) => {
          if (supported) {
            setVrMode("vr");
          }
        }).catch(() => {});
      }
    };
    
    checkDevice();
    window.addEventListener('resize', checkDevice);
    return () => window.removeEventListener('resize', checkDevice);
  }, []);

  // Auto-advance scenes when playing
  useEffect(() => {
    let interval;
    if (isPlaying && story?.narrative_content) {
      const sceneDuration = 60000 / story.narrative_content.length; // Distribute time across scenes
      interval = setInterval(() => {
        setProgress((prev) => {
          const newProgress = prev + (100 / (sceneDuration / 100));
          if (newProgress >= 100) {
            // Move to next scene
            if (currentScene < story.narrative_content.length - 1) {
              setCurrentScene((s) => s + 1);
              return 0;
            } else {
              setIsPlaying(false);
              return 100;
            }
          }
          return newProgress;
        });
      }, 100);
    }
    return () => clearInterval(interval);
  }, [isPlaying, currentScene, story]);

  // Fullscreen handling
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };
    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  const fetchData = useCallback(async () => {
    try {
      const storyResponse = await axios.get(`${API}/stories/${storyId}`, {
        withCredentials: true
      });
      setStory(storyResponse.data);

      if (storyResponse.data.artwork_id) {
        const artworkResponse = await axios.get(`${API}/artworks/${storyResponse.data.artwork_id}`);
        setArtwork(artworkResponse.data);
        
        // Fetch forensic report if user has access
        try {
          const reportResponse = await axios.get(
            `${API}/forensics/report/${storyResponse.data.artwork_id}`,
            { withCredentials: true }
          );
          setForensicReport(reportResponse.data);
        } catch (e) {
          // User may not have access - that's okay
        }
      }
    } catch (error) {
      console.error("Error:", error);
      toast.error("Failed to load experience");
      navigate('/gallery');
    } finally {
      setLoading(false);
    }
  }, [storyId, navigate]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const runForensicAnalysis = async (type) => {
    if (!artwork) return;
    
    setAnalyzing(true);
    setAnalysisType(type);
    
    try {
      const response = await axios.post(
        `${API}/forensics/analyze`,
        {
          artwork_id: artwork.artwork_id,
          analysis_type: type
        },
        { withCredentials: true }
      );
      setForensicResult(response.data);
      toast.success("Analysis complete");
    } catch (error) {
      console.error("Analysis error:", error);
      if (error.response?.status === 403) {
        toast.error("Forensic analysis requires Deep Dive or subscription access");
      } else {
        toast.error("Analysis failed. Please try again.");
      }
    } finally {
      setAnalyzing(false);
    }
  };

  const generateVisualization = async (type) => {
    if (!artwork) return;
    
    setGeneratingViz(true);
    
    try {
      const response = await axios.post(
        `${API}/forensics/generate-visualization`,
        {
          artwork_id: artwork.artwork_id,
          analysis_type: type
        },
        { withCredentials: true }
      );
      setVisualization(response.data);
      toast.success("Visualization generated");
    } catch (error) {
      console.error("Visualization error:", error);
      toast.error("Failed to generate visualization");
    } finally {
      setGeneratingViz(false);
    }
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  };

  const handleZoomIn = () => setZoom((z) => Math.min(z + 0.25, 3));
  const handleZoomOut = () => setZoom((z) => Math.max(z - 0.25, 0.5));
  const handleRotate = () => setRotation((r) => (r + 90) % 360);
  const handleReset = () => {
    setZoom(1);
    setRotation(0);
    setImagePosition({ x: 0, y: 0 });
  };

  const handleMouseDown = (e) => {
    if (zoom > 1) {
      setIsDragging(true);
      setDragStart({ x: e.clientX - imagePosition.x, y: e.clientY - imagePosition.y });
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      setImagePosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  };

  const handleMouseUp = () => setIsDragging(false);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleNextScene = () => {
    if (story?.narrative_content && currentScene < story.narrative_content.length - 1) {
      setCurrentScene(currentScene + 1);
      setProgress(0);
    }
  };

  const handlePrevScene = () => {
    if (currentScene > 0) {
      setCurrentScene(currentScene - 1);
      setProgress(0);
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `${artwork?.title} - Emaira.Art`,
          text: `Experience the story of ${artwork?.title} by ${artwork?.artist}`,
          url: window.location.href
        });
      } catch (e) {
        // User cancelled or error
      }
    } else {
      navigator.clipboard.writeText(window.location.href);
      toast.success("Link copied to clipboard");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#080d1c] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-2 border-[#D4AF37] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-[#A8A8A0] font-display text-lg">Preparing your experience...</p>
          <p className="text-[#666660] text-sm mt-2">Loading artwork and narrative</p>
        </div>
      </div>
    );
  }

  if (!story || !artwork) {
    return (
      <div className="min-h-screen bg-[#080d1c] flex items-center justify-center">
        <div className="text-center">
          <p className="text-[#A8A8A0] mb-4">Experience not found</p>
          <Button onClick={() => navigate('/gallery')} className="btn-gold">
            Back to Gallery
          </Button>
        </div>
      </div>
    );
  }

  const narrativeContent = story.narrative_content || [];
  const currentSceneData = narrativeContent[currentScene];

  // Mobile Layout
  if (isMobile) {
    return (
      <div className="min-h-screen bg-[#080d1c] flex flex-col" ref={containerRef}>
        {/* Mobile Top Bar */}
        <div className="fixed top-0 left-0 right-0 z-50 glass-dark">
          <div className="flex items-center justify-between h-14 px-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate(`/story/${storyId}`)}
              className="text-[#A8A8A0] -ml-2"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            
            <div className="flex-1 text-center px-2">
              <p className="text-xs text-[#A8A8A0] truncate">{artwork.artist}</p>
              <h1 className="font-display text-sm text-[#F5F5F0] truncate">{artwork.title}</h1>
            </div>

            <div className="flex items-center gap-1">
              <Button variant="ghost" size="sm" onClick={handleShare} className="text-[#A8A8A0]">
                <Share2 className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm" onClick={toggleFullscreen} className="text-[#A8A8A0]">
                {isFullscreen ? <Minimize className="w-4 h-4" /> : <Maximize className="w-4 h-4" />}
              </Button>
            </div>
          </div>
        </div>

        {/* Artwork Display */}
        <div className="flex-1 pt-14 pb-40 flex items-center justify-center p-4">
          <div 
            className="relative w-full max-w-md aspect-[3/4] overflow-hidden rounded-lg"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            onTouchStart={(e) => handleMouseDown(e.touches[0])}
            onTouchMove={(e) => handleMouseMove(e.touches[0])}
            onTouchEnd={handleMouseUp}
          >
            <img
              ref={imageRef}
              src={artwork.image_url}
              alt={artwork.title}
              className="w-full h-full object-contain transition-transform duration-200"
              style={{
                transform: `scale(${zoom}) rotate(${rotation}deg) translate(${imagePosition.x / zoom}px, ${imagePosition.y / zoom}px)`,
                cursor: zoom > 1 ? 'grab' : 'default'
              }}
              draggable={false}
            />
            
            {/* Forensic Overlay */}
            {activeView === 'forensic' && (
              <div className="absolute inset-0 rounded-lg forensic-scan pointer-events-none">
                <div className="absolute inset-0 grid grid-cols-3 grid-rows-3">
                  {[...Array(9)].map((_, i) => (
                    <div key={i} className="border border-[#00F0FF]/20"></div>
                  ))}
                </div>
                <div className="absolute top-2 left-2">
                  <Badge className="badge-forensic text-xs">
                    {analysisType === 'pigment' && <Palette className="w-3 h-3 mr-1" />}
                    {analysisType === 'signature' && <FileSignature className="w-3 h-3 mr-1" />}
                    {analysisType === 'canvas' && <Grid3X3 className="w-3 h-3 mr-1" />}
                    {analysisType} Mode
                  </Badge>
                </div>
              </div>
            )}

            {/* Zoom Controls */}
            <div className="absolute bottom-2 right-2 flex gap-1">
              <Button size="sm" variant="ghost" onClick={handleZoomOut} className="w-8 h-8 bg-black/50 text-white">
                <ZoomOut className="w-4 h-4" />
              </Button>
              <Button size="sm" variant="ghost" onClick={handleZoomIn} className="w-8 h-8 bg-black/50 text-white">
                <ZoomIn className="w-4 h-4" />
              </Button>
              <Button size="sm" variant="ghost" onClick={handleReset} className="w-8 h-8 bg-black/50 text-white">
                <RotateCcw className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* Mobile Bottom Panel */}
        <div className="fixed bottom-0 left-0 right-0 glass-dark border-t border-[#1a1a1a]">
          {/* View Toggle */}
          <div className="flex border-b border-[#1a1a1a]">
            <button
              onClick={() => setActiveView('narrative')}
              className={`flex-1 py-3 text-sm font-medium flex items-center justify-center gap-2 ${
                activeView === 'narrative' ? 'text-[#D4AF37] bg-[#D4AF37]/10' : 'text-[#A8A8A0]'
              }`}
            >
              <Eye className="w-4 h-4" /> Narrative
            </button>
            <button
              onClick={() => setActiveView('forensic')}
              className={`flex-1 py-3 text-sm font-medium flex items-center justify-center gap-2 ${
                activeView === 'forensic' ? 'text-[#00F0FF] bg-[#00F0FF]/10' : 'text-[#A8A8A0]'
              }`}
            >
              <Fingerprint className="w-4 h-4" /> Forensic
            </button>
          </div>

          {activeView === 'narrative' ? (
            <div className="p-4">
              {currentSceneData && (
                <div className="mb-4">
                  <Badge className="badge-gold mb-2 text-xs">{currentSceneData.scene}</Badge>
                  <p className="text-[#F5F5F0] text-sm line-clamp-2">{currentSceneData.narration}</p>
                </div>
              )}
              
              {/* Progress */}
              <Progress value={progress} className="h-1 mb-3" />
              
              {/* Controls */}
              <div className="flex items-center justify-between">
                <span className="text-xs text-[#666660]">
                  {currentScene + 1} / {narrativeContent.length}
                </span>
                <div className="flex items-center gap-2">
                  <Button size="sm" variant="ghost" onClick={handlePrevScene} disabled={currentScene === 0} className="text-[#A8A8A0]">
                    <ChevronLeft className="w-5 h-5" />
                  </Button>
                  <Button size="sm" onClick={handlePlayPause} className="btn-gold w-10 h-10 rounded-full">
                    {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
                  </Button>
                  <Button size="sm" variant="ghost" onClick={handleNextScene} disabled={currentScene >= narrativeContent.length - 1} className="text-[#A8A8A0]">
                    <ChevronRight className="w-5 h-5" />
                  </Button>
                </div>
                <Button size="sm" variant="ghost" onClick={() => setIsMuted(!isMuted)} className="text-[#A8A8A0]">
                  {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                </Button>
              </div>
            </div>
          ) : (
            <div className="p-4">
              {/* Analysis Type Selector */}
              <div className="flex gap-2 mb-3">
                {['pigment', 'signature', 'canvas'].map((type) => (
                  <button
                    key={type}
                    onClick={() => setAnalysisType(type)}
                    className={`flex-1 py-2 px-3 rounded-lg text-xs font-medium flex items-center justify-center gap-1 ${
                      analysisType === type 
                        ? 'bg-[#00F0FF]/20 text-[#00F0FF] border border-[#00F0FF]/50' 
                        : 'bg-[#111] text-[#A8A8A0] border border-[#1a1a1a]'
                    }`}
                  >
                    {type === 'pigment' && <Palette className="w-3 h-3" />}
                    {type === 'signature' && <FileSignature className="w-3 h-3" />}
                    {type === 'canvas' && <Grid3X3 className="w-3 h-3" />}
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </button>
                ))}
              </div>

              {/* Analysis Result Preview */}
              {forensicResult && (
                <div className="mb-3 p-2 bg-[#00F0FF]/5 border border-[#00F0FF]/20 rounded-lg">
                  <p className="text-xs text-[#F5F5F0] line-clamp-2">
                    {forensicResult.results?.summary?.substring(0, 100)}...
                  </p>
                </div>
              )}

              {/* Action Button */}
              <Button
                onClick={() => runForensicAnalysis(analysisType)}
                disabled={analyzing}
                className="w-full btn-forensic"
              >
                {analyzing ? (
                  <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Analyzing...</>
                ) : (
                  <><Fingerprint className="w-4 h-4 mr-2" /> Run AI Analysis</>
                )}
              </Button>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Desktop Layout
  return (
    <div className="min-h-screen bg-[#080d1c] flex flex-col" ref={containerRef}>
      {/* Top Bar */}
      <div className="fixed top-0 left-0 right-0 z-50 glass-dark">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                onClick={() => navigate(`/story/${storyId}`)}
                className="text-[#A8A8A0] hover:text-[#F5F5F0]"
                data-testid="back-btn"
              >
                <ArrowLeft className="w-5 h-5" />
              </Button>
              <div>
                <p className="text-sm text-[#A8A8A0]">{artwork.artist}</p>
                <h1 className="font-display text-lg text-[#F5F5F0]">{artwork.title}</h1>
              </div>
            </div>

            {/* View Toggle */}
            <div className="vr-toggle">
              <div 
                className={`vr-toggle-indicator ${activeView}`}
                style={{
                  width: '50%',
                  left: activeView === 'narrative' ? '4px' : 'calc(50% - 0px)'
                }}
              />
              <button
                onClick={() => setActiveView('narrative')}
                className={`vr-toggle-option ${activeView === 'narrative' ? 'active' : 'text-[#A8A8A0]'}`}
                data-testid="narrative-toggle"
              >
                <Eye className="w-4 h-4 inline mr-2" />
                Narrative
              </button>
              <button
                onClick={() => setActiveView('forensic')}
                className={`vr-toggle-option ${activeView === 'forensic' ? 'active' : 'text-[#A8A8A0]'}`}
                data-testid="forensic-toggle"
              >
                <Fingerprint className="w-4 h-4 inline mr-2" />
                Forensic
              </button>
            </div>

            <div className="flex items-center gap-2">
              {/* Device Mode Indicator */}
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="flex items-center gap-1 px-2 py-1 bg-[#111] rounded-lg">
                      {vrMode === 'vr' && <Glasses className="w-4 h-4 text-[#00F0FF]" />}
                      {vrMode === 'mobile' && <Smartphone className="w-4 h-4 text-[#A8A8A0]" />}
                      {vrMode === 'desktop' && <Monitor className="w-4 h-4 text-[#A8A8A0]" />}
                    </div>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>{vrMode === 'vr' ? 'VR Headset Detected' : vrMode === 'mobile' ? 'Mobile Mode' : 'Desktop Mode'}</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>

              <Button variant="ghost" onClick={handleShare} className="text-[#A8A8A0]">
                <Share2 className="w-5 h-5" />
              </Button>
              <Button variant="ghost" onClick={() => setIsMuted(!isMuted)} className="text-[#A8A8A0]">
                {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
              </Button>
              <Button variant="ghost" onClick={toggleFullscreen} className="text-[#A8A8A0]">
                {isFullscreen ? <Minimize className="w-5 h-5" /> : <Maximize className="w-5 h-5" />}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex pt-16">
        {/* Artwork Display */}
        <div className="flex-1 relative">
          <div 
            className="absolute inset-0 flex items-center justify-center p-8"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
          >
            <div className="relative max-w-4xl w-full aspect-[4/3]">
              <img
                ref={imageRef}
                src={artwork.image_url}
                alt={artwork.title}
                className="w-full h-full object-contain rounded-lg transition-transform duration-200"
                style={{
                  transform: `scale(${zoom}) rotate(${rotation}deg) translate(${imagePosition.x / zoom}px, ${imagePosition.y / zoom}px)`,
                  cursor: zoom > 1 ? (isDragging ? 'grabbing' : 'grab') : 'default'
                }}
                draggable={false}
              />
              
              {/* Forensic Overlay */}
              {activeView === 'forensic' && (
                <div className="absolute inset-0 rounded-lg forensic-scan">
                  {/* Grid Lines */}
                  <div className="absolute inset-0 grid grid-cols-4 grid-rows-4 pointer-events-none">
                    {[...Array(16)].map((_, i) => (
                      <div key={i} className="border border-[#00F0FF]/10"></div>
                    ))}
                  </div>
                  
                  {/* Analysis Type Indicator */}
                  <div className="absolute top-4 left-4">
                    <Badge className="badge-forensic">
                      {analysisType === 'pigment' && <Palette className="w-3 h-3 mr-1" />}
                      {analysisType === 'signature' && <FileSignature className="w-3 h-3 mr-1" />}
                      {analysisType === 'canvas' && <Grid3X3 className="w-3 h-3 mr-1" />}
                      {analysisType.charAt(0).toUpperCase() + analysisType.slice(1)} Analysis
                    </Badge>
                  </div>

                  {/* Visualization Overlay */}
                  {visualization && visualization.image_url && (
                    <div className="absolute inset-0 flex items-center justify-center bg-[#080d1c]/50">
                      <img
                        src={`${process.env.REACT_APP_BACKEND_URL}${visualization.image_url}`}
                        alt="Forensic Visualization"
                        className="max-w-full max-h-full object-contain"
                      />
                    </div>
                  )}

                  {/* Forensic Quick Stats */}
                  {forensicReport && (
                    <div className="absolute bottom-4 left-4 right-4 flex gap-2">
                      <div className="glass-dark p-2 rounded-lg flex-1">
                        <p className="text-[10px] text-[#00F0FF] uppercase tracking-wider">Auth Score</p>
                        <p className="text-lg font-mono text-[#F5F5F0]">
                          {forensicReport.forensic_summary?.authentication_score || 95}%
                        </p>
                      </div>
                      <div className="glass-dark p-2 rounded-lg flex-1">
                        <p className="text-[10px] text-[#00F0FF] uppercase tracking-wider">Technique</p>
                        <p className="text-xs text-[#F5F5F0] line-clamp-2">
                          {forensicReport.forensic_summary?.technique?.substring(0, 30) || 'Oil on canvas'}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Narrative Overlay */}
              {activeView === 'narrative' && currentSceneData && (
                <div className="absolute bottom-0 left-0 right-0 glass-dark rounded-b-lg p-6">
                  <div className="flex items-center justify-between mb-2">
                    <Badge className="badge-gold">{currentSceneData.scene}</Badge>
                    <span className="text-xs text-[#666660] font-mono">
                      Scene {currentScene + 1} of {narrativeContent.length}
                    </span>
                  </div>
                  <p className="text-[#F5F5F0] text-lg">{currentSceneData.narration}</p>
                  <Progress value={progress} className="mt-4 h-1" />
                </div>
              )}

              {/* Image Controls */}
              <div className="absolute top-4 right-4 flex flex-col gap-2">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button size="sm" variant="ghost" onClick={handleZoomIn} className="bg-black/50 text-white w-8 h-8">
                        <ZoomIn className="w-4 h-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent side="left"><p>Zoom In</p></TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button size="sm" variant="ghost" onClick={handleZoomOut} className="bg-black/50 text-white w-8 h-8">
                        <ZoomOut className="w-4 h-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent side="left"><p>Zoom Out</p></TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button size="sm" variant="ghost" onClick={handleRotate} className="bg-black/50 text-white w-8 h-8">
                        <RotateCw className="w-4 h-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent side="left"><p>Rotate</p></TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button size="sm" variant="ghost" onClick={handleReset} className="bg-black/50 text-white w-8 h-8">
                        <RotateCcw className="w-4 h-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent side="left"><p>Reset View</p></TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
            </div>
          </div>
        </div>

        {/* Side Panel */}
        <div className="w-96 border-l border-[#1a1a1a] bg-[#0a0a0a] flex flex-col">
          {activeView === 'narrative' ? (
            // Narrative Panel
            <div className="flex-1 flex flex-col">
              <div className="p-4 border-b border-[#1a1a1a]">
                <h2 className="font-display text-xl text-[#F5F5F0] mb-2">{story.title}</h2>
                <p className="text-sm text-[#A8A8A0]">{story.description}</p>
              </div>

              <ScrollArea className="flex-1 p-4">
                <h3 className="font-display text-lg text-[#F5F5F0] mb-4">Story Timeline</h3>
                <div className="space-y-4">
                  {narrativeContent.map((scene, index) => (
                    <button
                      key={index}
                      onClick={() => { setCurrentScene(index); setProgress(0); }}
                      className={`w-full text-left p-3 rounded-lg transition-all ${
                        currentScene === index 
                          ? 'bg-[#D4AF37]/10 border border-[#D4AF37]' 
                          : 'bg-[#111] border border-transparent hover:border-[#1a1a1a]'
                      }`}
                      data-testid={`scene-${index}`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-mono text-[#666660]">
                          {Math.floor(scene.timestamp / 60)}:{String(scene.timestamp % 60).padStart(2, '0')}
                        </span>
                        {currentScene === index && (
                          <span className="w-2 h-2 bg-[#D4AF37] rounded-full animate-pulse"></span>
                        )}
                      </div>
                      <p className={`text-sm ${currentScene === index ? 'text-[#F5F5F0]' : 'text-[#A8A8A0]'}`}>
                        {scene.scene}
                      </p>
                    </button>
                  ))}
                </div>
              </ScrollArea>

              {/* Playback Controls */}
              <div className="p-4 border-t border-[#1a1a1a]">
                <div className="flex items-center justify-center gap-4">
                  <Button
                    variant="ghost"
                    onClick={handlePrevScene}
                    disabled={currentScene === 0}
                    className="text-[#A8A8A0] disabled:opacity-30"
                  >
                    <RotateCcw className="w-5 h-5" />
                  </Button>
                  <Button
                    onClick={handlePlayPause}
                    className="w-14 h-14 rounded-full btn-gold"
                    data-testid="play-btn"
                  >
                    {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6 ml-1" />}
                  </Button>
                  <Button
                    variant="ghost"
                    onClick={handleNextScene}
                    disabled={currentScene >= narrativeContent.length - 1}
                    className="text-[#A8A8A0] disabled:opacity-30"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            // Forensic Panel
            <div className="flex-1 flex flex-col">
              <div className="p-4 border-b border-[#1a1a1a]">
                <h2 className="font-display text-xl text-[#00F0FF] mb-2">AI Forensic Analysis</h2>
                <p className="text-sm text-[#A8A8A0]">
                  Emaira analyzes the artwork's DNA markers
                </p>
              </div>

              {/* Analysis Type Tabs */}
              <Tabs value={analysisType} onValueChange={setAnalysisType} className="flex-1 flex flex-col">
                <div className="px-4 pt-4">
                  <TabsList className="grid w-full grid-cols-3 bg-[#111]">
                    <TabsTrigger 
                      value="pigment" 
                      className="data-[state=active]:bg-[#00F0FF]/20 data-[state=active]:text-[#00F0FF]"
                    >
                      <Palette className="w-4 h-4 mr-1" /> Pigment
                    </TabsTrigger>
                    <TabsTrigger 
                      value="signature"
                      className="data-[state=active]:bg-[#00F0FF]/20 data-[state=active]:text-[#00F0FF]"
                    >
                      <FileSignature className="w-4 h-4 mr-1" /> Sign
                    </TabsTrigger>
                    <TabsTrigger 
                      value="canvas"
                      className="data-[state=active]:bg-[#00F0FF]/20 data-[state=active]:text-[#00F0FF]"
                    >
                      <Grid3X3 className="w-4 h-4 mr-1" /> Canvas
                    </TabsTrigger>
                  </TabsList>
                </div>

                <ScrollArea className="flex-1 p-4">
                  <TabsContent value="pigment" className="mt-0">
                    <div className="space-y-4">
                      <p className="text-sm text-[#A8A8A0]">
                        Analyze the chemical composition of pigments used, identifying era-specific materials and authenticity markers.
                      </p>
                      {forensicReport?.forensic_summary?.pigments && (
                        <div className="p-3 bg-[#111] rounded-lg border border-[#1a1a1a]">
                          <p className="text-xs text-[#666660] mb-1">Known Pigments</p>
                          <div className="flex flex-wrap gap-1">
                            {forensicReport.forensic_summary.pigments.map((p, i) => (
                              <Badge key={i} className="bg-[#00F0FF]/10 text-[#00F0FF] text-xs">{p}</Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </TabsContent>

                  <TabsContent value="signature" className="mt-0">
                    <div className="space-y-4">
                      <p className="text-sm text-[#A8A8A0]">
                        Comparative analysis of signature patterns, brushwork, and pressure points for authentication.
                      </p>
                      {forensicReport?.forensic_summary?.signature_markers && (
                        <div className="p-3 bg-[#111] rounded-lg border border-[#1a1a1a]">
                          <p className="text-xs text-[#666660] mb-1">Signature Markers</p>
                          <p className="text-sm text-[#F5F5F0] font-mono">
                            {forensicReport.forensic_summary.signature_markers}
                          </p>
                        </div>
                      )}
                    </div>
                  </TabsContent>

                  <TabsContent value="canvas" className="mt-0">
                    <div className="space-y-4">
                      <p className="text-sm text-[#A8A8A0]">
                        Analyze canvas weave density, material composition, and aging patterns.
                      </p>
                      {forensicReport?.forensic_summary?.canvas_info && (
                        <div className="p-3 bg-[#111] rounded-lg border border-[#1a1a1a]">
                          <p className="text-xs text-[#666660] mb-1">Canvas Analysis</p>
                          <p className="text-sm text-[#F5F5F0] font-mono">
                            {forensicReport.forensic_summary.canvas_info}
                          </p>
                        </div>
                      )}
                    </div>
                  </TabsContent>

                  {/* AI Analysis Result */}
                  {forensicResult && (
                    <div className="mt-4 p-4 bg-[#00F0FF]/5 border border-[#00F0FF]/20 rounded-lg">
                      <div className="flex items-center gap-2 mb-3">
                        <Sparkles className="w-4 h-4 text-[#00F0FF]" />
                        <span className="text-sm font-medium text-[#00F0FF]">AI Analysis</span>
                      </div>
                      <p className="text-sm text-[#F5F5F0] whitespace-pre-wrap">
                        {forensicResult.results?.summary}
                      </p>
                      <p className="text-xs text-[#666660] mt-2 font-mono">
                        Confidence: {(forensicResult.results?.confidence_score * 100).toFixed(1)}%
                      </p>
                    </div>
                  )}
                </ScrollArea>

                {/* Analysis Actions */}
                <div className="p-4 border-t border-[#1a1a1a] space-y-3">
                  <Button
                    onClick={() => runForensicAnalysis(analysisType)}
                    disabled={analyzing}
                    className="w-full btn-forensic"
                    data-testid="run-analysis-btn"
                  >
                    {analyzing ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" /> Analyzing...
                      </>
                    ) : (
                      <>
                        <Fingerprint className="w-4 h-4 mr-2" /> Run AI Analysis
                      </>
                    )}
                  </Button>
                  <Button
                    onClick={() => generateVisualization(analysisType)}
                    disabled={generatingViz}
                    variant="outline"
                    className="w-full border-[#00F0FF]/50 text-[#00F0FF] hover:bg-[#00F0FF]/10"
                    data-testid="generate-viz-btn"
                  >
                    {generatingViz ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" /> Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4 mr-2" /> Generate Visualization
                      </>
                    )}
                  </Button>
                </div>
              </Tabs>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VRExperience;
