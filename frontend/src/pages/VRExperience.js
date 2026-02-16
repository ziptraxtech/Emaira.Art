import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useAuth, API } from "@/App";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
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
  RotateCcw,
  Loader2,
  Sparkles,
  X,
  ChevronRight
} from "lucide-react";

const VRExperience = () => {
  const { storyId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [story, setStory] = useState(null);
  const [artwork, setArtwork] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState("narrative"); // narrative or forensic
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentScene, setCurrentScene] = useState(0);
  const [analysisType, setAnalysisType] = useState("pigment");
  const [forensicResult, setForensicResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [generatingViz, setGeneratingViz] = useState(false);
  const [visualization, setVisualization] = useState(null);

  useEffect(() => {
    fetchData();
  }, [storyId]);

  const fetchData = async () => {
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
      console.error("Error:", error);
      toast.error("Failed to load experience");
      navigate('/gallery');
    } finally {
      setLoading(false);
    }
  };

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

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleNextScene = () => {
    if (story?.narrative_content && currentScene < story.narrative_content.length - 1) {
      setCurrentScene(currentScene + 1);
    }
  };

  const handlePrevScene = () => {
    if (currentScene > 0) {
      setCurrentScene(currentScene - 1);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-[#D4AF37] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-[#A8A8A0]">Loading experience...</p>
        </div>
      </div>
    );
  }

  if (!story || !artwork) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <p className="text-[#A8A8A0]">Experience not found</p>
      </div>
    );
  }

  const narrativeContent = story.narrative_content || [];
  const currentSceneData = narrativeContent[currentScene];

  return (
    <div className="min-h-screen bg-[#050505] flex flex-col">
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
              <Button variant="ghost" onClick={() => setIsMuted(!isMuted)} className="text-[#A8A8A0]">
                {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
              </Button>
              <Button variant="ghost" className="text-[#A8A8A0]">
                <Maximize className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex pt-16">
        {/* Artwork Display */}
        <div className="flex-1 relative">
          <div className="absolute inset-0 flex items-center justify-center p-8">
            <div className="relative max-w-4xl w-full aspect-[4/3]">
              <img
                src={artwork.image_url}
                alt={artwork.title}
                className="w-full h-full object-contain rounded-lg"
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
                    <div className="absolute inset-0 flex items-center justify-center bg-[#050505]/50">
                      <img
                        src={`${process.env.REACT_APP_BACKEND_URL}${visualization.image_url}`}
                        alt="Forensic Visualization"
                        className="max-w-full max-h-full object-contain"
                      />
                    </div>
                  )}
                </div>
              )}

              {/* Narrative Overlay */}
              {activeView === 'narrative' && currentSceneData && (
                <div className="absolute bottom-0 left-0 right-0 glass-dark rounded-b-lg p-6">
                  <Badge className="badge-gold mb-2">{currentSceneData.scene}</Badge>
                  <p className="text-[#F5F5F0] text-lg">{currentSceneData.narration}</p>
                </div>
              )}
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
                      onClick={() => setCurrentScene(index)}
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
                      {story.forensic_content?.pigment_analysis && (
                        <div className="p-3 bg-[#111] rounded-lg border border-[#1a1a1a]">
                          <p className="text-xs text-[#666660] mb-1">Quick Info</p>
                          <p className="text-sm text-[#F5F5F0] font-mono">
                            {story.forensic_content.pigment_analysis}
                          </p>
                        </div>
                      )}
                    </div>
                  </TabsContent>

                  <TabsContent value="signature" className="mt-0">
                    <div className="space-y-4">
                      <p className="text-sm text-[#A8A8A0]">
                        Comparative analysis of signature patterns, brushwork, and pressure points for authentication.
                      </p>
                      {story.forensic_content?.signature_markers && (
                        <div className="p-3 bg-[#111] rounded-lg border border-[#1a1a1a]">
                          <p className="text-xs text-[#666660] mb-1">Quick Info</p>
                          <p className="text-sm text-[#F5F5F0] font-mono">
                            {story.forensic_content.signature_markers}
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
                      {story.forensic_content?.canvas_analysis && (
                        <div className="p-3 bg-[#111] rounded-lg border border-[#1a1a1a]">
                          <p className="text-xs text-[#666660] mb-1">Quick Info</p>
                          <p className="text-sm text-[#F5F5F0] font-mono">
                            {story.forensic_content.canvas_analysis}
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
