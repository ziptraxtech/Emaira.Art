import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import Footer from "@/components/Footer";

const LegalLayout = ({ title, lastUpdated, children }) => {
  return (
    <div className="min-h-screen bg-[#FAFAF7] text-[#1A1A18] flex flex-col">
      <nav className="border-b border-[#E8E8E0] bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <Link to="/" className="inline-flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-[#D4AF37] to-[#B8962F] flex items-center justify-center">
              <span className="font-display text-white text-sm font-bold">E</span>
            </div>
            <span className="font-display text-lg text-[#1A1A18]">Emaira</span>
          </Link>
          <Link to="/" className="inline-flex items-center gap-1.5 text-sm text-[#4A4A45] hover:text-[#B8962F] transition-colors">
            <ArrowLeft className="w-4 h-4" /> Back to home
          </Link>
        </div>
      </nav>

      <main className="flex-1 max-w-4xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-12 md:py-16">
        <header className="mb-10">
          <h1 className="font-display text-3xl md:text-4xl text-[#1A1A18]">{title}</h1>
          {lastUpdated && (
            <p className="mt-2 text-sm text-[#666660]">Last updated: {lastUpdated}</p>
          )}
        </header>
        <article className="legal-prose space-y-8 text-[#2A2A28] leading-relaxed">
          {children}
        </article>
      </main>

      <Footer />
    </div>
  );
};

export default LegalLayout;
