from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import httpx
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Emaira.Art API")

# Create routers
api_router = APIRouter(prefix="/api")
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
artworks_router = APIRouter(prefix="/artworks", tags=["Artworks"])
stories_router = APIRouter(prefix="/stories", tags=["Stories"])
forensics_router = APIRouter(prefix="/forensics", tags=["AI Forensics"])
payments_router = APIRouter(prefix="/payments", tags=["Payments"])
subscriptions_router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])
dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===================== MODELS =====================

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    subscription_tier: Optional[str] = None
    subscription_expires: Optional[datetime] = None
    purchased_stories: List[str] = []
    forensic_markers_learned: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    session_id: str
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Artwork(BaseModel):
    model_config = ConfigDict(extra="ignore")
    artwork_id: str = Field(default_factory=lambda: f"art_{uuid.uuid4().hex[:12]}")
    title: str
    artist: str
    year: str
    period: str
    medium: str
    dimensions: str
    location: str
    image_url: str
    thumbnail_url: str
    description: str
    provenance: List[Dict[str, str]] = []
    forensic_data: Optional[Dict[str, Any]] = None
    story_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Story(BaseModel):
    model_config = ConfigDict(extra="ignore")
    story_id: str = Field(default_factory=lambda: f"story_{uuid.uuid4().hex[:12]}")
    artwork_id: str
    title: str
    description: str
    duration_minutes: int = 3
    narrative_content: List[Dict[str, Any]] = []
    forensic_content: Optional[Dict[str, Any]] = None
    price_narrative: float = 9.99
    price_full: float = 49.00
    is_featured: bool = False
    preview_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PaymentTransaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    transaction_id: str = Field(default_factory=lambda: f"txn_{uuid.uuid4().hex[:12]}")
    user_id: Optional[str] = None
    email: Optional[str] = None
    session_id: str
    payment_provider: str  # stripe or razorpay
    amount: float
    currency: str = "usd"
    metadata: Dict[str, str] = {}
    payment_status: str = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

class ForensicAnalysisRequest(BaseModel):
    artwork_id: str
    analysis_type: str  # pigment, signature, canvas, full

class ForensicAnalysisResponse(BaseModel):
    analysis_id: str
    artwork_id: str
    analysis_type: str
    results: Dict[str, Any]
    generated_image_url: Optional[str] = None

class SubscriptionTier(BaseModel):
    tier_id: str
    name: str
    price: float
    currency: str = "usd"
    period: str  # story, year
    features: List[str]

# Subscription tiers configuration
SUBSCRIPTION_TIERS = {
    "short_story": SubscriptionTier(
        tier_id="short_story",
        name="The Short Story",
        price=9.99,
        period="story",
        features=["One 3-minute VR experience", "Narrative view only"]
    ),
    "deep_dive": SubscriptionTier(
        tier_id="deep_dive",
        name="The Deep Dive",
        price=49.00,
        period="story",
        features=["Full Narrative view", "Complete Forensic View", "One masterpiece"]
    ),
    "connoisseur": SubscriptionTier(
        tier_id="connoisseur",
        name="Annual Connoisseur",
        price=249.00,
        period="year",
        features=["Unlimited stories", "Monthly New Discovery drops", "Knowledge Dashboard", "Forensic markers tracking"]
    ),
    "pro_collector": SubscriptionTier(
        tier_id="pro_collector",
        name="Pro Collector",
        price=999.00,
        period="year",
        features=["All Connoisseur features", "Request custom Forensic Stories", "Priority support", "Exclusive previews"]
    )
}

# ===================== AUTH HELPER =====================

async def get_current_user(request: Request) -> Optional[User]:
    """Get current user from session token in cookie or Authorization header"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    
    if not session_token:
        return None
    
    session_doc = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session_doc:
        return None
    
    expires_at = session_doc.get("expires_at")
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        return None
    
    user_doc = await db.users.find_one({"user_id": session_doc["user_id"]}, {"_id": 0})
    if not user_doc:
        return None
    
    return User(**user_doc)

async def require_auth(request: Request) -> User:
    """Require authentication for protected routes"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

# ===================== AUTH ROUTES =====================

@auth_router.post("/session")
async def create_session(request: Request, response: Response):
    """Exchange session_id for session_token after Google OAuth"""
    body = await request.json()
    session_id = body.get("session_id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")
    
    # Call Emergent Auth to get user data
    async with httpx.AsyncClient() as client_http:
        try:
            auth_response = await client_http.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id}
            )
            if auth_response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid session")
            
            user_data = auth_response.json()
        except Exception as e:
            logger.error(f"Auth error: {e}")
            raise HTTPException(status_code=401, detail="Authentication failed")
    
    email = user_data.get("email")
    name = user_data.get("name")
    picture = user_data.get("picture")
    session_token = user_data.get("session_token")
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": email}, {"_id": 0})
    
    if existing_user:
        user_id = existing_user["user_id"]
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"name": name, "picture": picture}}
        )
    else:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        new_user = User(
            user_id=user_id,
            email=email,
            name=name,
            picture=picture
        )
        user_doc = new_user.model_dump()
        user_doc["created_at"] = user_doc["created_at"].isoformat()
        await db.users.insert_one(user_doc)
    
    # Store session
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    session_doc = {
        "session_id": str(uuid.uuid4()),
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.user_sessions.insert_one(session_doc)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 60 * 60
    )
    
    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    return {"user": user_doc, "session_token": session_token}

@auth_router.get("/me")
async def get_current_user_route(request: Request):
    """Get current authenticated user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user.model_dump()

@auth_router.post("/logout")
async def logout(request: Request, response: Response):
    """Logout user and clear session"""
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_many({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/", secure=True, samesite="none")
    return {"message": "Logged out successfully"}

# ===================== ARTWORKS ROUTES =====================

@artworks_router.get("/", response_model=List[Dict[str, Any]])
async def get_artworks(featured: bool = False, limit: int = 20):
    """Get all artworks or featured artworks"""
    query = {"is_featured": True} if featured else {}
    artworks = await db.artworks.find(query, {"_id": 0}).limit(limit).to_list(limit)
    return artworks

@artworks_router.get("/{artwork_id}")
async def get_artwork(artwork_id: str):
    """Get single artwork by ID"""
    artwork = await db.artworks.find_one({"artwork_id": artwork_id}, {"_id": 0})
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    return artwork

@artworks_router.post("/", response_model=Dict[str, Any])
async def create_artwork(artwork: Artwork):
    """Create a new artwork (admin only in production)"""
    artwork_dict = artwork.model_dump()
    artwork_dict["created_at"] = artwork_dict["created_at"].isoformat()
    await db.artworks.insert_one(artwork_dict)
    return {"artwork_id": artwork.artwork_id, "message": "Artwork created successfully"}

# ===================== STORIES ROUTES =====================

@stories_router.get("/", response_model=List[Dict[str, Any]])
async def get_stories(featured: bool = False, limit: int = 20):
    """Get all stories or featured stories"""
    query = {"is_featured": True} if featured else {}
    stories = await db.stories.find(query, {"_id": 0}).limit(limit).to_list(limit)
    return stories

@stories_router.get("/{story_id}")
async def get_story(story_id: str, request: Request):
    """Get single story - full content only for purchased users"""
    story = await db.stories.find_one({"story_id": story_id}, {"_id": 0})
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    user = await get_current_user(request)
    has_access = False
    
    if user:
        # Check if user has subscription or purchased this story
        if user.subscription_tier in ["connoisseur", "pro_collector"]:
            has_access = True
        elif story_id in user.purchased_stories:
            has_access = True
    
    if not has_access:
        # Return preview only
        return {
            "story_id": story["story_id"],
            "artwork_id": story["artwork_id"],
            "title": story["title"],
            "description": story["description"],
            "duration_minutes": story["duration_minutes"],
            "price_narrative": story["price_narrative"],
            "price_full": story["price_full"],
            "is_featured": story.get("is_featured", False),
            "preview_url": story.get("preview_url"),
            "has_access": False
        }
    
    story["has_access"] = True
    return story

@stories_router.post("/", response_model=Dict[str, Any])
async def create_story(story: Story):
    """Create a new story"""
    story_dict = story.model_dump()
    story_dict["created_at"] = story_dict["created_at"].isoformat()
    await db.stories.insert_one(story_dict)
    return {"story_id": story.story_id, "message": "Story created successfully"}

# ===================== AI FORENSICS ROUTES =====================

@forensics_router.post("/analyze")
async def analyze_artwork(analysis_request: ForensicAnalysisRequest, request: Request):
    """AI-powered forensic analysis of artwork"""
    user = await require_auth(request)
    
    # Check if user has access to forensics
    if user.subscription_tier not in ["deep_dive", "connoisseur", "pro_collector"]:
        # Check if they purchased full access to this artwork's story
        artwork = await db.artworks.find_one({"artwork_id": analysis_request.artwork_id}, {"_id": 0})
        if artwork and artwork.get("story_id"):
            purchased_stories = user.purchased_stories or []
            # Check if purchased with full access
            if artwork["story_id"] not in purchased_stories:
                raise HTTPException(status_code=403, detail="Forensic analysis requires Deep Dive or subscription access")
    
    artwork = await db.artworks.find_one({"artwork_id": analysis_request.artwork_id}, {"_id": 0})
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    # Use Gemini for forensic analysis
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.getenv("EMERGENT_LLM_KEY")
        chat = LlmChat(
            api_key=api_key,
            session_id=f"forensics_{uuid.uuid4().hex[:8]}",
            system_message="""You are Emaira, an expert AI Art Forensics specialist. You provide detailed, scientific analysis of artworks including:
            - Pigment analysis: Chemical composition, historical availability, authenticity markers
            - Signature analysis: Brushwork patterns, pressure points, comparative analysis
            - Canvas/support analysis: Weave density, material composition, aging patterns
            - Provenance verification: Historical ownership, exhibition history, documentation
            Always respond in a professional, authoritative tone befitting a world-class art authentication expert."""
        )
        chat.with_model("gemini", "gemini-3-flash-preview")
        
        analysis_prompts = {
            "pigment": f"Analyze the pigments and colors in '{artwork['title']}' by {artwork['artist']} ({artwork['year']}). Discuss the chemical composition of colors used in this period, authenticity markers in pigment application, and any notable color choices that indicate the artist's technique or the work's authenticity.",
            "signature": f"Analyze the signature authentication aspects of '{artwork['title']}' by {artwork['artist']}. Discuss typical signature patterns of this artist, brushwork characteristics, pressure points, and how to verify authenticity through comparative analysis.",
            "canvas": f"Analyze the canvas and support structure of '{artwork['title']}' by {artwork['artist']} ({artwork['year']}). Discuss the weave density typical of this period, material composition, aging patterns, and what the support structure reveals about the work's authenticity and history.",
            "full": f"Provide a comprehensive forensic analysis of '{artwork['title']}' by {artwork['artist']} ({artwork['year']}). Cover all aspects: pigment mapping, signature authentication, canvas weave analysis, and provenance verification. Make it detailed and authoritative."
        }
        
        prompt = analysis_prompts.get(analysis_request.analysis_type, analysis_prompts["full"])
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        analysis_result = {
            "analysis_id": f"analysis_{uuid.uuid4().hex[:12]}",
            "artwork_id": analysis_request.artwork_id,
            "analysis_type": analysis_request.analysis_type,
            "results": {
                "summary": response,
                "confidence_score": 0.95,
                "analyzed_at": datetime.now(timezone.utc).isoformat()
            }
        }
        
        # Store learned forensic marker for user
        marker = {
            "artwork_id": analysis_request.artwork_id,
            "analysis_type": analysis_request.analysis_type,
            "learned_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.update_one(
            {"user_id": user.user_id},
            {"$push": {"forensic_markers_learned": marker}}
        )
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Forensic analysis error: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@forensics_router.post("/generate-visualization")
async def generate_forensic_visualization(analysis_request: ForensicAnalysisRequest, request: Request):
    """Generate AI visualization for forensic analysis"""
    user = await require_auth(request)
    
    artwork = await db.artworks.find_one({"artwork_id": analysis_request.artwork_id}, {"_id": 0})
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.getenv("EMERGENT_LLM_KEY")
        chat = LlmChat(
            api_key=api_key,
            session_id=f"viz_{uuid.uuid4().hex[:8]}",
            system_message="You are an AI that generates artistic forensic visualizations."
        )
        chat.with_model("gemini", "gemini-3-pro-image-preview").with_params(modalities=["image", "text"])
        
        viz_prompts = {
            "pigment": f"Create a scientific pigment analysis visualization overlay for a {artwork['period']} painting, showing color composition with labeled sections highlighting: vermillion, ultramarine, lead white, and organic dyes. Style: forensic analysis diagram with cyan highlights on dark background.",
            "signature": f"Create an artistic signature authentication overlay visualization showing brushstroke analysis, pressure mapping, and comparative signature patterns. Style: high-tech forensic scan with gold and cyan accents on black background.",
            "canvas": f"Create a canvas weave analysis visualization showing thread density mapping, material age patterns, and support structure. Style: scientific microscopy view with luminescent highlights on dark obsidian background."
        }
        
        prompt = viz_prompts.get(analysis_request.analysis_type, viz_prompts["pigment"])
        user_message = UserMessage(text=prompt)
        text, images = await chat.send_message_multimodal_response(user_message)
        
        image_url = None
        if images:
            # Save first image and return URL
            img_data = images[0]
            image_bytes = base64.b64decode(img_data['data'])
            image_id = f"viz_{uuid.uuid4().hex[:12]}"
            # Store in DB as base64 for simplicity
            await db.generated_images.insert_one({
                "image_id": image_id,
                "data": img_data['data'][:100] + "...",  # Store reference only
                "full_data": img_data['data'],
                "mime_type": img_data['mime_type'],
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            image_url = f"/api/forensics/image/{image_id}"
        
        return {
            "visualization_id": f"viz_{uuid.uuid4().hex[:12]}",
            "artwork_id": analysis_request.artwork_id,
            "analysis_type": analysis_request.analysis_type,
            "image_url": image_url,
            "description": text
        }
        
    except Exception as e:
        logger.error(f"Visualization generation error: {e}")
        raise HTTPException(status_code=500, detail="Visualization generation failed")

@forensics_router.get("/image/{image_id}")
async def get_forensic_image(image_id: str):
    """Get generated forensic visualization image"""
    image_doc = await db.generated_images.find_one({"image_id": image_id}, {"_id": 0})
    if not image_doc:
        raise HTTPException(status_code=404, detail="Image not found")
    
    image_bytes = base64.b64decode(image_doc["full_data"])
    return Response(content=image_bytes, media_type=image_doc.get("mime_type", "image/png"))

# ===================== PAYMENTS ROUTES =====================

@payments_router.get("/tiers")
async def get_subscription_tiers():
    """Get all subscription tiers"""
    return [tier.model_dump() for tier in SUBSCRIPTION_TIERS.values()]

@payments_router.post("/stripe/checkout")
async def create_stripe_checkout(request: Request):
    """Create Stripe checkout session"""
    body = await request.json()
    tier_id = body.get("tier_id")
    story_id = body.get("story_id")
    access_type = body.get("access_type", "narrative")  # narrative or full
    origin_url = body.get("origin_url")
    
    if not origin_url:
        raise HTTPException(status_code=400, detail="origin_url is required")
    
    user = await get_current_user(request)
    
    # Determine amount based on tier or story
    if tier_id:
        if tier_id not in SUBSCRIPTION_TIERS:
            raise HTTPException(status_code=400, detail="Invalid tier")
        tier = SUBSCRIPTION_TIERS[tier_id]
        amount = tier.price
        metadata = {"tier_id": tier_id, "type": "subscription"}
    elif story_id:
        story = await db.stories.find_one({"story_id": story_id}, {"_id": 0})
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")
        amount = story["price_full"] if access_type == "full" else story["price_narrative"]
        metadata = {"story_id": story_id, "access_type": access_type, "type": "story_purchase"}
    else:
        raise HTTPException(status_code=400, detail="tier_id or story_id required")
    
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
        
        api_key = os.getenv("STRIPE_API_KEY")
        host_url = str(request.base_url).rstrip("/")
        webhook_url = f"{host_url}/api/payments/webhook/stripe"
        
        stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
        
        success_url = f"{origin_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{origin_url}/pricing"
        
        if user:
            metadata["user_id"] = user.user_id
            metadata["email"] = user.email
        
        checkout_request = CheckoutSessionRequest(
            amount=float(amount),
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create transaction record
        transaction = PaymentTransaction(
            user_id=user.user_id if user else None,
            email=user.email if user else None,
            session_id=session.session_id,
            payment_provider="stripe",
            amount=float(amount),
            currency="usd",
            metadata=metadata,
            payment_status="pending"
        )
        txn_dict = transaction.model_dump()
        txn_dict["created_at"] = txn_dict["created_at"].isoformat()
        await db.payment_transactions.insert_one(txn_dict)
        
        return {"url": session.url, "session_id": session.session_id}
        
    except Exception as e:
        logger.error(f"Stripe checkout error: {e}")
        raise HTTPException(status_code=500, detail="Payment initialization failed")

@payments_router.get("/stripe/status/{session_id}")
async def get_stripe_payment_status(session_id: str, request: Request):
    """Check Stripe payment status and update user access"""
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        
        api_key = os.getenv("STRIPE_API_KEY")
        host_url = str(request.base_url).rstrip("/")
        webhook_url = f"{host_url}/api/payments/webhook/stripe"
        
        stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
        status = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction
        update_data = {
            "payment_status": status.payment_status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        txn = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
        
        if status.payment_status == "paid" and txn and txn.get("payment_status") != "paid":
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": update_data}
            )
            
            # Grant access
            metadata = txn.get("metadata", {})
            user_id = metadata.get("user_id")
            
            if user_id:
                if metadata.get("type") == "subscription":
                    tier_id = metadata.get("tier_id")
                    expires = datetime.now(timezone.utc) + timedelta(days=365 if SUBSCRIPTION_TIERS[tier_id].period == "year" else 30)
                    await db.users.update_one(
                        {"user_id": user_id},
                        {"$set": {
                            "subscription_tier": tier_id,
                            "subscription_expires": expires.isoformat()
                        }}
                    )
                elif metadata.get("type") == "story_purchase":
                    story_id = metadata.get("story_id")
                    access_type = metadata.get("access_type")
                    await db.users.update_one(
                        {"user_id": user_id},
                        {"$addToSet": {"purchased_stories": f"{story_id}:{access_type}"}}
                    )
        
        return {
            "status": status.status,
            "payment_status": status.payment_status,
            "amount_total": status.amount_total,
            "currency": status.currency
        }
        
    except Exception as e:
        logger.error(f"Payment status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to check payment status")

@payments_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        
        api_key = os.getenv("STRIPE_API_KEY")
        host_url = str(request.base_url).rstrip("/")
        webhook_url = f"{host_url}/api/payments/webhook/stripe"
        
        stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
        
        payload = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        webhook_response = await stripe_checkout.handle_webhook(payload, signature)
        
        logger.info(f"Stripe webhook: {webhook_response.event_type}")
        
        return {"status": "processed"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error"}

@payments_router.post("/razorpay/order")
async def create_razorpay_order(request: Request):
    """Create Razorpay order for Indian users"""
    import razorpay
    
    body = await request.json()
    tier_id = body.get("tier_id")
    story_id = body.get("story_id")
    access_type = body.get("access_type", "narrative")
    
    user = await get_current_user(request)
    
    # Determine amount (convert USD to INR approximately)
    usd_to_inr = 83  # Approximate rate
    
    if tier_id:
        if tier_id not in SUBSCRIPTION_TIERS:
            raise HTTPException(status_code=400, detail="Invalid tier")
        tier = SUBSCRIPTION_TIERS[tier_id]
        amount_usd = tier.price
        metadata = {"tier_id": tier_id, "type": "subscription"}
    elif story_id:
        story = await db.stories.find_one({"story_id": story_id}, {"_id": 0})
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")
        amount_usd = story["price_full"] if access_type == "full" else story["price_narrative"]
        metadata = {"story_id": story_id, "access_type": access_type, "type": "story_purchase"}
    else:
        raise HTTPException(status_code=400, detail="tier_id or story_id required")
    
    amount_inr = int(amount_usd * usd_to_inr * 100)  # Amount in paise
    
    razorpay_key = os.getenv("RAZORPAY_KEY_ID")
    razorpay_secret = os.getenv("RAZORPAY_KEY_SECRET")
    
    if not razorpay_key or not razorpay_secret:
        raise HTTPException(status_code=500, detail="Razorpay not configured")
    
    try:
        rz_client = razorpay.Client(auth=(razorpay_key, razorpay_secret))
        order = rz_client.order.create({
            "amount": amount_inr,
            "currency": "INR",
            "payment_capture": 1
        })
        
        if user:
            metadata["user_id"] = user.user_id
            metadata["email"] = user.email
        
        # Create transaction record
        transaction = PaymentTransaction(
            user_id=user.user_id if user else None,
            email=user.email if user else None,
            session_id=order["id"],
            payment_provider="razorpay",
            amount=float(amount_usd),
            currency="inr",
            metadata=metadata,
            payment_status="pending"
        )
        txn_dict = transaction.model_dump()
        txn_dict["created_at"] = txn_dict["created_at"].isoformat()
        await db.payment_transactions.insert_one(txn_dict)
        
        return {
            "order_id": order["id"],
            "amount": amount_inr,
            "currency": "INR",
            "key_id": razorpay_key
        }
        
    except Exception as e:
        logger.error(f"Razorpay error: {e}")
        raise HTTPException(status_code=500, detail="Payment initialization failed")

# ===================== DASHBOARD ROUTES =====================

@dashboard_router.get("/")
async def get_dashboard(request: Request):
    """Get user dashboard data"""
    user = await require_auth(request)
    
    # Get purchased stories details
    purchased_story_ids = [s.split(":")[0] for s in (user.purchased_stories or [])]
    purchased_stories = await db.stories.find(
        {"story_id": {"$in": purchased_story_ids}},
        {"_id": 0}
    ).to_list(100)
    
    # Get forensic markers count
    markers_count = len(user.forensic_markers_learned or [])
    
    # Get subscription info
    subscription_info = None
    if user.subscription_tier:
        tier = SUBSCRIPTION_TIERS.get(user.subscription_tier)
        if tier:
            subscription_info = {
                "tier": tier.model_dump(),
                "expires": user.subscription_expires.isoformat() if user.subscription_expires else None
            }
    
    return {
        "user": user.model_dump(),
        "purchased_stories": purchased_stories,
        "forensic_markers_learned": markers_count,
        "subscription": subscription_info,
        "recent_activity": user.forensic_markers_learned[-5:] if user.forensic_markers_learned else []
    }

@dashboard_router.get("/knowledge")
async def get_knowledge_dashboard(request: Request):
    """Get knowledge dashboard with learned forensic markers"""
    user = await require_auth(request)
    
    markers = user.forensic_markers_learned or []
    
    # Group by analysis type
    by_type = {}
    for marker in markers:
        t = marker.get("analysis_type", "unknown")
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(marker)
    
    return {
        "total_markers": len(markers),
        "by_type": by_type,
        "recent_markers": markers[-10:] if markers else []
    }

# ===================== SEED DATA =====================

@api_router.post("/seed")
async def seed_data():
    """Seed initial artwork and story data"""
    # Sample artworks
    artworks = [
        {
            "artwork_id": "art_mona_lisa",
            "title": "Mona Lisa",
            "artist": "Leonardo da Vinci",
            "year": "1503-1519",
            "period": "High Renaissance",
            "medium": "Oil on poplar panel",
            "dimensions": "77 cm x 53 cm",
            "location": "Louvre Museum, Paris",
            "image_url": "https://images.unsplash.com/photo-1423742774270-6884aac775fa?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1423742774270-6884aac775fa?w=400",
            "description": "The most famous portrait in the world, known for her enigmatic smile and Leonardo's masterful sfumato technique.",
            "provenance": [
                {"year": "1519", "event": "Inherited by Salai, Leonardo's assistant"},
                {"year": "1540", "event": "Acquired by Francis I of France"},
                {"year": "1797", "event": "Moved to the Louvre"},
                {"year": "1911", "event": "Stolen by Vincenzo Peruggia"},
                {"year": "1913", "event": "Recovered in Florence"}
            ],
            "is_featured": True,
            "story_id": "story_mona_lisa"
        },
        {
            "artwork_id": "art_starry_night",
            "title": "The Starry Night",
            "artist": "Vincent van Gogh",
            "year": "1889",
            "period": "Post-Impressionism",
            "medium": "Oil on canvas",
            "dimensions": "73.7 cm x 92.1 cm",
            "location": "Museum of Modern Art, New York",
            "image_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=400",
            "description": "Painted from memory during Van Gogh's stay at the asylum in Saint-Rémy-de-Provence, depicting a swirling night sky.",
            "provenance": [
                {"year": "1889", "event": "Painted at Saint-Paul-de-Mausole asylum"},
                {"year": "1900", "event": "Acquired by Emile Schuffenecker"},
                {"year": "1941", "event": "Acquired by MoMA through Lillie P. Bliss bequest"}
            ],
            "is_featured": True,
            "story_id": "story_starry_night"
        },
        {
            "artwork_id": "art_girl_pearl",
            "title": "Girl with a Pearl Earring",
            "artist": "Johannes Vermeer",
            "year": "c. 1665",
            "period": "Dutch Golden Age",
            "medium": "Oil on canvas",
            "dimensions": "44.5 cm x 39 cm",
            "location": "Mauritshuis, The Hague",
            "image_url": "https://images.unsplash.com/photo-1578321272176-b7bbc0679853?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578321272176-b7bbc0679853?w=400",
            "description": "Often called the 'Mona Lisa of the North', featuring a girl in exotic dress with a large pearl earring.",
            "provenance": [
                {"year": "1881", "event": "Purchased at auction for 2 guilders"},
                {"year": "1902", "event": "Bequeathed to the Mauritshuis"}
            ],
            "is_featured": True,
            "story_id": "story_girl_pearl"
        },
        {
            "artwork_id": "art_persistence",
            "title": "The Persistence of Memory",
            "artist": "Salvador Dalí",
            "year": "1931",
            "period": "Surrealism",
            "medium": "Oil on canvas",
            "dimensions": "24 cm x 33 cm",
            "location": "Museum of Modern Art, New York",
            "image_url": "https://images.unsplash.com/photo-1578926375605-eaf7559b1458?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578926375605-eaf7559b1458?w=400",
            "description": "Dalí's iconic surrealist masterpiece featuring melting watches in a dreamlike landscape.",
            "provenance": [
                {"year": "1931", "event": "First exhibited at Galerie Pierre Colle, Paris"},
                {"year": "1934", "event": "Acquired by MoMA"}
            ],
            "is_featured": True,
            "story_id": "story_persistence"
        },
        {
            "artwork_id": "art_birth_venus",
            "title": "The Birth of Venus",
            "artist": "Sandro Botticelli",
            "year": "c. 1485",
            "period": "Italian Renaissance",
            "medium": "Tempera on canvas",
            "dimensions": "172.5 cm x 278.5 cm",
            "location": "Uffizi Gallery, Florence",
            "image_url": "https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400",
            "description": "Depicts the goddess Venus emerging from the sea as a fully grown woman.",
            "provenance": [
                {"year": "1485", "event": "Commissioned by Lorenzo di Pierfrancesco de' Medici"},
                {"year": "1815", "event": "Entered the Uffizi collection"}
            ],
            "is_featured": True,
            "story_id": "story_birth_venus"
        }
    ]
    
    # Sample stories
    stories = [
        {
            "story_id": "story_mona_lisa",
            "artwork_id": "art_mona_lisa",
            "title": "The Enigma of Lisa Gherardini",
            "description": "Journey through 500 years of mystery surrounding the world's most famous portrait. From Leonardo's studio in Florence to its dramatic theft and recovery.",
            "duration_minutes": 5,
            "price_narrative": 9.99,
            "price_full": 49.00,
            "is_featured": True,
            "narrative_content": [
                {"timestamp": 0, "scene": "Leonardo's Studio", "narration": "Florence, 1503. In a modest studio near Santa Maria Novella..."},
                {"timestamp": 60, "scene": "The Sfumato Technique", "narration": "Leonardo developed a revolutionary technique..."},
                {"timestamp": 120, "scene": "The Theft of 1911", "narration": "On August 21, 1911, the unthinkable happened..."}
            ],
            "forensic_content": {
                "pigment_analysis": "Lead white, vermillion, azurite, walnut oil medium",
                "signature_markers": "Characteristic sfumato layering, left-handed brushstrokes",
                "canvas_analysis": "Poplar wood panel, vertical grain, 13mm thickness"
            }
        },
        {
            "story_id": "story_starry_night",
            "artwork_id": "art_starry_night",
            "title": "Visions from the Asylum Window",
            "description": "Experience the turbulent mind of Van Gogh as he painted the night sky from his asylum room, creating one of art history's most beloved works.",
            "duration_minutes": 4,
            "price_narrative": 9.99,
            "price_full": 49.00,
            "is_featured": True,
            "narrative_content": [
                {"timestamp": 0, "scene": "Saint-Rémy Asylum", "narration": "June 1889. Vincent van Gogh stands at his window..."},
                {"timestamp": 90, "scene": "The Swirling Sky", "narration": "The cypress tree rises like dark flame..."}
            ],
            "forensic_content": {
                "pigment_analysis": "Prussian blue, chrome yellow, zinc white, lead white",
                "signature_markers": "Impasto technique, visible brushstrokes, emotional energy",
                "canvas_analysis": "Standard French canvas, plain weave, primed with lead white"
            }
        },
        {
            "story_id": "story_girl_pearl",
            "artwork_id": "art_girl_pearl",
            "title": "The Mystery of the Pearl",
            "description": "Uncover the secrets of Vermeer's captivating portrait. Who was this girl? What stories does her luminous pearl earring tell?",
            "duration_minutes": 4,
            "price_narrative": 9.99,
            "price_full": 49.00,
            "is_featured": True,
            "narrative_content": [
                {"timestamp": 0, "scene": "Vermeer's Studio", "narration": "Delft, 1665. Light streams through the window..."}
            ],
            "forensic_content": {
                "pigment_analysis": "Natural ultramarine, lead-tin yellow, vermillion",
                "signature_markers": "Pointillé technique, light manipulation mastery",
                "canvas_analysis": "Fine linen canvas, tight weave pattern"
            }
        },
        {
            "story_id": "story_persistence",
            "artwork_id": "art_persistence",
            "title": "Dreams of Melting Time",
            "description": "Enter the surreal world of Salvador Dalí and discover the psychology behind his melting watches and the landscapes of the unconscious mind.",
            "duration_minutes": 3,
            "price_narrative": 9.99,
            "price_full": 49.00,
            "is_featured": True,
            "narrative_content": [
                {"timestamp": 0, "scene": "Port Lligat", "narration": "Catalonia, 1931. Dalí contemplates a melting wheel of Camembert..."}
            ],
            "forensic_content": {
                "pigment_analysis": "Cadmium yellow, cobalt blue, burnt sienna",
                "signature_markers": "Precise photorealistic technique, dreamlike juxtaposition",
                "canvas_analysis": "Small-scale canvas, fine grain, traditional priming"
            }
        },
        {
            "story_id": "story_birth_venus",
            "artwork_id": "art_birth_venus",
            "title": "When Venus Rose from the Sea",
            "description": "Travel to Renaissance Florence and witness the birth of beauty itself in Botticelli's masterpiece celebrating classical mythology.",
            "duration_minutes": 5,
            "price_narrative": 9.99,
            "price_full": 49.00,
            "is_featured": True,
            "narrative_content": [
                {"timestamp": 0, "scene": "Medici Villa", "narration": "Florence, 1485. Under Medici patronage..."}
            ],
            "forensic_content": {
                "pigment_analysis": "Lapis lazuli ultramarine, gold leaf, verdigris",
                "signature_markers": "Flowing linear style, idealized forms",
                "canvas_analysis": "Large canvas, medium weave, gesso preparation"
            }
        }
    ]
    
    # Insert data
    for artwork in artworks:
        artwork["created_at"] = datetime.now(timezone.utc).isoformat()
        await db.artworks.update_one(
            {"artwork_id": artwork["artwork_id"]},
            {"$set": artwork},
            upsert=True
        )
    
    for story in stories:
        story["created_at"] = datetime.now(timezone.utc).isoformat()
        await db.stories.update_one(
            {"story_id": story["story_id"]},
            {"$set": story},
            upsert=True
        )
    
    return {"message": "Data seeded successfully", "artworks": len(artworks), "stories": len(stories)}

# Include routers
api_router.include_router(auth_router)
api_router.include_router(artworks_router)
api_router.include_router(stories_router)
api_router.include_router(forensics_router)
api_router.include_router(payments_router)
api_router.include_router(subscriptions_router)
api_router.include_router(dashboard_router)

@api_router.get("/")
async def root():
    return {"message": "Emaira.Art API - VR Storyteller + AI Art Forensics"}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
