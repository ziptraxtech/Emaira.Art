# Emaira.Art - VR Storyteller + AI Art Forensics

## Original Problem Statement
Build "Emaira.Art: The VR Storyteller plus AI Art Forensics" - a high-end VR Storytelling portal for Art Galleries globally with the "Emaira AI Forensics Agent". The platform integrates:
- **Narrative View**: Cinematic journey through art provenance ($4.99-$9.99/story)
- **Forensic View**: AI-powered analysis - pigment mapping, signature authentication, canvas weave analysis

## User Personas
1. **Art Collectors**: High-net-worth individuals seeking authentication tools
2. **Art Enthusiasts**: Passionate learners wanting deeper art knowledge
3. **Museums/Galleries**: Institutions needing educational content
4. **Authentication Professionals**: Experts using AI-assisted verification

## Core Requirements (Static)
- VR Art Story Experience with Narrative & Forensic views
- AI Forensics Analysis (Gemini 3 Flash)
- AI Visualization Generation (Gemini Nano Banana)
- Subscription tiers: Short Story ($9.99), Deep Dive ($49), Connoisseur ($249/yr), Pro Collector ($999/yr), Collector's Advisory ($2499/yr)
- Dual payment: Stripe + Razorpay
- Google OAuth authentication (Emergent-managed)
- Light luxury "Vogue" aesthetic

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI + MongoDB
- **AI**: Gemini 3 Flash (text analysis), Gemini Nano Banana (image generation)
- **Payments**: Stripe (international), Razorpay (India)
- **Auth**: Emergent Google OAuth
- **Email**: Resend (for campaigns)
- **Museum API**: The Met Museum Open Access API

## What's Been Implemented

### Feb 17, 2026 - P0 Business Upgrades + P1 VR Enhancements
- [x] **Admin Roles System** (Super Admin, Content Curator, Marketing Admin, Support Admin)
- [x] **Email Marketing with Resend** - Campaign creation, templates, send functionality
- [x] **Direct Artwork Image Uploads** - Admin can upload artworks with base64 images
- [x] **The Met Museum API Integration** - Search, view, and import artworks
- [x] **Collector's Advisory Tier** ($2499/year) - Premium tier with advisory sessions
- [x] **Modern Art Categories** - Added 10 contemporary/modern artworks (total 38)
- [x] **Subscriptions API** - Public endpoint to list all subscription tiers
- [x] **VR Narrative Generation** - AI-generated immersive narratives for artworks
- [x] **Enhanced Forensics** - Deep analysis reports, forensic reports endpoint
- [x] **Enhanced VR Experience** - Mobile-optimized with zoom, pan, rotate, fullscreen
- [x] **Auto-play Narrative** - Progress tracking with scene auto-advance
- [x] **VR Headset Detection** - WebXR support check for VR devices
- [x] **Share Functionality** - Native share or clipboard copy

### Feb 16, 2026 - Initial Build
- [x] User authentication (Google OAuth via Emergent)
- [x] Artworks CRUD endpoints - **38 masterpieces seeded**
- [x] Stories CRUD endpoints - **Full narrative and forensic content**
- [x] AI Forensics analysis endpoint (Gemini integration)
- [x] AI Visualization generation endpoint
- [x] Stripe payment integration with checkout
- [x] Razorpay payment integration
- [x] Subscription tiers management
- [x] User dashboard data endpoints
- [x] Knowledge tracking for forensic markers
- [x] CRM System with analytics, user management, activity tracking
- [x] Landing, Gallery, Pricing, Story Detail, Dashboard pages
- [x] VR Experience viewer with Narrative/Forensic toggle
- [x] About Us, Our Technology, Events pages
- [x] Light Luxury Vogue theme

### Artworks Collection (38 Masterpieces)

**Classic Masterpieces (28):**
Mona Lisa, The Starry Night, Girl with a Pearl Earring, The Persistence of Memory, The Birth of Venus, The Last Supper, Guernica, The Scream, Water Lilies, The Night Watch, American Gothic, The Kiss, Las Meninas, The Great Wave, A Sunday on La Grande Jatte, The Creation of Adam, Impression Sunrise, Café Terrace at Night, The Arnolfini Portrait, Nighthawks, Girl with Balloon, The Physical Impossibility of Death...

**Modern & Contemporary Art (10):**
1. Shot Sage Blue Marilyn - Andy Warhol (Pop Art)
2. Untitled (Skull) - Jean-Michel Basquiat (Neo-Expressionism)
3. A Bigger Splash - David Hockney (British Pop Art)
4. Infinity Mirrored Room - Yayoi Kusama (Contemporary)
5. COMPANION - KAWS (Street Art/Pop Surrealism)
6. Sunflower Seeds - Ai Weiwei (Conceptual Art)
7. Abstraktes Bild - Gerhard Richter (Abstract Art)
8. Three Studies of Lucian Freud - Francis Bacon (Figurative Expressionism)
9. Maman - Louise Bourgeois (Contemporary Sculpture)
10. Cloud Gate - Anish Kapoor (Public Art)

## Admin Roles & Permissions
| Role | Permissions |
|------|-------------|
| Super Admin | Full access - manage users, admins, artworks, stories, campaigns, museums, payments, settings |
| Content Curator | Manage artworks, stories, museums; view analytics |
| Marketing Admin | Manage campaigns, view analytics, manage users |
| Support Admin | Manage users, view analytics |

## API Endpoints

### Subscriptions
- `GET /api/subscriptions/` - List all subscription tiers
- `GET /api/subscriptions/{tier_id}` - Get tier details
- `GET /api/subscriptions/user/current` - Get user's current subscription
- `POST /api/subscriptions/compare` - Compare tier features

### VR Narratives
- `POST /api/vr/generate-narrative/{artwork_id}` - Generate AI narrative
- `GET /api/vr/narrative/{artwork_id}` - Get existing narrative

### Enhanced Forensics
- `GET /api/forensics/report/{artwork_id}` - Get forensic report
- `POST /api/forensics/deep-analysis` - Run deep AI analysis (Pro/Advisory only)

### Museum Integration
- `GET /api/museums/met/search?q={query}` - Search The Met Museum
- `GET /api/museums/met/departments` - Get Met departments
- `POST /api/museums/met/import/{object_id}` - Import artwork from Met

### Email Campaigns
- `GET /api/campaigns/` - List campaigns
- `POST /api/campaigns/` - Create campaign
- `POST /api/campaigns/{id}/send` - Send campaign
- `GET /api/campaigns/templates` - Get email templates

### Admin Roles
- `GET /api/admin/roles` - Get role definitions
- `POST /api/admin/assign-role/{user_id}` - Assign role
- `GET /api/admin/users/admins` - List all admins

## Prioritized Backlog

### P0 (Critical) - COMPLETED ✅
- [x] Core viewing experience
- [x] Payment processing  
- [x] User authentication
- [x] AI forensics integration
- [x] Admin roles system
- [x] Email marketing
- [x] Museum API integration
- [x] Modern art categories
- [x] Collector's Advisory tier

### P1 (Important) - IN PROGRESS
- [x] Enhanced VR Experience with mobile optimization (zoom, pan, rotate, fullscreen)
- [x] VR headset detection (WebXR support check)
- [x] Auto-play narrative with progress tracking
- [x] Responsive mobile layout for VR experience
- [ ] VR headset SDK integration (Apple Vision Pro, Meta Quest) - Requires native SDK
- [ ] Real artwork image database integration
- [ ] Enhanced AI visualization overlays with actual image processing

### P2 (Nice to Have)
- [ ] Social sharing features
- [ ] User reviews/ratings
- [ ] Artwork comparison tool
- [ ] Multi-language support
- [ ] Offline mode for VR experiences

## Next Tasks
1. VR Headset SDK Integration (Apple Vision Pro, Meta Quest)
2. Enhanced AI Visualization with real-time image overlays
3. Mobile VR optimization
4. User notification system (purchase confirmations, subscription reminders)
5. Analytics dashboard improvements

## Technical Notes
- Gemini API Key: Stored in backend/.env as GEMINI_API_KEY
- Met Museum API: Free, public API (may occasionally return 403 due to rate limiting)
- Resend Email: Requires RESEND_API_KEY in backend/.env to send actual emails
- All admin features require authentication with appropriate role
