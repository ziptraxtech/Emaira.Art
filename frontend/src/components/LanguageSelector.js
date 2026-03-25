import { useTranslation } from 'react-i18next';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Globe } from "lucide-react";

const languages = [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'zh', name: '中文', flag: '🇨🇳' },
  { code: 'ar', name: 'العربية', flag: '🇸🇦', rtl: true }
];

const LanguageSelector = ({ variant = "default" }) => {
  const { i18n } = useTranslation();
  
  const currentLanguage = languages.find(l => l.code === i18n.language) || languages[0];
  
  const changeLanguage = (langCode) => {
    i18n.changeLanguage(langCode);
    // Set RTL direction for Arabic
    const isRTL = langCode === 'ar';
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
    document.documentElement.lang = langCode;
  };
  
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="ghost" 
          size="sm"
          className={`flex items-center gap-2 ${
            variant === "dark" 
              ? "text-[#A8A8A0] hover:text-[#F5F5F0]" 
              : "text-[#4A4A45] hover:text-[#1A1A18]"
          }`}
          data-testid="language-selector"
        >
          <Globe className="w-4 h-4" />
          <span className="hidden sm:inline">{currentLanguage.flag}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent 
        align="end" 
        className={`min-w-[140px] ${
          variant === "dark" 
            ? "bg-[#0a0a0a] border-[#1a1a1a]" 
            : "bg-white border-[#E8E8E0]"
        }`}
      >
        {languages.map((lang) => (
          <DropdownMenuItem
            key={lang.code}
            onClick={() => changeLanguage(lang.code)}
            className={`flex items-center gap-2 cursor-pointer ${
              variant === "dark"
                ? `text-[#F5F5F0] focus:bg-[#111] ${i18n.language === lang.code ? 'bg-[#111]' : ''}`
                : `text-[#1A1A18] focus:bg-[#F5F5F0] ${i18n.language === lang.code ? 'bg-[#F5F5F0]' : ''}`
            }`}
            data-testid={`lang-${lang.code}`}
          >
            <span className="text-lg">{lang.flag}</span>
            <span className={lang.rtl ? 'font-arabic' : ''}>{lang.name}</span>
            {i18n.language === lang.code && (
              <span className="ml-auto text-[#B8962F]">✓</span>
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default LanguageSelector;
