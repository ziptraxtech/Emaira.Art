import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Translation resources
const resources = {
  en: {
    translation: {
      // Navigation
      nav: {
        gallery: "Gallery",
        about: "About",
        technology: "Technology",
        events: "Events",
        pricing: "Pricing",
        dashboard: "Dashboard",
        signIn: "Sign In",
        signOut: "Logout"
      },
      // Landing Page
      landing: {
        hero: {
          title: "Experience Art Like Never Before",
          subtitle: "Immersive VR storytelling meets AI-powered forensic analysis",
          cta: "Explore Gallery",
          learnMore: "Learn More"
        },
        features: {
          narrative: {
            title: "Narrative View",
            description: "Cinematic journey through art provenance and history"
          },
          forensic: {
            title: "Forensic View",
            description: "AI-powered analysis of pigments, signatures, and canvas"
          },
          vr: {
            title: "VR Experience",
            description: "Immersive viewing on Apple Vision Pro & Meta Quest"
          }
        },
        featured: "Featured Artworks",
        viewAll: "View All Artworks"
      },
      // Gallery
      gallery: {
        title: "Art Gallery",
        subtitle: "Explore masterpieces and their stories",
        search: "Search artworks or artists...",
        allPeriods: "All Periods",
        backToHome: "Back to Home",
        viewStory: "View Story",
        by: "by"
      },
      // Story Detail
      story: {
        backToGallery: "Back to Gallery",
        aboutArtwork: "About the Artwork",
        provenance: "Provenance",
        forensicFeatures: "Forensic Analysis Features",
        pigmentMapping: "Pigment Mapping",
        signatureAuth: "Signature Auth",
        canvasAnalysis: "Canvas Analysis",
        accessGranted: "Access Granted",
        startExperience: "Start Experience",
        shortStory: "The Short Story",
        deepDive: "The Deep Dive",
        getAccess: "Get Access",
        recommended: "RECOMMENDED",
        unlimitedAccess: "Want unlimited access?",
        viewPlans: "View Subscription Plans"
      },
      // VR Experience
      vr: {
        narrative: "Narrative",
        forensic: "Forensic",
        loading: "Preparing your experience...",
        loadingArtwork: "Loading artwork and narrative",
        notFound: "Experience not found",
        backToGallery: "Back to Gallery",
        timeline: "Story Timeline",
        scene: "Scene",
        runAnalysis: "Run AI Analysis",
        analyzing: "Analyzing...",
        generateViz: "Generate Visualization",
        generating: "Generating...",
        analysisComplete: "Analysis complete",
        pigment: "Pigment",
        signature: "Sign",
        canvas: "Canvas",
        authScore: "Auth Score",
        technique: "Technique",
        zoomIn: "Zoom In",
        zoomOut: "Zoom Out",
        rotate: "Rotate",
        reset: "Reset View"
      },
      // Pricing
      pricing: {
        title: "Subscription Plans",
        subtitle: "From single story experiences to unlimited access with AI forensics—choose the plan that fits your passion.",
        chooseExperience: "Choose Your Experience",
        cardStripe: "Card (Stripe)",
        razorpayIndia: "Razorpay (India)",
        perStory: "/ story",
        perYear: "/ year",
        mostPopular: "MOST POPULAR",
        getStarted: "Get Started",
        subscribeNow: "Subscribe Now",
        tiers: {
          shortStory: {
            name: "The Short Story",
            feature1: "One 3-minute VR experience",
            feature2: "Narrative view only"
          },
          deepDive: {
            name: "The Deep Dive",
            feature1: "Full Narrative view",
            feature2: "Complete Forensic View",
            feature3: "One masterpiece"
          },
          connoisseur: {
            name: "Annual Connoisseur",
            feature1: "Unlimited stories",
            feature2: "Monthly New Discovery drops",
            feature3: "Knowledge Dashboard",
            feature4: "Forensic markers tracking"
          },
          proCollector: {
            name: "Pro Collector",
            feature1: "All Connoisseur features",
            feature2: "Request custom Forensic Stories",
            feature3: "Priority support",
            feature4: "Exclusive previews"
          },
          advisory: {
            name: "Collector's Advisory",
            feature1: "All Pro Collector features",
            feature2: "Monthly 1-on-1 video consultation",
            feature3: "Early access to authentication reports",
            feature4: "VIP gallery event invitations",
            feature5: "Personal art portfolio analysis",
            feature6: "Direct curator hotline",
            feature7: "12 advisory sessions per year"
          }
        }
      },
      // Dashboard
      dashboard: {
        title: "Your Dashboard",
        welcome: "Welcome back",
        myStories: "My Stories",
        knowledge: "Knowledge",
        settings: "Settings",
        noStories: "No stories yet",
        startExploring: "Start exploring the gallery to unlock your first story",
        exploreGallery: "Explore Gallery",
        forensicMarkers: "Forensic Markers Learned",
        subscription: "Subscription",
        upgradeNow: "Upgrade Now"
      },
      // Common
      common: {
        loading: "Loading...",
        error: "Something went wrong",
        retry: "Try Again",
        save: "Save",
        cancel: "Cancel",
        delete: "Delete",
        edit: "Edit",
        view: "View",
        close: "Close",
        share: "Share",
        download: "Download",
        linkCopied: "Link copied to clipboard"
      },
      // Footer
      footer: {
        tagline: "Where Art Meets Intelligence",
        quickLinks: "Quick Links",
        legal: "Legal",
        privacy: "Privacy Policy",
        terms: "Terms of Service",
        contact: "Contact Us",
        copyright: "All rights reserved"
      }
    }
  },
  es: {
    translation: {
      nav: {
        gallery: "Galería",
        about: "Nosotros",
        technology: "Tecnología",
        events: "Eventos",
        pricing: "Precios",
        dashboard: "Panel",
        signIn: "Iniciar Sesión",
        signOut: "Cerrar Sesión"
      },
      landing: {
        hero: {
          title: "Experimenta el Arte Como Nunca Antes",
          subtitle: "Narración inmersiva en RV con análisis forense impulsado por IA",
          cta: "Explorar Galería",
          learnMore: "Saber Más"
        },
        features: {
          narrative: {
            title: "Vista Narrativa",
            description: "Viaje cinematográfico a través de la procedencia e historia del arte"
          },
          forensic: {
            title: "Vista Forense",
            description: "Análisis con IA de pigmentos, firmas y lienzo"
          },
          vr: {
            title: "Experiencia RV",
            description: "Visualización inmersiva en Apple Vision Pro y Meta Quest"
          }
        },
        featured: "Obras Destacadas",
        viewAll: "Ver Todas las Obras"
      },
      gallery: {
        title: "Galería de Arte",
        subtitle: "Explora obras maestras y sus historias",
        search: "Buscar obras o artistas...",
        allPeriods: "Todos los Períodos",
        backToHome: "Volver al Inicio",
        viewStory: "Ver Historia",
        by: "de"
      },
      story: {
        backToGallery: "Volver a la Galería",
        aboutArtwork: "Sobre la Obra",
        provenance: "Procedencia",
        forensicFeatures: "Características del Análisis Forense",
        pigmentMapping: "Mapeo de Pigmentos",
        signatureAuth: "Autenticación de Firma",
        canvasAnalysis: "Análisis del Lienzo",
        accessGranted: "Acceso Concedido",
        startExperience: "Iniciar Experiencia",
        shortStory: "La Historia Corta",
        deepDive: "Inmersión Profunda",
        getAccess: "Obtener Acceso",
        recommended: "RECOMENDADO",
        unlimitedAccess: "¿Quieres acceso ilimitado?",
        viewPlans: "Ver Planes de Suscripción"
      },
      vr: {
        narrative: "Narrativa",
        forensic: "Forense",
        loading: "Preparando tu experiencia...",
        loadingArtwork: "Cargando obra y narrativa",
        notFound: "Experiencia no encontrada",
        backToGallery: "Volver a la Galería",
        timeline: "Línea de Tiempo",
        scene: "Escena",
        runAnalysis: "Ejecutar Análisis IA",
        analyzing: "Analizando...",
        generateViz: "Generar Visualización",
        generating: "Generando...",
        analysisComplete: "Análisis completado",
        pigment: "Pigmento",
        signature: "Firma",
        canvas: "Lienzo",
        authScore: "Puntuación Auth",
        technique: "Técnica",
        zoomIn: "Acercar",
        zoomOut: "Alejar",
        rotate: "Rotar",
        reset: "Restablecer Vista"
      },
      pricing: {
        title: "Planes de Suscripción",
        subtitle: "Desde experiencias de una historia hasta acceso ilimitado con análisis forense IA—elige el plan que se adapte a tu pasión.",
        chooseExperience: "Elige Tu Experiencia",
        cardStripe: "Tarjeta (Stripe)",
        razorpayIndia: "Razorpay (India)",
        perStory: "/ historia",
        perYear: "/ año",
        mostPopular: "MÁS POPULAR",
        getStarted: "Comenzar",
        subscribeNow: "Suscribirse Ahora",
        tiers: {
          shortStory: {
            name: "La Historia Corta",
            feature1: "Una experiencia RV de 3 minutos",
            feature2: "Solo vista narrativa"
          },
          deepDive: {
            name: "Inmersión Profunda",
            feature1: "Vista Narrativa completa",
            feature2: "Vista Forense completa",
            feature3: "Una obra maestra"
          },
          connoisseur: {
            name: "Conocedor Anual",
            feature1: "Historias ilimitadas",
            feature2: "Nuevos descubrimientos mensuales",
            feature3: "Panel de Conocimiento",
            feature4: "Seguimiento de marcadores forenses"
          },
          proCollector: {
            name: "Coleccionista Pro",
            feature1: "Todas las funciones de Conocedor",
            feature2: "Solicitar Historias Forenses personalizadas",
            feature3: "Soporte prioritario",
            feature4: "Avances exclusivos"
          },
          advisory: {
            name: "Asesoría del Coleccionista",
            feature1: "Todas las funciones de Pro Collector",
            feature2: "Consulta mensual 1-a-1 por video",
            feature3: "Acceso anticipado a informes de autenticación",
            feature4: "Invitaciones VIP a eventos de galería",
            feature5: "Análisis personal del portafolio de arte",
            feature6: "Línea directa con curador",
            feature7: "12 sesiones de asesoría por año"
          }
        }
      },
      dashboard: {
        title: "Tu Panel",
        welcome: "Bienvenido de nuevo",
        myStories: "Mis Historias",
        knowledge: "Conocimiento",
        settings: "Configuración",
        noStories: "Aún no hay historias",
        startExploring: "Comienza a explorar la galería para desbloquear tu primera historia",
        exploreGallery: "Explorar Galería",
        forensicMarkers: "Marcadores Forenses Aprendidos",
        subscription: "Suscripción",
        upgradeNow: "Actualizar Ahora"
      },
      common: {
        loading: "Cargando...",
        error: "Algo salió mal",
        retry: "Intentar de Nuevo",
        save: "Guardar",
        cancel: "Cancelar",
        delete: "Eliminar",
        edit: "Editar",
        view: "Ver",
        close: "Cerrar",
        share: "Compartir",
        download: "Descargar",
        linkCopied: "Enlace copiado al portapapeles"
      },
      footer: {
        tagline: "Donde el Arte Encuentra la Inteligencia",
        quickLinks: "Enlaces Rápidos",
        legal: "Legal",
        privacy: "Política de Privacidad",
        terms: "Términos de Servicio",
        contact: "Contáctanos",
        copyright: "Todos los derechos reservados"
      }
    }
  },
  fr: {
    translation: {
      nav: {
        gallery: "Galerie",
        about: "À Propos",
        technology: "Technologie",
        events: "Événements",
        pricing: "Tarifs",
        dashboard: "Tableau de Bord",
        signIn: "Connexion",
        signOut: "Déconnexion"
      },
      landing: {
        hero: {
          title: "Vivez l'Art Comme Jamais Auparavant",
          subtitle: "Narration immersive en RV avec analyse forensique alimentée par l'IA",
          cta: "Explorer la Galerie",
          learnMore: "En Savoir Plus"
        },
        features: {
          narrative: {
            title: "Vue Narrative",
            description: "Voyage cinématographique à travers la provenance et l'histoire de l'art"
          },
          forensic: {
            title: "Vue Forensique",
            description: "Analyse par IA des pigments, signatures et toiles"
          },
          vr: {
            title: "Expérience RV",
            description: "Visualisation immersive sur Apple Vision Pro et Meta Quest"
          }
        },
        featured: "Œuvres en Vedette",
        viewAll: "Voir Toutes les Œuvres"
      },
      gallery: {
        title: "Galerie d'Art",
        subtitle: "Explorez les chefs-d'œuvre et leurs histoires",
        search: "Rechercher des œuvres ou artistes...",
        allPeriods: "Toutes les Périodes",
        backToHome: "Retour à l'Accueil",
        viewStory: "Voir l'Histoire",
        by: "par"
      },
      story: {
        backToGallery: "Retour à la Galerie",
        aboutArtwork: "À Propos de l'Œuvre",
        provenance: "Provenance",
        forensicFeatures: "Fonctionnalités d'Analyse Forensique",
        pigmentMapping: "Cartographie des Pigments",
        signatureAuth: "Authentification de Signature",
        canvasAnalysis: "Analyse de la Toile",
        accessGranted: "Accès Accordé",
        startExperience: "Commencer l'Expérience",
        shortStory: "L'Histoire Courte",
        deepDive: "Plongée Profonde",
        getAccess: "Obtenir l'Accès",
        recommended: "RECOMMANDÉ",
        unlimitedAccess: "Vous voulez un accès illimité?",
        viewPlans: "Voir les Plans d'Abonnement"
      },
      vr: {
        narrative: "Narrative",
        forensic: "Forensique",
        loading: "Préparation de votre expérience...",
        loadingArtwork: "Chargement de l'œuvre et du récit",
        notFound: "Expérience non trouvée",
        backToGallery: "Retour à la Galerie",
        timeline: "Chronologie de l'Histoire",
        scene: "Scène",
        runAnalysis: "Lancer l'Analyse IA",
        analyzing: "Analyse en cours...",
        generateViz: "Générer la Visualisation",
        generating: "Génération en cours...",
        analysisComplete: "Analyse terminée",
        pigment: "Pigment",
        signature: "Sign.",
        canvas: "Toile",
        authScore: "Score Auth",
        technique: "Technique",
        zoomIn: "Zoom Avant",
        zoomOut: "Zoom Arrière",
        rotate: "Pivoter",
        reset: "Réinitialiser la Vue"
      },
      pricing: {
        title: "Plans d'Abonnement",
        subtitle: "Des expériences d'une seule histoire à un accès illimité avec analyse forensique IA—choisissez le plan qui correspond à votre passion.",
        chooseExperience: "Choisissez Votre Expérience",
        cardStripe: "Carte (Stripe)",
        razorpayIndia: "Razorpay (Inde)",
        perStory: "/ histoire",
        perYear: "/ an",
        mostPopular: "LE PLUS POPULAIRE",
        getStarted: "Commencer",
        subscribeNow: "S'abonner Maintenant",
        tiers: {
          shortStory: {
            name: "L'Histoire Courte",
            feature1: "Une expérience RV de 3 minutes",
            feature2: "Vue narrative uniquement"
          },
          deepDive: {
            name: "Plongée Profonde",
            feature1: "Vue Narrative complète",
            feature2: "Vue Forensique complète",
            feature3: "Un chef-d'œuvre"
          },
          connoisseur: {
            name: "Connaisseur Annuel",
            feature1: "Histoires illimitées",
            feature2: "Nouvelles découvertes mensuelles",
            feature3: "Tableau de Bord des Connaissances",
            feature4: "Suivi des marqueurs forensiques"
          },
          proCollector: {
            name: "Collectionneur Pro",
            feature1: "Toutes les fonctionnalités Connaisseur",
            feature2: "Demander des Histoires Forensiques personnalisées",
            feature3: "Support prioritaire",
            feature4: "Aperçus exclusifs"
          },
          advisory: {
            name: "Conseil du Collectionneur",
            feature1: "Toutes les fonctionnalités Pro Collector",
            feature2: "Consultation vidéo mensuelle 1-à-1",
            feature3: "Accès anticipé aux rapports d'authentification",
            feature4: "Invitations VIP aux événements de galerie",
            feature5: "Analyse personnelle du portefeuille d'art",
            feature6: "Ligne directe avec le curateur",
            feature7: "12 sessions de conseil par an"
          }
        }
      },
      dashboard: {
        title: "Votre Tableau de Bord",
        welcome: "Bienvenue",
        myStories: "Mes Histoires",
        knowledge: "Connaissances",
        settings: "Paramètres",
        noStories: "Pas encore d'histoires",
        startExploring: "Commencez à explorer la galerie pour débloquer votre première histoire",
        exploreGallery: "Explorer la Galerie",
        forensicMarkers: "Marqueurs Forensiques Appris",
        subscription: "Abonnement",
        upgradeNow: "Mettre à Niveau"
      },
      common: {
        loading: "Chargement...",
        error: "Une erreur s'est produite",
        retry: "Réessayer",
        save: "Enregistrer",
        cancel: "Annuler",
        delete: "Supprimer",
        edit: "Modifier",
        view: "Voir",
        close: "Fermer",
        share: "Partager",
        download: "Télécharger",
        linkCopied: "Lien copié dans le presse-papiers"
      },
      footer: {
        tagline: "Où l'Art Rencontre l'Intelligence",
        quickLinks: "Liens Rapides",
        legal: "Mentions Légales",
        privacy: "Politique de Confidentialité",
        terms: "Conditions d'Utilisation",
        contact: "Nous Contacter",
        copyright: "Tous droits réservés"
      }
    }
  },
  zh: {
    translation: {
      nav: {
        gallery: "画廊",
        about: "关于我们",
        technology: "技术",
        events: "活动",
        pricing: "价格",
        dashboard: "仪表板",
        signIn: "登录",
        signOut: "退出"
      },
      landing: {
        hero: {
          title: "以前所未有的方式体验艺术",
          subtitle: "沉浸式VR叙事与AI驱动的鉴定分析",
          cta: "探索画廊",
          learnMore: "了解更多"
        },
        features: {
          narrative: {
            title: "叙事视图",
            description: "穿越艺术品来源和历史的电影之旅"
          },
          forensic: {
            title: "鉴定视图",
            description: "AI驱动的颜料、签名和画布分析"
          },
          vr: {
            title: "VR体验",
            description: "在Apple Vision Pro和Meta Quest上的沉浸式观看"
          }
        },
        featured: "精选作品",
        viewAll: "查看所有作品"
      },
      gallery: {
        title: "艺术画廊",
        subtitle: "探索杰作及其故事",
        search: "搜索作品或艺术家...",
        allPeriods: "所有时期",
        backToHome: "返回首页",
        viewStory: "查看故事",
        by: "作者"
      },
      story: {
        backToGallery: "返回画廊",
        aboutArtwork: "关于作品",
        provenance: "来源",
        forensicFeatures: "鉴定分析功能",
        pigmentMapping: "颜料分析",
        signatureAuth: "签名鉴定",
        canvasAnalysis: "画布分析",
        accessGranted: "已获得访问权限",
        startExperience: "开始体验",
        shortStory: "短篇故事",
        deepDive: "深度探索",
        getAccess: "获取访问权限",
        recommended: "推荐",
        unlimitedAccess: "想要无限访问？",
        viewPlans: "查看订阅计划"
      },
      vr: {
        narrative: "叙事",
        forensic: "鉴定",
        loading: "正在准备您的体验...",
        loadingArtwork: "加载作品和叙事",
        notFound: "未找到体验",
        backToGallery: "返回画廊",
        timeline: "故事时间线",
        scene: "场景",
        runAnalysis: "运行AI分析",
        analyzing: "分析中...",
        generateViz: "生成可视化",
        generating: "生成中...",
        analysisComplete: "分析完成",
        pigment: "颜料",
        signature: "签名",
        canvas: "画布",
        authScore: "鉴定分数",
        technique: "技法",
        zoomIn: "放大",
        zoomOut: "缩小",
        rotate: "旋转",
        reset: "重置视图"
      },
      pricing: {
        title: "订阅计划",
        subtitle: "从单个故事体验到AI鉴定的无限访问——选择适合您热情的计划。",
        chooseExperience: "选择您的体验",
        cardStripe: "银行卡 (Stripe)",
        razorpayIndia: "Razorpay (印度)",
        perStory: "/ 故事",
        perYear: "/ 年",
        mostPopular: "最受欢迎",
        getStarted: "开始",
        subscribeNow: "立即订阅",
        tiers: {
          shortStory: {
            name: "短篇故事",
            feature1: "一次3分钟VR体验",
            feature2: "仅叙事视图"
          },
          deepDive: {
            name: "深度探索",
            feature1: "完整叙事视图",
            feature2: "完整鉴定视图",
            feature3: "一件杰作"
          },
          connoisseur: {
            name: "年度鉴赏家",
            feature1: "无限故事",
            feature2: "每月新发现",
            feature3: "知识仪表板",
            feature4: "鉴定标记追踪"
          },
          proCollector: {
            name: "专业收藏家",
            feature1: "所有鉴赏家功能",
            feature2: "请求定制鉴定故事",
            feature3: "优先支持",
            feature4: "独家预览"
          },
          advisory: {
            name: "收藏家顾问",
            feature1: "所有专业收藏家功能",
            feature2: "每月1对1视频咨询",
            feature3: "提前获取鉴定报告",
            feature4: "VIP画廊活动邀请",
            feature5: "个人艺术组合分析",
            feature6: "策展人直线",
            feature7: "每年12次顾问会议"
          }
        }
      },
      dashboard: {
        title: "您的仪表板",
        welcome: "欢迎回来",
        myStories: "我的故事",
        knowledge: "知识",
        settings: "设置",
        noStories: "还没有故事",
        startExploring: "开始探索画廊以解锁您的第一个故事",
        exploreGallery: "探索画廊",
        forensicMarkers: "已学习的鉴定标记",
        subscription: "订阅",
        upgradeNow: "立即升级"
      },
      common: {
        loading: "加载中...",
        error: "出错了",
        retry: "重试",
        save: "保存",
        cancel: "取消",
        delete: "删除",
        edit: "编辑",
        view: "查看",
        close: "关闭",
        share: "分享",
        download: "下载",
        linkCopied: "链接已复制到剪贴板"
      },
      footer: {
        tagline: "艺术与智能的交汇",
        quickLinks: "快速链接",
        legal: "法律",
        privacy: "隐私政策",
        terms: "服务条款",
        contact: "联系我们",
        copyright: "版权所有"
      }
    }
  },
  ar: {
    translation: {
      nav: {
        gallery: "المعرض",
        about: "من نحن",
        technology: "التكنولوجيا",
        events: "الفعاليات",
        pricing: "الأسعار",
        dashboard: "لوحة التحكم",
        signIn: "تسجيل الدخول",
        signOut: "تسجيل الخروج"
      },
      landing: {
        hero: {
          title: "اختبر الفن كما لم تختبره من قبل",
          subtitle: "سرد قصصي غامر بالواقع الافتراضي مع تحليل جنائي مدعوم بالذكاء الاصطناعي",
          cta: "استكشف المعرض",
          learnMore: "اعرف المزيد"
        },
        features: {
          narrative: {
            title: "العرض السردي",
            description: "رحلة سينمائية عبر مصدر وتاريخ الفن"
          },
          forensic: {
            title: "العرض الجنائي",
            description: "تحليل بالذكاء الاصطناعي للأصباغ والتوقيعات والقماش"
          },
          vr: {
            title: "تجربة الواقع الافتراضي",
            description: "مشاهدة غامرة على Apple Vision Pro و Meta Quest"
          }
        },
        featured: "أعمال مميزة",
        viewAll: "عرض جميع الأعمال"
      },
      gallery: {
        title: "معرض الفن",
        subtitle: "استكشف الروائع وقصصها",
        search: "البحث عن أعمال أو فنانين...",
        allPeriods: "جميع الفترات",
        backToHome: "العودة للرئيسية",
        viewStory: "عرض القصة",
        by: "بواسطة"
      },
      story: {
        backToGallery: "العودة للمعرض",
        aboutArtwork: "عن العمل الفني",
        provenance: "المصدر",
        forensicFeatures: "ميزات التحليل الجنائي",
        pigmentMapping: "تحليل الأصباغ",
        signatureAuth: "توثيق التوقيع",
        canvasAnalysis: "تحليل القماش",
        accessGranted: "تم منح الوصول",
        startExperience: "ابدأ التجربة",
        shortStory: "القصة القصيرة",
        deepDive: "الغوص العميق",
        getAccess: "احصل على الوصول",
        recommended: "موصى به",
        unlimitedAccess: "هل تريد وصولاً غير محدود؟",
        viewPlans: "عرض خطط الاشتراك"
      },
      vr: {
        narrative: "سردي",
        forensic: "جنائي",
        loading: "جاري تحضير تجربتك...",
        loadingArtwork: "جاري تحميل العمل والسرد",
        notFound: "التجربة غير موجودة",
        backToGallery: "العودة للمعرض",
        timeline: "الجدول الزمني للقصة",
        scene: "مشهد",
        runAnalysis: "تشغيل تحليل الذكاء الاصطناعي",
        analyzing: "جاري التحليل...",
        generateViz: "إنشاء التصور",
        generating: "جاري الإنشاء...",
        analysisComplete: "اكتمل التحليل",
        pigment: "صبغة",
        signature: "توقيع",
        canvas: "قماش",
        authScore: "درجة التوثيق",
        technique: "تقنية",
        zoomIn: "تكبير",
        zoomOut: "تصغير",
        rotate: "تدوير",
        reset: "إعادة تعيين العرض"
      },
      pricing: {
        title: "خطط الاشتراك",
        subtitle: "من تجارب القصة الواحدة إلى الوصول غير المحدود مع التحليل الجنائي بالذكاء الاصطناعي - اختر الخطة التي تناسب شغفك.",
        chooseExperience: "اختر تجربتك",
        cardStripe: "بطاقة (Stripe)",
        razorpayIndia: "Razorpay (الهند)",
        perStory: "/ قصة",
        perYear: "/ سنة",
        mostPopular: "الأكثر شعبية",
        getStarted: "ابدأ",
        subscribeNow: "اشترك الآن",
        tiers: {
          shortStory: {
            name: "القصة القصيرة",
            feature1: "تجربة واقع افتراضي لمدة 3 دقائق",
            feature2: "العرض السردي فقط"
          },
          deepDive: {
            name: "الغوص العميق",
            feature1: "عرض سردي كامل",
            feature2: "عرض جنائي كامل",
            feature3: "تحفة فنية واحدة"
          },
          connoisseur: {
            name: "الخبير السنوي",
            feature1: "قصص غير محدودة",
            feature2: "اكتشافات جديدة شهرية",
            feature3: "لوحة المعرفة",
            feature4: "تتبع العلامات الجنائية"
          },
          proCollector: {
            name: "جامع محترف",
            feature1: "جميع ميزات الخبير",
            feature2: "طلب قصص جنائية مخصصة",
            feature3: "دعم ذو أولوية",
            feature4: "معاينات حصرية"
          },
          advisory: {
            name: "استشارة الجامع",
            feature1: "جميع ميزات الجامع المحترف",
            feature2: "استشارة فيديو شهرية 1-على-1",
            feature3: "وصول مبكر لتقارير التوثيق",
            feature4: "دعوات VIP لفعاليات المعرض",
            feature5: "تحليل شخصي لمحفظة الفن",
            feature6: "خط مباشر مع القيم الفني",
            feature7: "12 جلسة استشارية سنوياً"
          }
        }
      },
      dashboard: {
        title: "لوحة التحكم الخاصة بك",
        welcome: "مرحباً بعودتك",
        myStories: "قصصي",
        knowledge: "المعرفة",
        settings: "الإعدادات",
        noStories: "لا توجد قصص بعد",
        startExploring: "ابدأ استكشاف المعرض لفتح أول قصة لك",
        exploreGallery: "استكشف المعرض",
        forensicMarkers: "العلامات الجنائية المكتسبة",
        subscription: "الاشتراك",
        upgradeNow: "الترقية الآن"
      },
      common: {
        loading: "جاري التحميل...",
        error: "حدث خطأ ما",
        retry: "حاول مرة أخرى",
        save: "حفظ",
        cancel: "إلغاء",
        delete: "حذف",
        edit: "تعديل",
        view: "عرض",
        close: "إغلاق",
        share: "مشاركة",
        download: "تحميل",
        linkCopied: "تم نسخ الرابط إلى الحافظة"
      },
      footer: {
        tagline: "حيث يلتقي الفن بالذكاء",
        quickLinks: "روابط سريعة",
        legal: "قانوني",
        privacy: "سياسة الخصوصية",
        terms: "شروط الخدمة",
        contact: "اتصل بنا",
        copyright: "جميع الحقوق محفوظة"
      }
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    },
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage']
    }
  });

export default i18n;
