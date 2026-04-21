import { useState, useRef } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Wand2, Sparkles, ChevronRight } from "lucide-react";

/**
 * Interactive before/after slider showcasing AI Art Restoration.
 * Uses a single high-resolution Wikimedia Commons masterpiece image
 * with a CSS filter stack applied to the "before" layer (aged varnish,
 * soot, craquelure look) and the original image as the "after" layer.
 * Drag the handle (or touch) to reveal the restoration.
 */
const RestorationTeaser = () => {
  const [pos, setPos] = useState(42); // 0 = all Before, 100 = all After
  const trackRef = useRef(null);
  const draggingRef = useRef(false);

  const IMG_URL =
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/1280px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg";

  const updateFromClientX = (clientX) => {
    const track = trackRef.current;
    if (!track) return;
    const rect = track.getBoundingClientRect();
    const next = ((clientX - rect.left) / rect.width) * 100;
    setPos(Math.max(0, Math.min(100, next)));
  };

  const handleMouseDown = (e) => {
    draggingRef.current = true;
    updateFromClientX(e.clientX);
  };
  const handleMouseMove = (e) => {
    if (!draggingRef.current) return;
    updateFromClientX(e.clientX);
  };
  const handleMouseUp = () => {
    draggingRef.current = false;
  };
  const handleTouchMove = (e) => {
    if (!e.touches?.[0]) return;
    updateFromClientX(e.touches[0].clientX);
  };

  return (
    <div className="mt-20" data-testid="restoration-teaser">
      <div className="text-center mb-6">
        <Badge className="bg-[#B8962F]/15 text-[#B8962F] border-[#B8962F]/30 mb-3">
          <Sparkles className="w-3 h-3 mr-1" /> Premium Feature Preview
        </Badge>
        <h2 className="font-display text-3xl lg:text-4xl text-[#1A1A18] mb-2">
          AI Art Restoration — See the Magic
        </h2>
        <p className="text-[#4A4A45] max-w-2xl mx-auto">
          Drag the slider to reveal centuries of surface grime, yellowed varnish, and micro-craquelure
          instantly corrected by Emaira's conservator-grade AI. Unlocks with Pro Collector & Advisory.
        </p>
      </div>

      <div className="max-w-4xl mx-auto">
        <div
          ref={trackRef}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onTouchStart={(e) => updateFromClientX(e.touches[0].clientX)}
          onTouchMove={handleTouchMove}
          className="relative aspect-[4/3] w-full overflow-hidden rounded-lg shadow-[0_20px_60px_rgba(26,26,24,0.25)] bg-[#0a0a0a] select-none cursor-ew-resize"
          data-testid="restoration-teaser-slider"
        >
          {/* AFTER (restored original) */}
          <img
            src={IMG_URL}
            alt="After AI Restoration"
            className="absolute inset-0 w-full h-full object-cover pointer-events-none"
            draggable={false}
          />

          {/* BEFORE (aged & damaged) — clipped on the left */}
          <div
            className="absolute inset-0 overflow-hidden pointer-events-none"
            style={{ clipPath: `inset(0 ${100 - pos}% 0 0)` }}
          >
            <img
              src={IMG_URL}
              alt="Before AI Restoration"
              className="absolute inset-0 w-full h-full object-cover"
              style={{
                filter:
                  "sepia(0.7) saturate(0.55) brightness(0.72) contrast(1.05) hue-rotate(-12deg)",
              }}
              draggable={false}
            />
            {/* Craquelure / noise overlay */}
            <div
              className="absolute inset-0 mix-blend-multiply opacity-40"
              style={{
                backgroundImage:
                  "radial-gradient(rgba(60,30,10,0.35) 1px, transparent 1.2px), radial-gradient(rgba(30,15,5,0.25) 0.8px, transparent 1px)",
                backgroundSize: "4px 4px, 7px 7px",
              }}
            />
          </div>

          {/* Labels */}
          <span className="absolute top-4 left-4 bg-[#1A1A18]/80 text-[#F5F5F0] text-xs font-medium px-3 py-1 rounded-full backdrop-blur-sm pointer-events-none">
            Before
          </span>
          <span className="absolute top-4 right-4 bg-[#B8962F]/95 text-white text-xs font-medium px-3 py-1 rounded-full pointer-events-none">
            After — AI Restored
          </span>

          {/* Divider + handle */}
          <div
            className="absolute top-0 bottom-0 pointer-events-none"
            style={{ left: `${pos}%`, transform: "translateX(-50%)" }}
          >
            <div className="w-[2px] h-full bg-[#F5F5F0] shadow-[0_0_12px_rgba(245,245,240,0.6)]" />
            <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-10 h-10 rounded-full bg-[#B8962F] text-white flex items-center justify-center shadow-[0_6px_20px_rgba(184,150,47,0.6)] ring-4 ring-white/80">
              <Wand2 className="w-4 h-4" />
            </div>
          </div>

          {/* Attribution (kept subtle) */}
          <span className="absolute bottom-2 right-3 text-[10px] text-white/50 pointer-events-none">
            Source: The Starry Night, Vincent van Gogh (public domain)
          </span>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 mt-8">
          <Link to="/pricing#tiers">
            <Button className="btn-gold" data-testid="restoration-teaser-upgrade">
              <Wand2 className="w-4 h-4 mr-2" /> Unlock AI Restoration
              <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          </Link>
          <span className="text-sm text-[#8A8A80]">
            Included in Pro Collector ($1,499/yr) & Collector's Advisory ($4,999/yr)
          </span>
        </div>
      </div>
    </div>
  );
};

export default RestorationTeaser;
