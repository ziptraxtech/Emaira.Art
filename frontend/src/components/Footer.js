import { Link } from "react-router-dom";
import { Linkedin, Instagram } from "lucide-react";

const ARCHITECTS_LINKS = [
  { label: "Home", to: "/" },
  { label: "Capabilities", to: "/#capabilities", anchor: true },
  { label: "Markets", to: "/#cities", anchor: true },
  { label: "Workflow", to: "/#workflow", anchor: true },
  { label: "Launch Studio", to: "/architects/dashboard" },
  { label: "Pricing", to: "/architects/pricing" },
];

const ART_LINKS = [
  { label: "Home", to: "/art" },
  { label: "Gallery", to: "/gallery" },
  { label: "About", to: "/about" },
  { label: "Technology", to: "/technology" },
  { label: "Events", to: "/events" },
  { label: "Pricing", to: "/pricing" },
];

const LEGAL_LINKS = [
  { label: "Terms of Use", to: "/legal/terms" },
  { label: "Privacy Policy", to: "/legal/privacy" },
  { label: "Refund & Cancellation Policy", to: "/legal/refund" },
];

const INSTAGRAM_URL = "https://www.instagram.com/emaira.art";
const LINKEDIN_URL = "https://www.linkedin.com/company/emaira/";

const renderLink = (l) => {
  if (l.anchor) {
    return (
      <a href={l.to} className="text-sm hover:text-[#F5F5F0] transition-colors">
        {l.label}
      </a>
    );
  }
  return (
    <Link to={l.to} className="text-sm hover:text-[#F5F5F0] transition-colors">
      {l.label}
    </Link>
  );
};

const Footer = ({ variant = "art" }) => {
  const isArchitects = variant === "architects";
  const productLinks = isArchitects ? ARCHITECTS_LINKS : ART_LINKS;
  const productHeading = isArchitects ? "Emaira.Architects" : "Emaira.Art";
  const homePath = isArchitects ? "/" : "/art";
  const brandLabel = isArchitects ? "Emaira.Architects" : "Emaira.Art";
  const tagline = isArchitects
    ? "AI-powered construction QC and QA — built for architects, contractors, and project owners."
    : "Where art meets AI forensics — provenance, authentication, and the hidden stories within masterpieces.";

  return (
    <footer className="bg-[#0a0f1f] border-t border-[#1a1a1a] text-[#A8A8A0]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 md:gap-14">
          <div className="space-y-4">
            <Link to={homePath} className="inline-flex items-center gap-2">
              <div className="w-9 h-9 rounded bg-gradient-to-br from-[#D4AF37] to-[#B8962F] flex items-center justify-center">
                <span className="font-display text-white text-base font-bold">E</span>
              </div>
              <span className="font-display text-xl text-[#F5F5F0]">{brandLabel}</span>
            </Link>
            <p className="text-sm leading-relaxed max-w-sm">{tagline}</p>
          </div>

          <div>
            <h4 className="font-display text-base text-[#D4AF37] mb-4">{productHeading}</h4>
            <ul className="space-y-2">
              {productLinks.map((l) => (
                <li key={l.label}>{renderLink(l)}</li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-display text-base text-[#D4AF37] mb-4">Legal</h4>
            <ul className="space-y-2">
              {LEGAL_LINKS.map((l) => (
                <li key={l.label}>{renderLink(l)}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-[#1a1330] via-[#2a1850] to-[#c44a1a]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-sm text-[#F5F5F0]">
          <span>Copyright {new Date().getFullYear()}. All Rights Reserved</span>
          <div className="flex items-center gap-4">
            <span className="text-[#F5F5F0]/80">Follow us on</span>
            <a href={LINKEDIN_URL} target="_blank" rel="noreferrer" aria-label="LinkedIn" className="w-8 h-8 rounded bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors">
              <Linkedin className="w-4 h-4" />
            </a>
            <a href={INSTAGRAM_URL} target="_blank" rel="noreferrer" aria-label="Instagram" className="w-8 h-8 rounded bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors">
              <Instagram className="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
