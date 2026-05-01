import { useState, useEffect } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { useAuth, API } from "@/App";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  ArrowLeft,
  Camera,
  HardHat,
  Ruler,
  AlertTriangle,
  Sparkles,
  Clock,
  CheckCircle2,
  Loader2,
  Download,
  RotateCw,
  Trash2,
  FileText,
  Share2,
  Copy,
  Check,
} from "lucide-react";
import { toast } from "sonner";

const CATEGORY_META = {
  defect: { icon: Camera, label: "Defect", color: "text-rose-400", bar: "bg-rose-500" },
  safety_violation: { icon: HardHat, label: "Safety", color: "text-amber-400", bar: "bg-amber-500" },
  design_deviation: { icon: Ruler, label: "Design", color: "text-sky-400", bar: "bg-sky-500" },
  material_note: { icon: FileText, label: "Note", color: "text-[#A8A8A0]", bar: "bg-[#333]" },
};

const SEVERITY_BADGE = {
  low: "bg-emerald-900/30 text-emerald-400 border-emerald-900/50",
  medium: "bg-yellow-900/30 text-yellow-300 border-yellow-900/50",
  high: "bg-orange-900/30 text-orange-400 border-orange-900/50",
  critical: "bg-rose-900/40 text-rose-300 border-rose-900/60",
};

const RISK_BADGE = {
  low: "bg-emerald-900/30 text-emerald-400 border-emerald-900/50",
  medium: "bg-yellow-900/30 text-yellow-400 border-yellow-900/50",
  high: "bg-orange-900/30 text-orange-400 border-orange-900/50",
  critical: "bg-rose-900/40 text-rose-300 border-rose-900/60",
};

const ArchitectsInspection = () => {
  const { inspectionId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reanalyzing, setReanalyzing] = useState(false);
  const [videoEl, setVideoEl] = useState(null);
  const [shareLink, setShareLink] = useState(null);
  const [creatingShare, setCreatingShare] = useState(false);
  const [shareCopied, setShareCopied] = useState(false);

  const fetch = async () => {
    try {
      const r = await axios.get(`${API}/architects/inspections/${inspectionId}`, { withCredentials: true });
      setData(r.data);
      return r.data;
    } catch (e) {
      toast.error("Could not load inspection");
      return null;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!user) return;
    fetch();
  }, [inspectionId, user]);

  // Auto-poll while analysis is running
  useEffect(() => {
    if (!data || data.status !== "analyzing") return;
    const t = setInterval(fetch, 4000);
    return () => clearInterval(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data?.status]);

  const reanalyze = async () => {
    if (!data) return;
    setReanalyzing(true);
    try {
      await axios.post(`${API}/architects/inspections/${inspectionId}/analyze`, {}, { withCredentials: true });
      toast.success("Analysis finished");
      fetch();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Analysis failed");
    } finally {
      setReanalyzing(false);
    }
  };

  const del = async () => {
    if (!window.confirm("Delete this inspection and its video?")) return;
    try {
      await axios.delete(`${API}/architects/inspections/${inspectionId}`, { withCredentials: true });
      toast.success("Deleted");
      navigate("/architects/dashboard");
    } catch {
      toast.error("Could not delete");
    }
  };

  const exportJSON = () => {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `emaira_architects_${inspectionId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportPDF = () => {
    const url = `${process.env.REACT_APP_BACKEND_URL}/api/architects/inspections/${inspectionId}/report.pdf`;
    window.open(url, "_blank");
  };

  const createShare = async () => {
    setCreatingShare(true);
    try {
      const r = await axios.post(`${API}/architects/inspections/${inspectionId}/share`, {}, { withCredentials: true });
      setShareLink(r.data);
      toast.success("Public share link ready");
    } catch (e) {
      toast.error(e.response?.data?.detail || "Could not create share link");
    } finally {
      setCreatingShare(false);
    }
  };

  const revokeShare = async () => {
    if (!window.confirm("Revoke the public share link? Anyone with the URL will lose access.")) return;
    try {
      await axios.delete(`${API}/architects/inspections/${inspectionId}/share`, { withCredentials: true });
      setShareLink(null);
      toast.success("Share link revoked");
    } catch {
      toast.error("Could not revoke");
    }
  };

  const copyShareUrl = () => {
    if (!shareLink) return;
    const url = `${window.location.origin}/architects/share/${shareLink.token}`;
    navigator.clipboard.writeText(url).then(() => {
      setShareCopied(true);
      setTimeout(() => setShareCopied(false), 1500);
    });
  };

  const jumpTo = (sec) => {
    if (videoEl && typeof sec === "number") {
      videoEl.currentTime = sec;
      videoEl.play().catch(() => {});
    }
  };

  if (!user) {
    return <div className="min-h-screen bg-[#080d1c] flex items-center justify-center text-[#A8A8A0]">Please sign in.</div>;
  }
  if (loading) {
    return (
      <div className="min-h-screen bg-[#080d1c] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-[#D4AF37] animate-spin" />
      </div>
    );
  }
  if (!data) return null;

  const BACKEND = process.env.REACT_APP_BACKEND_URL;

  return (
    <div className="min-h-screen bg-[#080d1c] text-[#F5F5F0]" data-testid="architects-inspection-detail">
      <nav className="fixed top-0 left-0 right-0 z-50 glass-dark border-b border-[#1a1a1a]">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/architects/dashboard" className="flex items-center gap-2 text-[#A8A8A0] hover:text-[#F5F5F0] text-sm">
            <ArrowLeft className="w-4 h-4" /> Dashboard
          </Link>
          <Link to="/architects" className="font-display text-sm">Emaira<span className="text-[#D4AF37]">.</span>Architects</Link>
        </div>
      </nav>

      <div className="pt-24 pb-16 max-w-7xl mx-auto px-4 sm:px-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-6">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <Badge className="bg-[#1a1a1a] text-[#D4AF37] border-[#333] capitalize">{data.inspection_type.replace(/_/g, " ")}</Badge>
              {data.status === "completed" && (
                <Badge className="bg-emerald-900/30 text-emerald-400 border-emerald-900/50"><CheckCircle2 className="w-3 h-3 mr-1" />Completed</Badge>
              )}
              {data.status === "analyzing" && (
                <Badge className="bg-sky-900/30 text-sky-300 border-sky-900/50"><Loader2 className="w-3 h-3 mr-1 animate-spin" />Analyzing…</Badge>
              )}
              {data.status === "failed" && (
                <Badge className="bg-rose-900/30 text-rose-300 border-rose-900/50">Failed</Badge>
              )}
              {data.status === "uploaded" && (
                <Badge className="bg-[#222] text-[#A8A8A0] border-[#333]"><Clock className="w-3 h-3 mr-1" />Ready</Badge>
              )}
              {data.overall_risk_level && (
                <Badge className={RISK_BADGE[data.overall_risk_level] || RISK_BADGE.low}>
                  <AlertTriangle className="w-3 h-3 mr-1" />{data.overall_risk_level} risk
                </Badge>
              )}
            </div>
            <h1 className="font-display text-2xl sm:text-3xl lg:text-4xl break-words" data-testid="architects-inspection-title">{data.title}</h1>
            {data.ai_model && <p className="text-xs text-[#666660] mt-1">AI: {data.ai_model}</p>}
          </div>
          <div className="flex flex-wrap gap-2">
            {data.status !== "analyzing" && (
              <Button variant="outline" className="border-[#333] text-[#F5F5F0] hover:bg-[#111] flex-1 sm:flex-none" onClick={reanalyze} disabled={reanalyzing} data-testid="architects-reanalyze-btn">
                {reanalyzing ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <RotateCw className="w-4 h-4 mr-2" />}
                <span className="truncate">{data.status === "uploaded" ? "Run Analysis" : "Re-analyze"}</span>
              </Button>
            )}
            {data.status === "completed" && (
              <Button variant="outline" className="border-[#333] text-[#F5F5F0] hover:bg-[#111] flex-1 sm:flex-none" onClick={exportPDF} data-testid="architects-pdf-btn">
                <FileText className="w-4 h-4 mr-2" /> PDF
              </Button>
            )}
            {data.status === "completed" && (
              <Button variant="outline" className="border-[#333] text-[#F5F5F0] hover:bg-[#111] flex-1 sm:flex-none" onClick={exportJSON} data-testid="architects-export-btn">
                <Download className="w-4 h-4 mr-2" /> JSON
              </Button>
            )}
            {data.status === "completed" && !shareLink && (
              <Button className="btn-gold flex-1 sm:flex-none" onClick={createShare} disabled={creatingShare} data-testid="architects-share-btn">
                {creatingShare ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Share2 className="w-4 h-4 mr-2" />}
                <span className="truncate">Share</span>
              </Button>
            )}
            {data.status === "completed" && shareLink && (
              <div className="flex items-center gap-1 bg-[#0a0a0a] border border-[#D4AF37]/40 rounded-md p-1 pr-2 max-w-full">
                <span className="text-xs font-mono text-[#D4AF37] px-2 max-w-[100px] sm:max-w-[120px] truncate">/share/{shareLink.token.slice(0, 8)}…</span>
                <Button size="sm" variant="ghost" onClick={copyShareUrl} className="h-7 px-2 text-[#A8A8A0] hover:text-[#F5F5F0]">
                  {shareCopied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                </Button>
                <Button size="sm" variant="ghost" onClick={revokeShare} className="h-7 px-2 text-rose-400 hover:text-rose-300">
                  <Trash2 className="w-3.5 h-3.5" />
                </Button>
              </div>
            )}
            <Button variant="outline" className="border-rose-900/50 text-rose-300 hover:bg-rose-900/20 flex-1 sm:flex-none" onClick={del}>
              <Trash2 className="w-4 h-4 mr-2" /> Delete
            </Button>
          </div>
        </div>

        <div className="grid lg:grid-cols-5 gap-6">
          {/* Video */}
          <div className="lg:col-span-3 space-y-4">
            <div className="card-obsidian rounded-xl overflow-hidden bg-black">
              <video
                ref={setVideoEl}
                src={`${BACKEND}/api/architects/inspections/${inspectionId}/video`}
                controls
                className="w-full aspect-video bg-black"
                data-testid="architects-video-player"
              />
            </div>
            {/* Summary */}
            {data.overall_summary && (
              <div className="card-obsidian rounded-xl p-5">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="w-4 h-4 text-[#D4AF37]" />
                  <h3 className="font-display text-lg">AI Summary</h3>
                </div>
                <p className="text-sm text-[#CECEC5] leading-relaxed">{data.overall_summary}</p>
              </div>
            )}
            {/* Keyframes */}
            {(data.keyframes || []).length > 0 && (
              <div>
                <h3 className="font-display text-lg mb-3">Keyframes</h3>
                <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
                  {data.keyframes.map((k, i) => (
                    <img
                      key={i}
                      src={`${BACKEND}${k}`}
                      alt={`Keyframe ${i}`}
                      loading="lazy"
                      className="aspect-video object-cover rounded border border-[#1a1a1a] hover:border-[#D4AF37] cursor-pointer transition-colors"
                      onClick={() => jumpTo((data.video_duration_sec || 0) * ((i + 1) / ((data.keyframe_count || 6) + 1)))}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Findings sidebar */}
          <div className="lg:col-span-2 space-y-3">
            <div className="grid grid-cols-3 gap-2">
              <div className="card-obsidian rounded-lg p-3 text-center">
                <Camera className="w-4 h-4 mx-auto text-rose-400 mb-1" />
                <div className="font-display text-2xl text-rose-400">{data.defects_count || 0}</div>
                <div className="text-[10px] text-[#A8A8A0]">Defects</div>
              </div>
              <div className="card-obsidian rounded-lg p-3 text-center">
                <HardHat className="w-4 h-4 mx-auto text-amber-400 mb-1" />
                <div className="font-display text-2xl text-amber-400">{data.safety_violations_count || 0}</div>
                <div className="text-[10px] text-[#A8A8A0]">Safety</div>
              </div>
              <div className="card-obsidian rounded-lg p-3 text-center">
                <Ruler className="w-4 h-4 mx-auto text-sky-400 mb-1" />
                <div className="font-display text-2xl text-sky-400">{data.design_deviations_count || 0}</div>
                <div className="text-[10px] text-[#A8A8A0]">Design</div>
              </div>
            </div>

            <h3 className="font-display text-lg pt-2">Findings ({(data.findings || []).length})</h3>
            {data.status === "analyzing" && (
              <div className="card-obsidian rounded-xl p-6 text-center">
                <Loader2 className="w-6 h-6 text-[#D4AF37] mx-auto mb-3 animate-spin" />
                <p className="text-sm text-[#A8A8A0]">Gemini 3 Pro is reviewing the video. This typically takes 20–60 seconds.</p>
              </div>
            )}
            {(data.findings || []).length === 0 && data.status === "completed" && (
              <div className="card-obsidian rounded-xl p-6 text-center text-sm text-[#A8A8A0]">
                No issues detected.
              </div>
            )}
            <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
              {(data.findings || []).map((f) => {
                const meta = CATEGORY_META[f.category] || CATEGORY_META.material_note;
                const Icon = meta.icon;
                return (
                  <button
                    key={f.finding_id}
                    onClick={() => jumpTo(f.timestamp_sec)}
                    className="w-full text-left card-obsidian rounded-lg p-3 hover:border-[#D4AF37]/40 border border-transparent transition-colors"
                    data-testid={`architects-finding-${f.finding_id}`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-8 h-8 rounded bg-[#1a1a1a] flex items-center justify-center flex-shrink-0 ${meta.color}`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-1.5 flex-wrap mb-1">
                          <Badge className={`text-[10px] ${SEVERITY_BADGE[f.severity] || SEVERITY_BADGE.medium}`}>
                            {f.severity}
                          </Badge>
                          <span className="text-xs font-mono text-[#666]">{meta.label} · {f.type}</span>
                          {typeof f.timestamp_sec === "number" && (
                            <span className="text-[10px] font-mono text-[#D4AF37]">@ {f.timestamp_sec.toFixed(1)}s</span>
                          )}
                          {typeof f.confidence === "number" && (
                            <span className="text-[10px] font-mono text-[#666]">{Math.round((f.confidence || 0) * 100)}%</span>
                          )}
                        </div>
                        <p className="text-sm text-[#E0E0D8] mb-1">{f.description}</p>
                        {f.recommendation && (
                          <p className="text-[11px] text-[#A8A8A0] italic">→ {f.recommendation}</p>
                        )}
                        {f.bbox_hint && (
                          <span className="text-[10px] text-[#666] mt-1 inline-block">Location: {f.bbox_hint}</span>
                        )}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArchitectsInspection;
