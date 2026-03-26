# Emaira.Art - VR Storyteller + AI Art Forensics

## Original Problem Statement
Build "Emaira.Art: The VR Storyteller plus AI Art Forensics" - a high-end VR Storytelling portal for Art Galleries globally with the "Emaira AI Forensics Agent".

## User Personas
1. **Art Collectors**: High-net-worth individuals seeking authentication tools
2. **Art Enthusiasts**: Passionate learners wanting deeper art knowledge
3. **Museums/Galleries**: Institutions needing educational content
4. **Authentication Professionals**: Experts using AI-assisted verification

## Core Requirements
- VR Art Story Experience with Narrative & Forensic views
- AI Forensics Analysis (Gemini 3 Flash)
- AI Visualization Generation (Gemini Nano Banana)
- 5 Subscription tiers: Short Story ($9.99), Deep Dive ($49), Connoisseur ($249/yr), Pro Collector ($999/yr), Collector's Advisory ($2499/yr)
- Dual payment: Stripe + Razorpay
- Google OAuth authentication
- Multi-language support (EN, ES, FR, ZH, AR)

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI + i18next
- **Backend**: FastAPI + MongoDB
- **AI**: Gemini 3 Flash (text), Gemini Nano Banana (images)
- **Payments**: Stripe + Razorpay
- **Auth**: Emergent Google OAuth
- **Email**: Resend

---

## COMPLETED FEATURES

### Feb 17, 2026 - Full Development Complete ✅

#### P0 - Business Core (100% Complete)
- [x] **50 Masterpiece Artworks** with galleries (Louvre, MoMA, Tate, Prado, Met, etc.)
- [x] **Admin Roles System** (Super Admin, Content Curator, Marketing Admin, Support Admin)
- [x] **Organizations Management** (Museums, Galleries, Collectors, Auction Houses)
- [x] **Email Marketing (Resend)** - Campaigns, templates, segmented sending
- [x] **The Met Museum API Integration** - Search & import 470K+ artworks
- [x] **Collector's Advisory Tier** ($2499/year) - 12 advisory sessions
- [x] **Subscriptions API** - 5 tiers with feature comparison
- [x] **Superadmin Account** - rohankaji@gmail.com

#### P1 - VR & AI Experience (100% Complete)
- [x] **Enhanced VR Experience** - Mobile-optimized with zoom, pan, rotate
- [x] **VR Headset Detection** - WebXR support for Vision Pro/Quest
- [x] **Auto-play Narrative** - Progress tracking with scene transitions
- [x] **AI Visualization Overlays** - Gemini Nano Banana for forensic visualizations
- [x] **VR Narrative Generation** - AI-generated immersive stories
- [x] **Deep Forensic Analysis** - Comprehensive authentication reports

#### P2 - User Engagement (100% Complete)
- [x] **Multi-language Support** - English, Spanish, French, Chinese, Arabic (RTL)
- [x] **Reviews & Ratings System** - 5-star ratings, helpful votes, verified purchases
- [x] **Social Sharing** - Twitter, Facebook, LinkedIn with OG metadata
- [x] **User Notifications** - Welcome messages, purchase confirmations
- [x] **Language Selector** - Globe icon with country flags

---

## 50 ARTWORKS COLLECTION

### Classic Masterpieces (38)
| Artwork | Artist | Location |
|---------|--------|----------|
| Mona Lisa | Leonardo da Vinci | Louvre Museum, Paris |
| The Starry Night | Vincent van Gogh | MoMA, New York |
| Girl with a Pearl Earring | Johannes Vermeer | Mauritshuis, The Hague |
| The Persistence of Memory | Salvador Dalí | MoMA, New York |
| The Birth of Venus | Sandro Botticelli | Uffizi Gallery, Florence |
| The Last Supper | Leonardo da Vinci | Santa Maria delle Grazie |
| Guernica | Pablo Picasso | Reina Sofía, Madrid |
| The Scream | Edvard Munch | National Gallery, Oslo |
| Water Lilies | Claude Monet | Musée de l'Orangerie, Paris |
| The Night Watch | Rembrandt | Rijksmuseum, Amsterdam |
| American Gothic | Grant Wood | Art Institute of Chicago |
| The Kiss | Gustav Klimt | Belvedere, Vienna |
| Las Meninas | Diego Velázquez | Museo del Prado, Madrid |
| The Great Wave | Hokusai | Multiple museums |
| A Sunday on La Grande Jatte | Georges Seurat | Art Institute of Chicago |
| The Creation of Adam | Michelangelo | Sistine Chapel, Vatican |
| Impression, Sunrise | Claude Monet | Musée Marmottan |
| Café Terrace at Night | Vincent van Gogh | Kröller-Müller Museum |
| The Arnolfini Portrait | Jan van Eyck | National Gallery, London |
| Nighthawks | Edward Hopper | Art Institute of Chicago |
| Girl with Balloon | Banksy | Various/Destroyed |
| The Physical Impossibility of Death | Damien Hirst | Various Collections |
| Wanderer above the Sea of Fog | C.D. Friedrich | Hamburger Kunsthalle |
| Olympia | Édouard Manet | Musée d'Orsay, Paris |
| Liberty Leading the People | Delacroix | Louvre Museum, Paris |
| The Milkmaid | Johannes Vermeer | Rijksmuseum, Amsterdam |
| The School of Athens | Raphael | Vatican Museums |
| The Garden of Earthly Delights | Hieronymus Bosch | Museo del Prado |
| Whistler's Mother | J.M. Whistler | Musée d'Orsay, Paris |
| David (sculpture) | Michelangelo | Galleria dell'Accademia |
| Venus de Milo | Alexandros of Antioch | Louvre Museum, Paris |

### Modern & Contemporary Art (12)
| Artwork | Artist | Movement |
|---------|--------|----------|
| Shot Sage Blue Marilyn | Andy Warhol | Pop Art |
| Untitled (Skull) | Jean-Michel Basquiat | Neo-Expressionism |
| A Bigger Splash | David Hockney | British Pop Art |
| Infinity Mirrored Room | Yayoi Kusama | Contemporary |
| COMPANION | KAWS | Street Art |
| Sunflower Seeds | Ai Weiwei | Conceptual Art |
| Abstraktes Bild | Gerhard Richter | Abstract Art |
| Three Studies of Lucian Freud | Francis Bacon | Figurative Expressionism |
| Maman (Spider) | Louise Bourgeois | Contemporary Sculpture |
| Cloud Gate (The Bean) | Anish Kapoor | Public Art |
| The Son of Man | René Magritte | Surrealism |
| The Thinker | Auguste Rodin | Modern Sculpture |

---

## API ENDPOINTS

### Core APIs
- `GET /api/artworks/` - List 50 artworks with filters
- `GET /api/stories/{story_id}` - Get story with narrative content
- `GET /api/subscriptions/` - List 5 subscription tiers
- `POST /api/vr/generate-narrative/{artwork_id}` - AI narrative generation
- `GET /api/vr/narrative/{artwork_id}` - Get existing narrative

### Reviews & Ratings
- `GET /api/reviews/story/{story_id}` - Get reviews with average rating
- `GET /api/reviews/artwork/{artwork_id}` - Get artwork reviews
- `POST /api/reviews/` - Create review (auth required)
- `POST /api/reviews/{id}/helpful` - Mark helpful (auth required)

### Social Sharing
- `POST /api/share/artwork/{artwork_id}` - Create share link with OG metadata
- `POST /api/share/story/{story_id}` - Create share link
- `GET /api/share/track/{share_id}` - Track share views

### Notifications
- `GET /api/notifications/` - Get user notifications
- `POST /api/notifications/{id}/read` - Mark as read
- `POST /api/notifications/read-all` - Mark all read

### Admin & Organizations
- `GET /api/admin/roles` - Get role definitions
- `POST /api/admin/assign-role/{user_id}` - Assign role (super_admin)
- `GET /api/organizations/` - List organizations (super_admin)
- `POST /api/organizations/` - Create organization
- `POST /api/organizations/{id}/members` - Add member

---

## CREDENTIALS

### Superadmin Account
| Field | Value |
|-------|-------|
| Email | rohankaji@gmail.com |
| Role | super_admin |
| Login | Google OAuth |
| Access | Full platform access |

### Admin Roles
| Role | Permissions |
|------|-------------|
| Super Admin | Full access - users, admins, content, payments, settings |
| Content Curator | Artworks, stories, museums, analytics |
| Marketing Admin | Campaigns, analytics, user data |
| Support Admin | User management, analytics |

---

## SUPPORTED LANGUAGES
| Code | Language | RTL |
|------|----------|-----|
| en | English | No |
| es | Español | No |
| fr | Français | No |
| zh | 中文 | No |
| ar | العربية | Yes |

---

## FUTURE ENHANCEMENTS
- [ ] Native VR SDK (Apple Vision Pro, Meta Quest)
- [ ] Offline VR mode
- [ ] User artwork comparison tool
- [ ] Advanced analytics dashboard
- [ ] Push notifications (mobile)

---

## TECHNICAL NOTES
- Gemini API Key: `backend/.env` as GEMINI_API_KEY
- Emergent LLM Key: `backend/.env` as EMERGENT_LLM_KEY
- Stripe Test Key: Pre-configured in environment
- Resend: Requires `RESEND_API_KEY` for actual email sending
- Met Museum API: Free public API (may rate limit)
