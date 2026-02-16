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
- Subscription tiers: Short Story ($9.99), Deep Dive ($49), Connoisseur ($249/yr), Pro Collector ($999/yr)
- Dual payment: Stripe + Razorpay
- Google OAuth authentication (Emergent-managed)
- Dark luxury "Vogue" aesthetic

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI + MongoDB
- **AI**: Gemini 3 Flash (text analysis), Gemini Nano Banana (image generation)
- **Payments**: Stripe (international), Razorpay (India)
- **Auth**: Emergent Google OAuth

## What's Been Implemented (Feb 16, 2026)
### Backend
- [x] User authentication (Google OAuth via Emergent)
- [x] Artworks CRUD endpoints - **20 world masterpieces seeded**
- [x] Stories CRUD endpoints - **Full narrative and forensic content**
- [x] AI Forensics analysis endpoint (Gemini integration)
- [x] AI Visualization generation endpoint
- [x] Stripe payment integration with checkout
- [x] Razorpay payment integration
- [x] Subscription tiers management
- [x] User dashboard data endpoints
- [x] Knowledge tracking for forensic markers
- [x] **NEW** CRM System:
  - User management (CRUD, search, filter, pagination)
  - User activity tracking (login, purchases, views, analysis)
  - Analytics dashboard (revenue, users, subscriptions)
  - User segments (high_value, subscribers, free_users, etc.)
  - CRM notes system
  - User detail profiles with stats

### Frontend
- [x] Landing page with hero, features, featured artworks
- [x] Gallery page with search/filter - **20 artworks displayed**
- [x] Story detail page with purchase options
- [x] Pricing page with tier comparison
- [x] VR Experience viewer with Narrative/Forensic toggle
- [x] User dashboard with stories & knowledge tracking
- [x] Payment success/failure handling
- [x] Google OAuth callback handling
- [x] About Us page with team, mission, and values sections
- [x] Our Technology page with AI forensics features deep-dive
- [x] Events page with calendar, upcoming events, and past recordings
- [x] **NEW** CRM Dashboard (/crm) with:
  - Overview tab (stats, segments, subscription breakdown)
  - Users tab (paginated list, search, filters, detail modal)
  - Activity tab (real-time activity feed)
- [x] Light Luxury Vogue theme (Bodoni Moda, Manrope, Space Mono fonts)
- [x] Ivory (#FAFAF8), Gold (#B8962F) and Navy (#1A365D) color palette

### Artworks Collection (20 Masterpieces)
1. Mona Lisa - Leonardo da Vinci
2. The Starry Night - Vincent van Gogh
3. Girl with a Pearl Earring - Johannes Vermeer
4. The Persistence of Memory - Salvador Dalí
5. The Birth of Venus - Sandro Botticelli
6. The Last Supper - Leonardo da Vinci
7. Guernica - Pablo Picasso
8. The Scream - Edvard Munch
9. Water Lilies - Claude Monet
10. The Night Watch - Rembrandt van Rijn
11. American Gothic - Grant Wood
12. The Kiss - Gustav Klimt
13. Las Meninas - Diego Velázquez
14. The Great Wave off Kanagawa - Katsushika Hokusai
15. A Sunday on La Grande Jatte - Georges Seurat
16. The Creation of Adam - Michelangelo
17. Impression, Sunrise - Claude Monet
18. Café Terrace at Night - Vincent van Gogh
19. The Arnolfini Portrait - Jan van Eyck
20. Nighthawks - Edward Hopper

Each artwork includes:
- Full provenance history
- Forensic DNA (pigments, signature markers, canvas analysis, technique)
- 5-scene narrative storyline
- Authentication score

## Prioritized Backlog

### P0 (Critical for MVP)
- [x] Core viewing experience
- [x] Payment processing
- [x] User authentication
- [x] AI forensics integration

### P1 (Important)
- [ ] VR headset integration (Apple Vision Pro, Meta Quest)
- [ ] Real artwork image database integration
- [ ] Enhanced AI visualization overlays
- [ ] Email notifications for purchases

### P2 (Nice to Have)
- [ ] Social sharing features
- [ ] User reviews/ratings
- [ ] Artwork comparison tool
- [ ] Mobile-optimized VR experience

## Next Tasks
1. Add more artwork content and stories
2. Implement VR headset SDK integration
3. Enhanced AI forensic visualization overlays
4. Add user notification system
5. Implement analytics dashboard for admins
