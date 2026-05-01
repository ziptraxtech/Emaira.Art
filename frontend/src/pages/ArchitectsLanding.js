import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Camera,
  HardHat,
  Ruler,
  ShieldCheck,
  Video,
  Sparkles,
  ArrowRight,
  CheckCircle,
  Building2,
  Activity,
  Layers,
  MapPin,
  Globe,
} from "lucide-react";

const CAPABILITIES = [
  {
    icon: Camera,
    title: "Real-world Defect Detection",
    desc: "Cracks, spalling, honeycombing, rebar exposure, efflorescence — Gemini 3 Pro scans every frame and timestamps every issue.",
    color: "from-rose-500/20 to-rose-500/5",
    ring: "ring-rose-500/30",
  },
  {
    icon: HardHat,
    title: "Activity & Safety Monitoring",
    desc: "Missing PPE, unsafe edges, scaffolding risks, unsafe behavior — 3D-CNN-style activity classification with location hints.",
    color: "from-amber-500/20 to-amber-500/5",
    ring: "ring-amber-500/30",
  },
  {
    icon: Ruler,
    title: "Reality vs. Design Validation",
    desc: "Upload a site video alongside your BIM/drawing — Emaira AI calls out deviations in column placement, openings, MEP routing.",
    color: "from-sky-500/20 to-sky-500/5",
    ring: "ring-sky-500/30",
  },
];

const WORKFLOW = [
  { n: "01", title: "Upload", desc: "Drag-and-drop MP4/MOV from drones, helmet cams, or fixed site cameras. Up to 500 MB per clip." },
  { n: "02", title: "Analyze", desc: "Gemini 3 Pro reviews the video end-to-end. OpenCV extracts 6 keyframes for the report UI." },
  { n: "03", title: "Review", desc: "Findings with severity, confidence, timestamp and bbox hint — jump to the exact second in the player." },
  { n: "04", title: "Act", desc: "Export a PDF/JSON report, share with contractors, or wire up Slack/Teams alerts (Pro+)." },
];

const ArchitectsLanding = () => {
  return (
    <div className="min-h-screen bg-[#050505] text-[#F5F5F0]" data-testid="architects-landing">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass-dark border-b border-[#1a1a1a]">
        <div className="max-w-7xl mx-auto px-6 h-16 lg:h-20 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded bg-gradient-to-br from-[#D4AF37] to-[#B8860B] flex items-center justify-center">
              <span className="font-display text-[#050505] text-xl font-bold">E</span>
            </div>
            <div className="leading-tight hidden sm:block">
              <div className="font-display text-lg">Emaira<span className="text-[#D4AF37]">.</span>Architects</div>
              <div className="text-[10px] tracking-[0.2em] text-[#A8A8A0] uppercase">Construction QC · AI</div>
            </div>
          </Link>
          <div className="hidden md:flex items-center gap-8 text-sm text-[#A8A8A0]">
            <a href="#capabilities" className="hover:text-[#F5F5F0] transition-colors">Capabilities</a>
            <a href="#cities" className="hover:text-[#F5F5F0] transition-colors">Markets</a>
            <a href="#workflow" className="hover:text-[#F5F5F0] transition-colors">Workflow</a>
            <Link to="/architects/pricing" className="hover:text-[#F5F5F0] transition-colors">Pricing</Link>
            <Link to="/art" className="hover:text-[#F5F5F0] transition-colors">Emaira.Art</Link>
          </div>
          <Link to="/architects/dashboard">
            <Button className="btn-gold text-sm" data-testid="architects-nav-launch">
              Launch Studio <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 lg:pt-40 pb-0 relative overflow-hidden">
        <div className="absolute inset-0 opacity-[0.08] pointer-events-none"
             style={{ backgroundImage: "linear-gradient(rgba(212,175,55,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(212,175,55,0.5) 1px, transparent 1px)", backgroundSize: "56px 56px" }} />
        <div className="max-w-7xl mx-auto px-6 relative">
          {/* Two-col on desktop: text left, image right. Stacked on mobile. */}
          <div className="grid lg:grid-cols-2 gap-10 items-center mb-10">
            <div>
              <Badge className="bg-[#D4AF37]/15 text-[#D4AF37] border-[#D4AF37]/30 mb-6">
                <Sparkles className="w-3 h-3 mr-1" /> New Business Line · Powered by Gemini 3 Pro
              </Badge>
              <h1 className="font-display text-4xl sm:text-5xl lg:text-7xl leading-[1.05] mb-6">
                Video AI<br />
                <span className="text-[#D4AF37]">QC / QA</span> for<br />
                every job site.
              </h1>
              <p className="text-lg text-[#A8A8A0] max-w-xl mb-8">
                Emaira Architects ingests your site video and returns a structural defect log, a PPE safety sheet, and design-vs-reality deviations — in minutes, not weeks.
              </p>
              <div className="flex flex-col sm:flex-row gap-3">
                <Link to="/architects/dashboard">
                  <Button className="btn-gold text-base px-6 py-6 w-full sm:w-auto" data-testid="architects-hero-cta">
                    <Video className="w-4 h-4 mr-2" /> Start an Inspection
                  </Button>
                </Link>
                <Link to="/architects/pricing">
                  <Button variant="outline" className="border-[#333] text-[#F5F5F0] hover:bg-[#111] px-6 py-6 w-full sm:w-auto">
                    See Pricing
                  </Button>
                </Link>
              </div>
            </div>
            {/* Construction image — desktop only */}
            <div className="hidden lg:block relative">
              <div className="absolute -inset-4 rounded-2xl bg-gradient-to-br from-[#D4AF37]/20 via-transparent to-transparent blur-3xl" />
              <div className="relative rounded-xl overflow-hidden border border-[#222]">
                <img
                  src="https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=1200&q=80"
                  alt="Construction site"
                  className="w-full h-full object-cover opacity-90"
                  style={{ maxHeight: "420px" }}
                />
                <div className="absolute top-4 left-4 bg-[#050505]/80 backdrop-blur-sm border border-[#D4AF37]/40 rounded px-2.5 py-1 text-[10px] font-mono text-[#D4AF37] uppercase tracking-wider">
                  ● Emaira AI · Site Overview
                </div>
                <div className="absolute top-14 left-8 w-24 h-24 rounded border border-rose-500/80 animate-pulse">
                  <span className="absolute -top-5 left-0 text-[10px] font-mono text-rose-400">CRACK · 87%</span>
                </div>
                <div className="absolute bottom-10 right-8 w-28 h-28 rounded border border-amber-400/80">
                  <span className="absolute -top-5 left-0 text-[10px] font-mono text-amber-300">NO HARDHAT · 92%</span>
                </div>
                <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-[#050505] to-transparent" />
              </div>
            </div>
          </div>
        </div>

        {/* Full-width video panel */}
        <div className="relative mt-4">
          <div className="absolute -inset-1 bg-gradient-to-b from-[#D4AF37]/10 via-transparent to-transparent pointer-events-none" />
          <div className="mx-auto max-w-7xl px-6">
            <div className="relative rounded-t-2xl overflow-hidden border border-[#222] border-b-0 shadow-[0_-20px_80px_-20px_rgba(212,175,55,0.25)]">
              {/* HUD bar */}
              <div className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between px-5 py-3 bg-[#050505]/70 backdrop-blur-md border-b border-[#D4AF37]/20">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-[#D4AF37] animate-pulse" />
                  <span className="text-[11px] font-mono text-[#D4AF37] uppercase tracking-widest">Emaira AI · Live Analysis</span>
                </div>
                <div className="hidden sm:flex items-center gap-6 text-[11px] font-mono text-[#A8A8A0]">
                  <span className="text-rose-400">● Defects: 3</span>
                  <span className="text-amber-400">● Safety: 2</span>
                  <span className="text-blue-400">● Design: 1</span>
                </div>
              </div>
              <video
                src="/site-demo.mp4"
                autoPlay
                loop
                muted
                playsInline
                className="w-full object-cover"
                style={{ maxHeight: "520px" }}
              />
              {/* Bottom gradient fade */}
              <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-[#050505] to-transparent pointer-events-none" />
            </div>
          </div>
        </div>
      </section>

      {/* About — Eliminating the visibility gap */}
      <section className="py-20 border-t border-[#111]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="font-display text-4xl lg:text-5xl leading-tight mb-6">
                Eliminating the visibility gap in modern construction
              </h2>
              <p className="text-[#A8A8A0] text-lg leading-relaxed mb-4">
                Emaira is an AI-first B2B SaaS platform that removes manual data entry from the project management lifecycle. By leveraging magnet-mounted 360-degree cameras and proprietary computer vision, we automate defect detection and progress tracking.
              </p>
              <p className="text-[#A8A8A0] text-lg leading-relaxed">
                No special hardware required — use any <span className="text-[#F5F5F0]">smartphone camera</span>, drone, helmet-cam, or dedicated <span className="text-[#F5F5F0]">360° camera</span>. If it captures video, Emaira can analyse it.
              </p>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {[
                { label: "Smartphone camera", icon: "📱", color: "from-blue-900/40 to-blue-800/10", ring: "ring-blue-800/30" },
                { label: "360° special cams", icon: "🔭", color: "from-violet-900/40 to-violet-800/10", ring: "ring-violet-800/30" },
                { label: "Drone + helmet-cam", icon: "🎥", color: "from-amber-900/40 to-amber-800/10", ring: "ring-amber-700/30" },
                { label: "PDF/JSON export · 500 MB / clip", icon: "📄", color: "from-emerald-900/40 to-emerald-800/10", ring: "ring-emerald-800/30" },
              ].map((item) => (
                <div key={item.label} className={`card-obsidian rounded-xl p-5 bg-gradient-to-br ${item.color} ring-1 ${item.ring} text-center`}>
                  <div className="text-3xl mb-3">{item.icon}</div>
                  <p className="text-xs text-[#A8A8A0] leading-snug">{item.label}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Capabilities */}
      <section id="capabilities" className="py-20 border-t border-[#111]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="mb-14 max-w-2xl">
            <Badge className="bg-[#1a1a1a] text-[#D4AF37] border-[#333] mb-3">What it catches</Badge>
            <h2 className="font-display text-3xl lg:text-5xl mb-4">Three inspection lenses. One upload.</h2>
            <p className="text-[#A8A8A0]">Pick a focus, drop a clip. Emaira returns a structured report with timestamps, severities, and recommendations.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-5">
            {CAPABILITIES.map((c) => (
              <div key={c.title} className={`card-obsidian rounded-xl p-7 bg-gradient-to-br ${c.color} ring-1 ${c.ring} transition-transform hover:-translate-y-1`}>
                <c.icon className="w-8 h-8 text-[#F5F5F0] mb-5" />
                <h3 className="font-display text-xl mb-2">{c.title}</h3>
                <p className="text-sm text-[#A8A8A0] leading-relaxed">{c.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Global Cities */}
      <section id="cities" className="py-20 border-t border-[#111] relative overflow-hidden">
        <div className="absolute inset-0 opacity-[0.04] pointer-events-none"
             style={{ backgroundImage: "radial-gradient(circle at 20% 30%, #D4AF37 1px, transparent 1.5px), radial-gradient(circle at 70% 60%, #D4AF37 1px, transparent 1.5px)", backgroundSize: "120px 120px" }} />
        <div className="max-w-7xl mx-auto px-6 relative">
          <div className="mb-12 max-w-2xl">
            <Badge className="bg-[#1a1a1a] text-[#D4AF37] border-[#333] mb-3">
              <Globe className="w-3 h-3 mr-1" /> Global Footprint
            </Badge>
            <h2 className="font-display text-3xl lg:text-5xl mb-4">
              Built for the world's <span className="text-[#D4AF37]">most ambitious</span> skylines.
            </h2>
            <p className="text-[#A8A8A0]">
              Emaira Architects is the QC partner for marquee construction programs across four continents. From mile-high towers in the Gulf to data-center hyperscale builds in Silicon Valley.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { city: "Dubai", country: "UAE", flag: "🇦🇪", focus: "Hospitality · Mixed-use · Mile-high towers", projects: "Marquee partner program" },
              { city: "Mumbai", country: "India", flag: "🇮🇳", focus: "Residential high-rise · Metro infrastructure", projects: "Pilot expansion 2026" },
              { city: "Singapore", country: "Singapore", flag: "🇸🇬", focus: "Smart city · Sustainable construction", projects: "Reg-tech compliant deployments" },
              { city: "San Francisco", country: "USA", flag: "🇺🇸", focus: "Data centers · Tech HQ · Seismic retrofit", projects: "West coast launch hub" },
            ].map((c) => (
              <div key={c.city} data-testid={`city-card-${c.city.toLowerCase().replace(/\s/g, '-')}`} className="card-obsidian rounded-xl p-6 hover:border-[#D4AF37]/40 border border-[#1a1a1a] transition-colors group">
                <div className="flex items-start justify-between mb-3">
                  <span className="text-3xl">{c.flag}</span>
                  <MapPin className="w-4 h-4 text-[#666] group-hover:text-[#D4AF37] transition-colors" />
                </div>
                <h3 className="font-display text-2xl">{c.city}</h3>
                <p className="text-[10px] tracking-[0.2em] uppercase text-[#666660] mb-3">{c.country}</p>
                <p className="text-xs text-[#A8A8A0] leading-relaxed mb-3">{c.focus}</p>
                <p className="text-[10px] text-[#D4AF37] font-mono">→ {c.projects}</p>
              </div>
            ))}
          </div>
          <p className="text-center text-xs text-[#666660] mt-10">
            …and more cities coming online: <span className="text-[#A8A8A0]">London · Toronto · Riyadh · Hong Kong · Sydney · Tokyo · Berlin · São Paulo</span>
          </p>
        </div>
      </section>

      {/* Workflow */}
      <section id="workflow" className="py-20 bg-[#080808] border-y border-[#111]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="mb-14 max-w-2xl">
            <Badge className="bg-[#1a1a1a] text-[#D4AF37] border-[#333] mb-3">How it works</Badge>
            <h2 className="font-display text-3xl lg:text-5xl mb-4">From footage to findings in four steps.</h2>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-5">
            {WORKFLOW.map((s) => (
              <div key={s.n} className="card-obsidian rounded-xl p-6">
                <div className="font-display text-4xl text-[#D4AF37] mb-3">{s.n}</div>
                <h3 className="font-display text-lg mb-2">{s.title}</h3>
                <p className="text-sm text-[#A8A8A0] leading-relaxed">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats / trust */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-3 gap-8 text-center">
          {[
            { icon: Building2, kpi: "40+", label: "sites analyzed in pilot" },
            { icon: Activity, kpi: "94%", label: "avg. defect-detection recall" },
            { icon: Layers, kpi: "12×", label: "faster than manual walkthroughs" },
          ].map((s) => (
            <div key={s.label} className="card-obsidian rounded-xl p-8">
              <s.icon className="w-6 h-6 mx-auto text-[#D4AF37] mb-4" />
              <div className="font-display text-5xl text-[#F5F5F0] mb-1">{s.kpi}</div>
              <div className="text-sm text-[#A8A8A0]">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-6">
          <div className="card-obsidian rounded-2xl p-10 lg:p-16 text-center relative overflow-hidden">
            <div className="absolute -top-16 -right-16 w-64 h-64 rounded-full bg-[#D4AF37]/10 blur-3xl" />
            <ShieldCheck className="w-10 h-10 mx-auto text-[#D4AF37] mb-5" />
            <h2 className="font-display text-3xl lg:text-5xl mb-4">Give your next inspection superpowers.</h2>
            <p className="text-[#A8A8A0] mb-8 max-w-xl mx-auto">
              Start with 2 free inspections. Upgrade when you're ready to scale across every project.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link to="/architects/dashboard">
                <Button className="btn-gold px-6 py-6" data-testid="architects-footer-cta">
                  <Video className="w-4 h-4 mr-2" /> Upload a Test Video
                </Button>
              </Link>
              <Link to="/architects/pricing">
                <Button variant="outline" className="border-[#333] text-[#F5F5F0] hover:bg-[#111] px-6 py-6">
                  Compare Plans
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      <footer className="py-10 border-t border-[#111] text-center text-xs text-[#555]">
        © 2026 Emaira Labs · <Link to="/art" className="hover:text-[#D4AF37]">Explore Emaira.Art</Link>
      </footer>
    </div>
  );
};

export default ArchitectsLanding;
