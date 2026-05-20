import { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth, API } from "@/App";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Video,
  Plus,
  FolderPlus,
  HardHat,
  Camera,
  Ruler,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Play,
  ArrowLeft,
  Loader2,
  UploadCloud,
  Sparkles,
  Building2,
  Smartphone,
} from "lucide-react";
import { toast } from "sonner";

const FALLBACK_PHOTOS = ["/insp1.jpg", "/insp2.jpg", "/insp3.jpg", "/insp4.jpg"];

const INSPECTION_TYPES = [
  { value: "defect_detection", label: "Defect Detection", icon: Camera, color: "text-rose-400" },
  { value: "safety_monitoring", label: "Safety Monitoring (PPE)", icon: HardHat, color: "text-amber-400" },
  { value: "design_validation", label: "Reality vs. Design", icon: Ruler, color: "text-sky-400" },
];

const RISK_BADGE = {
  low: "bg-emerald-900/30 text-emerald-400 border-emerald-900/50",
  medium: "bg-yellow-900/30 text-yellow-400 border-yellow-900/50",
  high: "bg-orange-900/30 text-orange-400 border-orange-900/50",
  critical: "bg-rose-900/40 text-rose-300 border-rose-900/60",
};

const ArchitectsDashboard = () => {
  const { user, login, logout } = useAuth();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  const [projects, setProjects] = useState([]);
  const [inspections, setInspections] = useState([]);
  const [loading, setLoading] = useState(true);

  // Project dialog
  const [projectDialogOpen, setProjectDialogOpen] = useState(false);
  const [projectForm, setProjectForm] = useState({ name: "", location: "", project_type: "commercial", description: "" });
  const [creatingProject, setCreatingProject] = useState(false);

  // Upload dialog
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [uploadForm, setUploadForm] = useState({ project_id: "", title: "", inspection_type: "defect_detection", notes: "", file: null, design_reference: null });
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  useEffect(() => {
    if (user) fetchAll();
  }, [user]);

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [p, i] = await Promise.all([
        axios.get(`${API}/architects/projects`, { withCredentials: true }),
        axios.get(`${API}/architects/inspections`, { withCredentials: true }),
      ]);
      setProjects(p.data.projects || []);
      setInspections(i.data.inspections || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    if (!projectForm.name.trim()) return;
    setCreatingProject(true);
    try {
      await axios.post(`${API}/architects/projects`, projectForm, { withCredentials: true });
      toast.success("Project created");
      setProjectDialogOpen(false);
      setProjectForm({ name: "", location: "", project_type: "commercial", description: "" });
      fetchAll();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Could not create project");
    } finally {
      setCreatingProject(false);
    }
  };

  const ACCEPTED_MEDIA = "video/mp4,video/quicktime,video/x-m4v,video/webm,image/jpeg,image/png,image/webp";

  const handleFileSelect = (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (f.size > 500 * 1024 * 1024) {
      toast.error("File must be under 500 MB");
      return;
    }
    setUploadForm((s) => ({ ...s, file: f, title: s.title || f.name.replace(/\.[^.]+$/, "") }));
  };

  const s3Put = (url, file, onProgress) =>
    new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open("PUT", url);
      xhr.upload.onprogress = (evt) => {
        if (evt.lengthComputable && onProgress) onProgress(evt.loaded / evt.total);
      };
      xhr.onload = () => (xhr.status >= 200 && xhr.status < 300 ? resolve() : reject(new Error(`S3 upload failed: ${xhr.status}`)));
      xhr.onerror = () => reject(new Error("S3 upload network error"));
      xhr.send(file);
    });

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!uploadForm.file || !uploadForm.project_id || !uploadForm.title) {
      toast.error("Project, title and file are required");
      return;
    }
    setUploading(true);
    setUploadProgress(0);
    try {
      const file = uploadForm.file;
      const ref = uploadForm.design_reference;

      // Step 1 — get presigned URL(s) from backend
      const { data: presign } = await axios.post(
        `${API}/architects/inspections/presign`,
        { filename: file.name, ...(ref ? { ref_filename: ref.name } : {}) },
        { withCredentials: true }
      );

      // Step 2 — upload primary file to S3
      const refWeight = ref ? 0.15 : 0;
      await s3Put(presign.upload_url, file, (p) =>
        setUploadProgress(Math.round(p * (85 - refWeight * 85)))
      );

      // Step 2b — upload design reference if present
      let ref_s3_key;
      if (ref && presign.ref_upload_url) {
        await s3Put(presign.ref_upload_url, ref, (p) =>
          setUploadProgress(Math.round(85 - refWeight * 85 + p * refWeight * 85))
        );
        ref_s3_key = presign.ref_s3_key;
      }

      // Step 3 — finalize
      setUploadProgress(90);
      const { data } = await axios.post(
        `${API}/architects/inspections/finalize`,
        {
          inspection_id: presign.inspection_id,
          s3_key: presign.s3_key,
          project_id: uploadForm.project_id,
          title: uploadForm.title,
          inspection_type: uploadForm.inspection_type,
          notes: uploadForm.notes || undefined,
          ...(ref_s3_key ? { ref_s3_key } : {}),
        },
        { withCredentials: true }
      );
      setUploadProgress(100);
      const isImg = presign.is_image;
      toast.success(`${isImg ? "Image" : "Video"} uploaded — analysis running in background`);
      setUploadDialogOpen(false);
      setUploadForm({ project_id: "", title: "", inspection_type: "defect_detection", notes: "", file: null, design_reference: null });
      navigate(`/architects/inspection/${data.inspection_id}`);
      fetchAll();
    } catch (err) {
      toast.error(err?.message || err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-[#080d1c] flex items-center justify-center text-[#F5F5F0]">
        <div className="max-w-md mx-auto px-6 text-center">
          <Video className="w-14 h-14 mx-auto text-[#D4AF37] mb-6" />
          <h1 className="font-display text-3xl mb-3">Emaira Architects Studio</h1>
          <p className="text-[#A8A8A0] mb-6">Sign in with your Emaira account to start uploading inspection videos.</p>
          <Button onClick={login} className="btn-gold" data-testid="architects-dashboard-signin">Sign In</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#080d1c] text-[#F5F5F0]">
      <nav className="fixed top-0 left-0 right-0 z-50 glass-dark border-b border-[#1a1a1a]">
        <div className="max-w-7xl mx-auto px-6 h-16 lg:h-20 flex items-center justify-between">
          <Link to="/architects" className="flex items-center gap-3">
            <img src="/logo.jpg" alt="Emaira" className="w-10 h-10 rounded object-cover" />
            <div className="leading-tight hidden sm:block">
              <div className="font-display text-lg">Emaira<span className="text-[#D4AF37]">.</span>Architects</div>
              <div className="text-[10px] tracking-[0.2em] text-[#A8A8A0] uppercase">Studio</div>
            </div>
          </Link>
          <div className="flex items-center gap-3">
            <Link to="/" className="hidden md:inline text-sm text-[#A8A8A0] hover:text-[#F5F5F0]">Emaira.Art</Link>
            <Button variant="ghost" size="sm" onClick={logout} className="text-[#A8A8A0] hover:text-[#F5F5F0]">Logout</Button>
          </div>
        </div>
      </nav>

      <div className="pt-24 sm:pt-28 pb-16 max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-6 sm:mb-8">
          <div className="min-w-0">
            <h1 className="font-display text-2xl sm:text-3xl lg:text-5xl mb-1 break-words" data-testid="architects-dashboard-title">
              Welcome, {user.name?.split(" ")[0]}
            </h1>
            <p className="text-[#A8A8A0] text-xs sm:text-sm">Your construction QC workspace.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" className="border-[#333] text-[#F5F5F0] hover:bg-[#111] flex-1 sm:flex-none min-w-0" onClick={() => setProjectDialogOpen(true)} data-testid="architects-new-project">
              <FolderPlus className="w-4 h-4 mr-1.5" /> <span className="truncate">New Project</span>
            </Button>
            <Button className="btn-gold flex-1 sm:flex-none min-w-0" onClick={() => setUploadDialogOpen(true)} disabled={projects.length === 0} data-testid="architects-new-inspection">
              <UploadCloud className="w-4 h-4 mr-1.5" /> <span className="truncate">Upload Video</span>
            </Button>
          </div>
        </div>

        {/* KPI */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 mb-8 sm:mb-10">
          <div className="card-obsidian rounded-xl p-4 sm:p-5">
            <Building2 className="w-5 h-5 text-[#D4AF37] mb-2 sm:mb-3" />
            <div className="font-display text-2xl sm:text-3xl">{projects.length}</div>
            <div className="text-[10px] sm:text-xs text-[#A8A8A0]">Projects</div>
          </div>
          <div className="card-obsidian rounded-xl p-4 sm:p-5">
            <Video className="w-5 h-5 text-[#D4AF37] mb-2 sm:mb-3" />
            <div className="font-display text-2xl sm:text-3xl">{inspections.length}</div>
            <div className="text-[10px] sm:text-xs text-[#A8A8A0]">Inspections</div>
          </div>
          <div className="card-obsidian rounded-xl p-4 sm:p-5">
            <AlertTriangle className="w-5 h-5 text-rose-400 mb-2 sm:mb-3" />
            <div className="font-display text-2xl sm:text-3xl">{inspections.reduce((s, i) => s + (i.defects_count || 0), 0)}</div>
            <div className="text-[10px] sm:text-xs text-[#A8A8A0]">Defects flagged</div>
          </div>
          <div className="card-obsidian rounded-xl p-4 sm:p-5">
            <HardHat className="w-5 h-5 text-amber-400 mb-2 sm:mb-3" />
            <div className="font-display text-2xl sm:text-3xl">{inspections.reduce((s, i) => s + (i.safety_violations_count || 0), 0)}</div>
            <div className="text-[10px] sm:text-xs text-[#A8A8A0]">Safety violations</div>
          </div>
        </div>

        {/* Inspections grouped by project */}
        <h2 className="font-display text-2xl mb-5">Recent Inspections</h2>
        {loading ? (
          <div className="space-y-8">
            {[0, 1].map((g) => (
              <div key={g}>
                <div className="skeleton-dark h-5 w-48 rounded mb-4" />
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[0, 1, 2].map((i) => (
                    <div key={i} className="card-obsidian rounded-2xl overflow-hidden">
                      <div className="skeleton-dark h-44" />
                      <div className="p-4 space-y-2">
                        <div className="skeleton-dark h-4 w-3/4 rounded" />
                        <div className="skeleton-dark h-3 w-full rounded mt-3" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : inspections.length === 0 ? (
          <div className="card-obsidian rounded-xl p-12 text-center">
            <Video className="w-10 h-10 mx-auto text-[#444] mb-3" />
            <p className="text-[#A8A8A0] mb-4">No inspections yet. Start by creating a project, then upload a site video.</p>
            <Button className="btn-gold" onClick={() => projects.length ? setUploadDialogOpen(true) : setProjectDialogOpen(true)}>
              <Plus className="w-4 h-4 mr-1" /> {projects.length ? "Upload video" : "Create project"}
            </Button>
          </div>
        ) : (() => {
          // Group inspections by project_id, preserving order of first occurrence
          const grouped = [];
          const seen = {};
          inspections.forEach((insp) => {
            const pid = insp.project_id || "__none__";
            if (!seen[pid]) {
              seen[pid] = true;
              grouped.push({ project: projects.find((p) => p.project_id === pid), items: [] });
            }
            grouped[grouped.findIndex((g) => (g.project?.project_id || "__none__") === pid)].items.push(insp);
          });
          return (
            <div className="space-y-10">
              {grouped.map(({ project, items }) => (
                <div key={project?.project_id || "__none__"}>
                  {/* Project header */}
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-1 h-6 rounded-full bg-[#D4AF37]" />
                    <div>
                      <h3 className="font-display text-lg sm:text-xl leading-tight">{project?.name || "Uncategorized"}</h3>
                      {project?.location && <p className="text-[11px] text-[#666660]">{project.location}</p>}
                    </div>
                    <span className="ml-auto text-[11px] text-[#666660]">{items.length} inspection{items.length !== 1 ? "s" : ""}</span>
                  </div>
                  {/* Cards */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
                    {items.map((insp) => {
                      const type = INSPECTION_TYPES.find((t) => t.value === insp.inspection_type) || INSPECTION_TYPES[0];
                      const TypeIcon = type.icon;
                      const thumbSrc = insp.status !== "uploaded" ? `${API}/architects/inspections/${insp.inspection_id}/keyframe` : null;
                      const fallback = FALLBACK_PHOTOS[inspections.indexOf(insp) % FALLBACK_PHOTOS.length];
                      return (
                        <Link
                          key={insp.inspection_id}
                          to={`/architects/inspection/${insp.inspection_id}`}
                          data-testid={`architects-inspection-card-${insp.inspection_id}`}
                          className="group card-obsidian rounded-2xl overflow-hidden border border-transparent hover:border-[#D4AF37]/40 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-[#D4AF37]/5"
                        >
                          {/* Thumbnail */}
                          <div className="relative h-56 bg-[#0d0d0d] overflow-hidden">
                            {thumbSrc ? (
                              <img
                                src={thumbSrc}
                                alt={insp.title}
                                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                                onError={(e) => { e.currentTarget.style.display = "none"; e.currentTarget.nextSibling.style.display = "block"; }}
                              />
                            ) : null}
                            <img
                              src={fallback}
                              alt=""
                              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                              style={{ display: thumbSrc ? "none" : "block" }}
                            />
                            <div className="absolute inset-0 bg-gradient-to-t from-[#080d1c]/80 via-transparent to-transparent" />
                            <div className="absolute top-3 left-3 right-3 flex items-start justify-between">
                              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium backdrop-blur-sm bg-black/40 border border-white/10 ${type.color}`}>
                                <TypeIcon className="w-3 h-3" />
                                {type.label.split(" (")[0]}
                              </span>
                              {insp.status === "completed" ? (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] backdrop-blur-sm bg-emerald-900/60 text-emerald-300 border border-emerald-800/50"><CheckCircle2 className="w-3 h-3" />Done</span>
                              ) : insp.status === "analyzing" ? (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] backdrop-blur-sm bg-sky-900/60 text-sky-300 border border-sky-800/50"><Loader2 className="w-3 h-3 animate-spin" />Analyzing</span>
                              ) : insp.status === "failed" ? (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] backdrop-blur-sm bg-rose-900/60 text-rose-300 border border-rose-800/50">Failed</span>
                              ) : (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] backdrop-blur-sm bg-black/40 text-[#A8A8A0] border border-white/10"><Clock className="w-3 h-3" />Uploaded</span>
                              )}
                            </div>
                            <div className="absolute bottom-3 right-3 w-8 h-8 rounded-full bg-[#D4AF37]/20 border border-[#D4AF37]/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                              <Play className="w-3.5 h-3.5 text-[#D4AF37] ml-0.5" />
                            </div>
                          </div>
                          {/* Card body */}
                          <div className="p-4">
                            <h3 className="font-medium text-sm sm:text-base leading-snug mb-3 line-clamp-2 group-hover:text-[#D4AF37] transition-colors">
                              {insp.title}
                            </h3>
                            <div className="flex items-center gap-0 border-t border-[#1a1a1a] pt-3">
                              <div className="flex-1 text-center">
                                <div className="text-sm font-mono font-semibold text-rose-400">{insp.defects_count || 0}</div>
                                <div className="text-[10px] text-[#666660] mt-0.5">Defects</div>
                              </div>
                              <div className="w-px h-8 bg-[#1a1a1a]" />
                              <div className="flex-1 text-center">
                                <div className="text-sm font-mono font-semibold text-amber-400">{insp.safety_violations_count || 0}</div>
                                <div className="text-[10px] text-[#666660] mt-0.5">Safety</div>
                              </div>
                              <div className="w-px h-8 bg-[#1a1a1a]" />
                              <div className="flex-1 text-center">
                                <div className="text-sm font-mono font-semibold text-sky-400">{insp.design_deviations_count || 0}</div>
                                <div className="text-[10px] text-[#666660] mt-0.5">Design</div>
                              </div>
                              {insp.overall_risk_level && (
                                <>
                                  <div className="w-px h-8 bg-[#1a1a1a]" />
                                  <div className="flex-1 text-center">
                                    <div className={`text-[10px] font-semibold uppercase tracking-wide mt-1 ${RISK_BADGE[insp.overall_risk_level]?.split(" ")[1] || "text-emerald-400"}`}>
                                      {insp.overall_risk_level}
                                    </div>
                                    <div className="text-[10px] text-[#666660] mt-0.5">Risk</div>
                                  </div>
                                </>
                              )}
                            </div>
                          </div>
                        </Link>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          );
        })()}
      </div>

      {/* Create project dialog */}
      <Dialog open={projectDialogOpen} onOpenChange={setProjectDialogOpen}>
        <DialogContent className="bg-[#0a0a0a] border-[#1a1a1a] text-[#F5F5F0] w-[95vw] max-w-md max-h-[92vh] overflow-y-auto p-4 sm:p-6 rounded-xl">
          <DialogHeader>
            <DialogTitle className="font-display text-xl sm:text-2xl">New Project</DialogTitle>
            <DialogDescription className="text-[#A8A8A0] text-xs sm:text-sm">Group related inspections under a single site or build.</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreateProject} className="space-y-4">
            <div>
              <label className="text-xs text-[#A8A8A0]">Project name *</label>
              <Input value={projectForm.name} onChange={(e) => setProjectForm({ ...projectForm, name: e.target.value })} placeholder="Tower A — Phase 2" className="mt-1 bg-[#111] border-[#1a1a1a] text-[#F5F5F0]" data-testid="architects-project-name-input" />
            </div>
            <div>
              <label className="text-xs text-[#A8A8A0]">Location</label>
              <Input value={projectForm.location} onChange={(e) => setProjectForm({ ...projectForm, location: e.target.value })} placeholder="Dubai, UAE" className="mt-1 bg-[#111] border-[#1a1a1a] text-[#F5F5F0]" />
            </div>
            <div>
              <label className="text-xs text-[#A8A8A0]">Type</label>
              <Select value={projectForm.project_type} onValueChange={(v) => setProjectForm({ ...projectForm, project_type: v })}>
                <SelectTrigger className="mt-1 bg-[#111] border-[#1a1a1a] text-[#F5F5F0]"><SelectValue /></SelectTrigger>
                <SelectContent className="bg-[#0a0a0a] border-[#1a1a1a] text-[#F5F5F0]">
                  <SelectItem value="commercial">Commercial</SelectItem>
                  <SelectItem value="residential">Residential</SelectItem>
                  <SelectItem value="infra">Infrastructure</SelectItem>
                  <SelectItem value="industrial">Industrial</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-xs text-[#A8A8A0]">Description</label>
              <Textarea value={projectForm.description} onChange={(e) => setProjectForm({ ...projectForm, description: e.target.value })} className="mt-1 bg-[#111] border-[#1a1a1a] text-[#F5F5F0] min-h-[80px]" />
            </div>
            <Button type="submit" className="w-full btn-gold" disabled={creatingProject} data-testid="architects-project-submit">
              {creatingProject ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <FolderPlus className="w-4 h-4 mr-2" />}
              Create Project
            </Button>
          </form>
        </DialogContent>
      </Dialog>

      {/* Upload dialog */}
      <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
        <DialogContent className="bg-[#0a0a0a] border-[#1a1a1a] text-[#F5F5F0] w-[95vw] max-w-lg max-h-[92vh] overflow-y-auto p-4 sm:p-6 rounded-xl">
          <DialogHeader>
            <DialogTitle className="font-display text-xl sm:text-2xl">Upload Inspection Video</DialogTitle>
            <DialogDescription className="text-[#A8A8A0] text-xs sm:text-sm">MP4, MOV or WebM up to 500 MB. Gemini 3 Pro will analyze immediately after upload.</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleUpload} className="space-y-4">
            <div>
              <label className="text-xs text-[#A8A8A0]">Project *</label>
              <Select value={uploadForm.project_id} onValueChange={(v) => setUploadForm({ ...uploadForm, project_id: v })}>
                <SelectTrigger className="mt-1 bg-[#111] border-[#1a1a1a] text-[#F5F5F0]" data-testid="architects-upload-project-trigger"><SelectValue placeholder="Select a project" /></SelectTrigger>
                <SelectContent className="bg-[#0a0a0a] border-[#1a1a1a] text-[#F5F5F0]">
                  {projects.map((p) => <SelectItem key={p.project_id} value={p.project_id}>{p.name}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-xs text-[#A8A8A0]">Title *</label>
              <Input value={uploadForm.title} onChange={(e) => setUploadForm({ ...uploadForm, title: e.target.value })} placeholder="Tower A — L7 slab walkthrough" className="mt-1 bg-[#111] border-[#1a1a1a] text-[#F5F5F0]" />
            </div>
            <div>
              <label className="text-xs text-[#A8A8A0]">Inspection type</label>
              <div className="grid grid-cols-3 gap-2 mt-1">
                {INSPECTION_TYPES.map((t) => {
                  const Icon = t.icon;
                  const active = uploadForm.inspection_type === t.value;
                  return (
                    <button
                      type="button"
                      key={t.value}
                      onClick={() => setUploadForm({ ...uploadForm, inspection_type: t.value })}
                      className={`p-2 sm:p-3 rounded-lg border text-center transition-colors min-h-[64px] ${active ? "border-[#D4AF37] bg-[#D4AF37]/10 text-[#D4AF37]" : "border-[#1a1a1a] text-[#A8A8A0] hover:border-[#333]"}`}
                      data-testid={`architects-type-${t.value}`}
                    >
                      <Icon className={`w-5 h-5 mx-auto mb-1 ${active ? "text-[#D4AF37]" : t.color}`} />
                      <span className="text-[10px] block leading-tight break-words">{t.label.split(" (")[0]}</span>
                    </button>
                  );
                })}
              </div>
            </div>
            <div>
              <label className="text-xs text-[#A8A8A0]">Video file (MP4, MOV, WebM · ≤ 500 MB)</label>
              {/* On phones, show two side-by-side options: Take video / Choose file */}
              <input
                ref={fileInputRef}
                type="file"
                accept="video/mp4,video/quicktime,video/webm,video/x-m4v,video/*"
                onChange={handleFileSelect}
                className="hidden"
              />
              <input
                ref={cameraInputRef}
                type="file"
                accept="video/*"
                capture="environment"
                onChange={handleFileSelect}
                className="hidden"
                data-testid="architects-camera-capture-input"
              />
              <div className="grid grid-cols-2 gap-2 mt-1">
                <button
                  type="button"
                  onClick={() => cameraInputRef.current?.click()}
                  className="p-3 sm:p-4 rounded-lg border-2 border-dashed border-[#333] hover:border-[#D4AF37] active:border-[#D4AF37] text-xs sm:text-sm text-[#A8A8A0] transition-colors flex flex-col items-center gap-1.5 min-h-[80px]"
                  data-testid="architects-record-camera-btn"
                >
                  <Smartphone className="w-5 h-5" />
                  <span>Record on phone</span>
                </button>
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="p-3 sm:p-4 rounded-lg border-2 border-dashed border-[#333] hover:border-[#D4AF37] active:border-[#D4AF37] text-xs sm:text-sm text-[#A8A8A0] transition-colors flex flex-col items-center gap-1.5 min-h-[80px]"
                  data-testid="architects-upload-file-btn"
                >
                  <UploadCloud className="w-5 h-5" />
                  <span>Choose file</span>
                </button>
              </div>
              {uploadForm.file && (
                <p className="mt-2 text-[11px] text-[#D4AF37] break-all px-1" data-testid="architects-selected-file">
                  📼 {uploadForm.file.name} ({(uploadForm.file.size / 1_048_576).toFixed(1)} MB)
                </p>
              )}
            </div>
            {uploadForm.inspection_type === "design_validation" && (
              <div>
                <label className="text-xs text-[#A8A8A0]">BIM / Design reference (JPG, PNG, WebP · ≤ 25 MB · optional)</label>
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={(e) => setUploadForm((s) => ({ ...s, design_reference: e.target.files?.[0] || null }))}
                  className="mt-1 block w-full text-xs sm:text-sm text-[#A8A8A0] file:mr-2 sm:file:mr-3 file:py-2 file:px-3 sm:file:px-4 file:rounded file:border-0 file:bg-[#1a1a1a] file:text-[#D4AF37] hover:file:bg-[#222]"
                  data-testid="architects-design-ref-input"
                />
                {uploadForm.design_reference && (
                  <p className="text-[10px] text-[#666] mt-1 break-all">📐 {uploadForm.design_reference.name} ({(uploadForm.design_reference.size / 1024).toFixed(0)} KB)</p>
                )}
              </div>
            )}
            <div>
              <label className="text-xs text-[#A8A8A0]">Notes (optional)</label>
              <Textarea value={uploadForm.notes} onChange={(e) => setUploadForm({ ...uploadForm, notes: e.target.value })} className="mt-1 bg-[#111] border-[#1a1a1a] text-[#F5F5F0] min-h-[60px]" />
            </div>
            {uploading && (
              <div>
                <Progress value={uploadProgress} className="h-1.5" />
                <p className="text-[10px] text-[#666] mt-1 text-center">Uploading {uploadProgress}%</p>
              </div>
            )}
            <Button type="submit" className="w-full btn-gold py-5 text-base" disabled={uploading} data-testid="architects-upload-submit">
              {uploading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 mr-2" />}
              Upload & Analyze
            </Button>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ArchitectsDashboard;
