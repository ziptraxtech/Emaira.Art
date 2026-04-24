import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Loader2,
  Camera,
  HardHat,
  Ruler,
  AlertTriangle,
  Sparkles,
  Eye,
  Download,
  ArrowRight,
  ShieldCheck,
  FileText,
} from "lucide-react";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CATEGORY_META = {
  defect: { icon: Camera, label: "Defect", color: "text-rose-400" },
  safety_violation: { icon: HardHat, label: "Safety", color: "text-amber-400" },
  design_deviation: { icon: Ruler, label: "Design", color: "text-sky-400" },
  material_note: { icon: FileText, label: "Note", color: "text-[#A8A8A0]" },
};

const SEVERITY_BADGE = {
  low: "bg-emerald-900/30 text-emerald-400 border-emerald-900/50",
  medium: "bg-yellow-900/30 text-yellow-300 border-yellow-900/50",
  high: "bg-orange-900/30 text-orange-400 border-orange-900/50",
  critical: "bg-rose-900/40 text-rose-300 border-rose-900/60",
};

const RISK_BADGE = SEVERITY_BADGE;

const ArchitectsSharedReport = () => {
  const { token } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);
  const [videoEl, setVideoEl] = useState(null);

  useEffect(() => {
    let alive = true;
    axios.get(`${API}/architects/share/${token}`)
      .then((r) => alive && setData(r.data))
      .catch((e) => alive && setErr(e.response?.data?.detail || "This share link is invalid or has been revoked."))
      .finally(() => alive && setLoading(false));
    return () => { alive = false; };
  }, [token]);

  const jumpTo = (sec) => {
    if (videoEl && typeof sec === "number") {
      videoEl.currentTime = sec;
      videoEl.play().catch(() => {});
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-[#D4AF37] animate-spin" />
      </div>
    );
  }
  if (err || !data) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center text-center px-6">
        <div className="max-w-md">
          <ShieldCheck className="w-12 h-12 text-[#444] mx-auto mb-4" />
          <h1 className="font-display text-2xl text-[#F5F5F0] mb-2">Share link unavailable</h1>
          <p className="text-[#A8A8A0] mb-6">{err}</p>
          <Link to="/architects"><Button className="btn-gold">Visit Emaira Architects</Button></Link>
        </div>
      </div>
    );
  }

  const BACKEND = process.env.REACT_APP_BACKEND_URL;

  return (
    <div className="min-h-screen bg-[#050505] text-[#F5F5F0]" data-testid="architects-shared-report">
      {/* Public banner nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass-dark border-b border-[#1a1a1a]">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/architects" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded bg-gradient-to-br from-[#D4AF37] to-[#B8860B] flex items-center justify-center">
              <span className="font-display text-[#050505] text-lg font-bold">E</span>
            </div>
            <div className="leading-tight hidden sm:block">
              <div className="font-display text-base">Emaira<span className="text-[#D4AF37]">.</span>Architects</div>
              <div className="text-[9px] tracking-[0.2em] text-[#A8A8A0] uppercase">Shared Report</div>
            </div>
          </Link>
          <div className="flex items-center gap-2">
            <Badge className="bg-[#1a1a1a] text-[#A8A8A0] border-[#333] hidden sm:inline-flex">
              <Eye className="w-3 h-3 mr-1" /> {data.share_view_count} views
            </Badge>
            <Link to="/architects/pricing">
              <Button className="btn-gold text-xs sm:text-sm" data-testid="shared-cta-upgrade">
                Try Emaira Architects <ArrowRight className="w-3 h-3 ml-1" />
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      <div className="pt-24 pb-16 max-w-7xl mx-auto px-6">
        <div className="mb-6">
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <Badge className="bg-[#1a1a1a] text-[#D4AF37] border-[#333] capitalize">
              {data.inspection_type?.replace(/_/g, " ")}
            </Badge>
            {data.overall_risk_level && (
              <Badge className={RISK_BADGE[data.overall_risk_level] || RISK_BADGE.low}>
                <AlertTriangle className="w-3 h-3 mr-1" />{data.overall_risk_level} risk
              </Badge>
            )}
            {data.project?.location && (
              <span className="text-xs text-[#666] ml-2">{data.project.location}</span>
            )}
          </div>
          <h1 className="font-display text-3xl lg:text-5xl mb-2" data-testid="shared-title">{data.title}</h1>
          {data.project?.name && (
            <p className="text-sm text-[#A8A8A0]">Project: {data.project.name}</p>
          )}
          <a
            href={`${BACKEND}/api/architects/share/${token}/report.pdf`}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center mt-4 text-sm text-[#D4AF37] hover:underline"
            data-testid="shared-pdf-link"
          >
            <Download className="w-4 h-4 mr-1" /> Download PDF report
          </a>
        </div>

        <div className="grid lg:grid-cols-5 gap-6">
          <div className="lg:col-span-3 space-y-4">
            <div className="card-obsidian rounded-xl overflow-hidden bg-black">
              <video
                ref={setVideoEl}
                src={`${BACKEND}${data.video_url}`}
                controls
                className="w-full aspect-video bg-black"
                data-testid="shared-video"
              />
            </div>
            {data.overall_summary && (
              <div className="card-obsidian rounded-xl p-5">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="w-4 h-4 text-[#D4AF37]" />
                  <h3 className="font-display text-lg">AI Summary</h3>
                </div>
                <p className="text-sm text-[#CECEC5] leading-relaxed">{data.overall_summary}</p>
              </div>
            )}
            {data.design_reference_url && (
              <div className="card-obsidian rounded-xl p-4">
                <h3 className="font-display text-sm mb-2 text-[#A8A8A0]">Reference design (BIM)</h3>
                <img src={`${BACKEND}${data.design_reference_url}`} alt="Reference" className="rounded border border-[#1a1a1a] max-h-72 mx-auto" />
              </div>
            )}
            {(data.keyframes || []).length > 0 && (
              <div>
                <h3 className="font-display text-lg mb-3">Keyframes</h3>
                <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
                  {data.keyframes.map((k, i) => (
                    <img key={i} src={`${BACKEND}${k}`} alt={`KF ${i}`} loading="lazy" className="aspect-video object-cover rounded border border-[#1a1a1a]" />
                  ))}
                </div>
              </div>
            )}
          </div>
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
            <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
              {(data.findings || []).map((f) => {
                const meta = CATEGORY_META[f.category] || CATEGORY_META.material_note;
                const Icon = meta.icon;
                return (
                  <button
                    key={f.finding_id}
                    onClick={() => jumpTo(f.timestamp_sec)}
                    className="w-full text-left card-obsidian rounded-lg p-3 hover:border-[#D4AF37]/40 border border-transparent transition-colors"
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-8 h-8 rounded bg-[#1a1a1a] flex items-center justify-center flex-shrink-0 ${meta.color}`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-1.5 flex-wrap mb-1">
                          <Badge className={`text-[10px] ${SEVERITY_BADGE[f.severity] || SEVERITY_BADGE.medium}`}>{f.severity}</Badge>
                          <span className="text-xs font-mono text-[#666]">{meta.label} · {f.type}</span>
                          {typeof f.timestamp_sec === "number" && (
                            <span className="text-[10px] font-mono text-[#D4AF37]">@ {f.timestamp_sec.toFixed(1)}s</span>
                          )}
                        </div>
                        <p className="text-sm text-[#E0E0D8]">{f.description}</p>
                        {f.recommendation && <p className="text-[11px] text-[#A8A8A0] italic mt-1">→ {f.recommendation}</p>}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
        <div className="mt-12 card-obsidian rounded-xl p-6 text-center border border-[#D4AF37]/20">
          <Sparkles className="w-5 h-5 text-[#D4AF37] mx-auto mb-2" />
          <p className="text-sm text-[#A8A8A0] mb-3">This report was generated by Emaira Architects — Video AI QC/QA in minutes.</p>
          <Link to="/architects">
            <Button className="btn-gold">Run your own inspection <ArrowRight className="w-4 h-4 ml-1" /></Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ArchitectsSharedReport;
