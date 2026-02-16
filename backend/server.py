from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends, Query
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
crm_router = APIRouter(prefix="/crm", tags=["CRM"])

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
    tags: List[str] = []
    notes: Optional[str] = None
    total_spent: float = 0.0
    last_active: Optional[datetime] = None
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
    is_featured: bool = False
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
    payment_provider: str
    amount: float
    currency: str = "usd"
    metadata: Dict[str, str] = {}
    payment_status: str = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

class ForensicAnalysisRequest(BaseModel):
    artwork_id: str
    analysis_type: str

class SubscriptionTier(BaseModel):
    tier_id: str
    name: str
    price: float
    currency: str = "usd"
    period: str
    features: List[str]

# CRM Models
class UserActivity(BaseModel):
    activity_id: str = Field(default_factory=lambda: f"act_{uuid.uuid4().hex[:12]}")
    user_id: str
    activity_type: str  # login, view_artwork, purchase, analysis, etc.
    details: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CRMNote(BaseModel):
    note_id: str = Field(default_factory=lambda: f"note_{uuid.uuid4().hex[:12]}")
    user_id: str
    content: str
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

async def log_activity(user_id: str, activity_type: str, details: Dict[str, Any] = {}):
    """Log user activity for CRM tracking"""
    activity = {
        "activity_id": f"act_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "activity_type": activity_type,
        "details": details,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.user_activities.insert_one(activity)
    
    # Update user's last_active
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"last_active": datetime.now(timezone.utc).isoformat()}}
    )

# ===================== AUTH ROUTES =====================

@auth_router.post("/session")
async def create_session(request: Request, response: Response):
    body = await request.json()
    session_id = body.get("session_id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")
    
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
    
    existing_user = await db.users.find_one({"email": email}, {"_id": 0})
    
    if existing_user:
        user_id = existing_user["user_id"]
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"name": name, "picture": picture, "last_active": datetime.now(timezone.utc).isoformat()}}
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
    
    # Log login activity
    await log_activity(user_id, "login", {"method": "google_oauth"})
    
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    session_doc = {
        "session_id": str(uuid.uuid4()),
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.user_sessions.insert_one(session_doc)
    
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
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user.model_dump()

@auth_router.post("/logout")
async def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_many({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/", secure=True, samesite="none")
    return {"message": "Logged out successfully"}

# ===================== CRM ROUTES =====================

@crm_router.get("/users")
async def get_crm_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    subscription: Optional[str] = None,
    tag: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    """Get paginated list of users with filters"""
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    if subscription:
        query["subscription_tier"] = subscription
    
    if tag:
        query["tags"] = tag
    
    skip = (page - 1) * limit
    sort_direction = -1 if sort_order == "desc" else 1
    
    total = await db.users.count_documents(query)
    users = await db.users.find(query, {"_id": 0}).sort(sort_by, sort_direction).skip(skip).limit(limit).to_list(limit)
    
    return {
        "users": users,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }

@crm_router.get("/users/{user_id}")
async def get_crm_user_detail(user_id: str):
    """Get detailed user profile with activity history"""
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get recent activities
    activities = await db.user_activities.find(
        {"user_id": user_id}, 
        {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)
    
    # Get payment history
    payments = await db.payment_transactions.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    # Get CRM notes
    notes = await db.crm_notes.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    
    # Calculate stats
    total_spent = sum(p.get("amount", 0) for p in payments if p.get("payment_status") == "paid")
    total_purchases = len([p for p in payments if p.get("payment_status") == "paid"])
    
    return {
        "user": user,
        "activities": activities,
        "payments": payments,
        "notes": notes,
        "stats": {
            "total_spent": total_spent,
            "total_purchases": total_purchases,
            "forensic_markers_count": len(user.get("forensic_markers_learned", [])),
            "purchased_stories_count": len(user.get("purchased_stories", []))
        }
    }

@crm_router.put("/users/{user_id}")
async def update_crm_user(user_id: str, request: Request):
    """Update user profile (tags, notes, etc.)"""
    body = await request.json()
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_fields = {}
    if "tags" in body:
        update_fields["tags"] = body["tags"]
    if "notes" in body:
        update_fields["notes"] = body["notes"]
    if "subscription_tier" in body:
        update_fields["subscription_tier"] = body["subscription_tier"]
    
    if update_fields:
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": update_fields}
        )
    
    return {"message": "User updated successfully"}

@crm_router.post("/users/{user_id}/notes")
async def add_crm_note(user_id: str, request: Request):
    """Add a CRM note to a user"""
    body = await request.json()
    content = body.get("content")
    created_by = body.get("created_by", "admin")
    
    if not content:
        raise HTTPException(status_code=400, detail="Note content required")
    
    note = {
        "note_id": f"note_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "content": content,
        "created_by": created_by,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.crm_notes.insert_one(note)
    
    return {"message": "Note added", "note_id": note["note_id"]}

@crm_router.get("/analytics")
async def get_crm_analytics():
    """Get CRM analytics dashboard data"""
    # Total users
    total_users = await db.users.count_documents({})
    
    # Users by subscription
    subscription_pipeline = [
        {"$group": {"_id": "$subscription_tier", "count": {"$sum": 1}}}
    ]
    subscription_stats = await db.users.aggregate(subscription_pipeline).to_list(10)
    
    # Revenue stats
    revenue_pipeline = [
        {"$match": {"payment_status": "paid"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
    ]
    revenue_stats = await db.payment_transactions.aggregate(revenue_pipeline).to_list(1)
    
    # Recent signups (last 30 days)
    thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    recent_signups = await db.users.count_documents({"created_at": {"$gte": thirty_days_ago}})
    
    # Active users (last 7 days)
    seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    active_users = await db.users.count_documents({"last_active": {"$gte": seven_days_ago}})
    
    # Top artworks viewed
    artwork_views = await db.user_activities.aggregate([
        {"$match": {"activity_type": "view_artwork"}},
        {"$group": {"_id": "$details.artwork_id", "views": {"$sum": 1}}},
        {"$sort": {"views": -1}},
        {"$limit": 10}
    ]).to_list(10)
    
    return {
        "total_users": total_users,
        "subscription_breakdown": {s["_id"] or "free": s["count"] for s in subscription_stats},
        "revenue": {
            "total": revenue_stats[0]["total"] if revenue_stats else 0,
            "transaction_count": revenue_stats[0]["count"] if revenue_stats else 0
        },
        "recent_signups_30d": recent_signups,
        "active_users_7d": active_users,
        "top_artworks": artwork_views
    }

@crm_router.get("/activities")
async def get_recent_activities(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    activity_type: Optional[str] = None,
    user_id: Optional[str] = None
):
    """Get recent user activities"""
    query = {}
    if activity_type:
        query["activity_type"] = activity_type
    if user_id:
        query["user_id"] = user_id
    
    skip = (page - 1) * limit
    total = await db.user_activities.count_documents(query)
    activities = await db.user_activities.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    return {
        "activities": activities,
        "total": total,
        "page": page,
        "limit": limit
    }

@crm_router.get("/segments")
async def get_user_segments():
    """Get user segments for targeting"""
    segments = {
        "high_value": await db.users.count_documents({"total_spent": {"$gte": 200}}),
        "subscribers": await db.users.count_documents({"subscription_tier": {"$in": ["connoisseur", "pro_collector"]}}),
        "one_time_buyers": await db.users.count_documents({
            "purchased_stories": {"$exists": True, "$ne": []},
            "subscription_tier": None
        }),
        "free_users": await db.users.count_documents({
            "subscription_tier": None,
            "purchased_stories": {"$size": 0}
        }),
        "inactive_30d": await db.users.count_documents({
            "last_active": {"$lt": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()}
        }),
        "forensics_enthusiasts": await db.users.count_documents({
            "forensic_markers_learned.5": {"$exists": True}
        })
    }
    return segments

# ===================== ARTWORKS ROUTES =====================

@artworks_router.get("/", response_model=List[Dict[str, Any]])
async def get_artworks(featured: bool = False, limit: int = 50):
    query = {"is_featured": True} if featured else {}
    artworks = await db.artworks.find(query, {"_id": 0}).limit(limit).to_list(limit)
    return artworks

@artworks_router.get("/{artwork_id}")
async def get_artwork(artwork_id: str, request: Request):
    artwork = await db.artworks.find_one({"artwork_id": artwork_id}, {"_id": 0})
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    # Log view activity if user is logged in
    user = await get_current_user(request)
    if user:
        await log_activity(user.user_id, "view_artwork", {"artwork_id": artwork_id, "title": artwork.get("title")})
    
    return artwork

@artworks_router.post("/", response_model=Dict[str, Any])
async def create_artwork(artwork: Artwork):
    artwork_dict = artwork.model_dump()
    artwork_dict["created_at"] = artwork_dict["created_at"].isoformat()
    await db.artworks.insert_one(artwork_dict)
    return {"artwork_id": artwork.artwork_id, "message": "Artwork created successfully"}

# ===================== STORIES ROUTES =====================

@stories_router.get("/", response_model=List[Dict[str, Any]])
async def get_stories(featured: bool = False, limit: int = 50):
    query = {"is_featured": True} if featured else {}
    stories = await db.stories.find(query, {"_id": 0}).limit(limit).to_list(limit)
    return stories

@stories_router.get("/{story_id}")
async def get_story(story_id: str, request: Request):
    story = await db.stories.find_one({"story_id": story_id}, {"_id": 0})
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    user = await get_current_user(request)
    has_access = False
    
    if user:
        if user.subscription_tier in ["connoisseur", "pro_collector"]:
            has_access = True
        elif story_id in user.purchased_stories:
            has_access = True
    
    if not has_access:
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
    story_dict = story.model_dump()
    story_dict["created_at"] = story_dict["created_at"].isoformat()
    await db.stories.insert_one(story_dict)
    return {"story_id": story.story_id, "message": "Story created successfully"}

# ===================== AI FORENSICS ROUTES =====================

@forensics_router.post("/analyze")
async def analyze_artwork(analysis_request: ForensicAnalysisRequest, request: Request):
    user = await require_auth(request)
    
    if user.subscription_tier not in ["deep_dive", "connoisseur", "pro_collector"]:
        artwork = await db.artworks.find_one({"artwork_id": analysis_request.artwork_id}, {"_id": 0})
        if artwork and artwork.get("story_id"):
            purchased_stories = user.purchased_stories or []
            if artwork["story_id"] not in purchased_stories:
                raise HTTPException(status_code=403, detail="Forensic analysis requires Deep Dive or subscription access")
    
    artwork = await db.artworks.find_one({"artwork_id": analysis_request.artwork_id}, {"_id": 0})
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
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
        
        # Log activity
        await log_activity(user.user_id, "forensic_analysis", {
            "artwork_id": analysis_request.artwork_id,
            "analysis_type": analysis_request.analysis_type
        })
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Forensic analysis error: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@forensics_router.post("/generate-visualization")
async def generate_forensic_visualization(analysis_request: ForensicAnalysisRequest, request: Request):
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
            img_data = images[0]
            image_id = f"viz_{uuid.uuid4().hex[:12]}"
            await db.generated_images.insert_one({
                "image_id": image_id,
                "data": img_data['data'][:100] + "...",
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
    image_doc = await db.generated_images.find_one({"image_id": image_id}, {"_id": 0})
    if not image_doc:
        raise HTTPException(status_code=404, detail="Image not found")
    
    image_bytes = base64.b64decode(image_doc["full_data"])
    return Response(content=image_bytes, media_type=image_doc.get("mime_type", "image/png"))

# ===================== PAYMENTS ROUTES =====================

@payments_router.get("/tiers")
async def get_subscription_tiers():
    return [tier.model_dump() for tier in SUBSCRIPTION_TIERS.values()]

@payments_router.post("/stripe/checkout")
async def create_stripe_checkout(request: Request):
    body = await request.json()
    tier_id = body.get("tier_id")
    story_id = body.get("story_id")
    access_type = body.get("access_type", "narrative")
    origin_url = body.get("origin_url")
    
    if not origin_url:
        raise HTTPException(status_code=400, detail="origin_url is required")
    
    user = await get_current_user(request)
    
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
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        
        api_key = os.getenv("STRIPE_API_KEY")
        host_url = str(request.base_url).rstrip("/")
        webhook_url = f"{host_url}/api/payments/webhook/stripe"
        
        stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
        status = await stripe_checkout.get_checkout_status(session_id)
        
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
                        },
                        "$inc": {"total_spent": float(txn.get("amount", 0))}}
                    )
                elif metadata.get("type") == "story_purchase":
                    story_id = metadata.get("story_id")
                    access_type = metadata.get("access_type")
                    await db.users.update_one(
                        {"user_id": user_id},
                        {"$addToSet": {"purchased_stories": f"{story_id}:{access_type}"},
                         "$inc": {"total_spent": float(txn.get("amount", 0))}}
                    )
                
                # Log purchase activity
                await log_activity(user_id, "purchase", {
                    "amount": txn.get("amount"),
                    "type": metadata.get("type"),
                    "session_id": session_id
                })
        
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
    import razorpay
    
    body = await request.json()
    tier_id = body.get("tier_id")
    story_id = body.get("story_id")
    access_type = body.get("access_type", "narrative")
    
    user = await get_current_user(request)
    
    usd_to_inr = 83
    
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
    
    amount_inr = int(amount_usd * usd_to_inr * 100)
    
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
    user = await require_auth(request)
    
    purchased_story_ids = [s.split(":")[0] for s in (user.purchased_stories or [])]
    purchased_stories = await db.stories.find(
        {"story_id": {"$in": purchased_story_ids}},
        {"_id": 0}
    ).to_list(100)
    
    markers_count = len(user.forensic_markers_learned or [])
    
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
    user = await require_auth(request)
    
    markers = user.forensic_markers_learned or []
    
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
    """Seed 20 masterpieces with full narrative and forensic data"""
    
    artworks = [
        # 1. Mona Lisa
        {
            "artwork_id": "art_mona_lisa",
            "title": "Mona Lisa",
            "artist": "Leonardo da Vinci",
            "year": "1503-1519",
            "period": "High Renaissance",
            "medium": "Oil on poplar panel",
            "dimensions": "77 cm × 53 cm",
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
            "forensic_data": {
                "pigments": ["Lead white", "Vermillion", "Azurite", "Walnut oil medium"],
                "technique": "Sfumato layering, up to 40 transparent glazes",
                "signature_markers": "Left-handed brushstrokes, characteristic sfumato transitions",
                "canvas_info": "Poplar wood panel, vertical grain, 13mm thickness"
            },
            "is_featured": True,
            "story_id": "story_mona_lisa"
        },
        # 2. Starry Night
        {
            "artwork_id": "art_starry_night",
            "title": "The Starry Night",
            "artist": "Vincent van Gogh",
            "year": "1889",
            "period": "Post-Impressionism",
            "medium": "Oil on canvas",
            "dimensions": "73.7 cm × 92.1 cm",
            "location": "Museum of Modern Art, New York",
            "image_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=400",
            "description": "Painted from memory during Van Gogh's stay at the asylum in Saint-Rémy-de-Provence, depicting a swirling night sky.",
            "provenance": [
                {"year": "1889", "event": "Painted at Saint-Paul-de-Mausole asylum"},
                {"year": "1900", "event": "Acquired by Emile Schuffenecker"},
                {"year": "1941", "event": "Acquired by MoMA through Lillie P. Bliss bequest"}
            ],
            "forensic_data": {
                "pigments": ["Prussian blue", "Chrome yellow", "Zinc white", "Lead white"],
                "technique": "Impasto, visible brushstrokes showing emotional energy",
                "signature_markers": "Characteristic thick impasto, swirling motion patterns",
                "canvas_info": "Standard French canvas, plain weave, primed with lead white"
            },
            "is_featured": True,
            "story_id": "story_starry_night"
        },
        # 3. Girl with a Pearl Earring
        {
            "artwork_id": "art_girl_pearl",
            "title": "Girl with a Pearl Earring",
            "artist": "Johannes Vermeer",
            "year": "c. 1665",
            "period": "Dutch Golden Age",
            "medium": "Oil on canvas",
            "dimensions": "44.5 cm × 39 cm",
            "location": "Mauritshuis, The Hague",
            "image_url": "https://images.unsplash.com/photo-1578321272176-b7bbc0679853?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578321272176-b7bbc0679853?w=400",
            "description": "Often called the 'Mona Lisa of the North', featuring a girl in exotic dress with a large pearl earring.",
            "provenance": [
                {"year": "1881", "event": "Purchased at auction for 2 guilders"},
                {"year": "1902", "event": "Bequeathed to the Mauritshuis"}
            ],
            "forensic_data": {
                "pigments": ["Natural ultramarine (lapis lazuli)", "Lead-tin yellow", "Vermillion", "Bone black"],
                "technique": "Pointillé highlights, masterful light manipulation",
                "signature_markers": "Characteristic soft focus, luminous skin tones",
                "canvas_info": "Fine linen canvas, tight weave pattern, thin ground layer"
            },
            "is_featured": True,
            "story_id": "story_girl_pearl"
        },
        # 4. The Persistence of Memory
        {
            "artwork_id": "art_persistence",
            "title": "The Persistence of Memory",
            "artist": "Salvador Dalí",
            "year": "1931",
            "period": "Surrealism",
            "medium": "Oil on canvas",
            "dimensions": "24 cm × 33 cm",
            "location": "Museum of Modern Art, New York",
            "image_url": "https://images.unsplash.com/photo-1578926375605-eaf7559b1458?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578926375605-eaf7559b1458?w=400",
            "description": "Dalí's iconic surrealist masterpiece featuring melting watches in a dreamlike landscape.",
            "provenance": [
                {"year": "1931", "event": "First exhibited at Galerie Pierre Colle, Paris"},
                {"year": "1934", "event": "Acquired by MoMA"}
            ],
            "forensic_data": {
                "pigments": ["Cadmium yellow", "Cobalt blue", "Burnt sienna", "Titanium white"],
                "technique": "Precise photorealistic technique, thin glazes",
                "signature_markers": "Meticulous detail, dreamlike juxtaposition",
                "canvas_info": "Small-scale canvas, fine grain, traditional priming"
            },
            "is_featured": True,
            "story_id": "story_persistence"
        },
        # 5. The Birth of Venus
        {
            "artwork_id": "art_birth_venus",
            "title": "The Birth of Venus",
            "artist": "Sandro Botticelli",
            "year": "c. 1485",
            "period": "Italian Renaissance",
            "medium": "Tempera on canvas",
            "dimensions": "172.5 cm × 278.5 cm",
            "location": "Uffizi Gallery, Florence",
            "image_url": "https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400",
            "description": "Depicts the goddess Venus emerging from the sea as a fully grown woman.",
            "provenance": [
                {"year": "1485", "event": "Commissioned by Lorenzo di Pierfrancesco de' Medici"},
                {"year": "1815", "event": "Entered the Uffizi collection"}
            ],
            "forensic_data": {
                "pigments": ["Lapis lazuli ultramarine", "Gold leaf", "Verdigris", "Red lake"],
                "technique": "Flowing linear style, idealized forms, tempera on canvas",
                "signature_markers": "Characteristic flowing lines, elongated figures",
                "canvas_info": "Large canvas, medium weave, gesso preparation"
            },
            "is_featured": True,
            "story_id": "story_birth_venus"
        },
        # 6. The Last Supper
        {
            "artwork_id": "art_last_supper",
            "title": "The Last Supper",
            "artist": "Leonardo da Vinci",
            "year": "1495-1498",
            "period": "High Renaissance",
            "medium": "Tempera and oil on gesso, pitch and mastic",
            "dimensions": "460 cm × 880 cm",
            "location": "Santa Maria delle Grazie, Milan",
            "image_url": "https://images.unsplash.com/photo-1574182245530-967d9b3831af?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1574182245530-967d9b3831af?w=400",
            "description": "Leonardo's monumental mural depicting Christ's final meal with his disciples.",
            "provenance": [
                {"year": "1498", "event": "Completed in refectory of Santa Maria delle Grazie"},
                {"year": "1796", "event": "Survived Napoleon's troops using room as stable"},
                {"year": "1943", "event": "Survived Allied bombing of Milan"}
            ],
            "forensic_data": {
                "pigments": ["Lead white", "Vermillion", "Natural ultramarine", "Earth pigments"],
                "technique": "Experimental oil and tempera on dry wall (not true fresco)",
                "signature_markers": "One-point perspective, dramatic gestures, psychological depth",
                "canvas_info": "Wall mural, gesso and pitch preparation, severe deterioration"
            },
            "is_featured": True,
            "story_id": "story_last_supper"
        },
        # 7. Guernica
        {
            "artwork_id": "art_guernica",
            "title": "Guernica",
            "artist": "Pablo Picasso",
            "year": "1937",
            "period": "Cubism/Surrealism",
            "medium": "Oil on canvas",
            "dimensions": "349 cm × 776 cm",
            "location": "Museo Reina Sofía, Madrid",
            "image_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=400",
            "description": "Picasso's powerful anti-war statement responding to the bombing of Guernica.",
            "provenance": [
                {"year": "1937", "event": "Created for Spanish Pavilion, Paris World's Fair"},
                {"year": "1939-1981", "event": "Held at MoMA, New York per Picasso's wishes"},
                {"year": "1981", "event": "Returned to Spain after democracy restored"}
            ],
            "forensic_data": {
                "pigments": ["Titanium white", "Ivory black", "Limited grayscale palette"],
                "technique": "Cubist fragmentation, powerful symbolism, monochromatic",
                "signature_markers": "Fragmented forms, distorted figures, newspaper texture elements",
                "canvas_info": "Massive scale canvas, commercial priming, rapid execution marks"
            },
            "is_featured": True,
            "story_id": "story_guernica"
        },
        # 8. The Scream
        {
            "artwork_id": "art_scream",
            "title": "The Scream",
            "artist": "Edvard Munch",
            "year": "1893",
            "period": "Expressionism",
            "medium": "Tempera and crayon on cardboard",
            "dimensions": "91 cm × 73.5 cm",
            "location": "National Gallery, Oslo",
            "image_url": "https://images.unsplash.com/photo-1579541814924-49fef17c5be5?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1579541814924-49fef17c5be5?w=400",
            "description": "An iconic image of modern anxiety and existential dread.",
            "provenance": [
                {"year": "1893", "event": "Created as part of 'The Frieze of Life' series"},
                {"year": "1994", "event": "Stolen and recovered"},
                {"year": "2004", "event": "Second theft, recovered in 2006"}
            ],
            "forensic_data": {
                "pigments": ["Cadmium pigments (orange/yellow)", "Prussian blue", "Vermillion"],
                "technique": "Bold brushwork, swirling lines, emotional color",
                "signature_markers": "Characteristic swirling sky, elongated figure",
                "canvas_info": "Cardboard support (unusual), tempera and crayon mixed media"
            },
            "is_featured": True,
            "story_id": "story_scream"
        },
        # 9. Water Lilies
        {
            "artwork_id": "art_water_lilies",
            "title": "Water Lilies",
            "artist": "Claude Monet",
            "year": "1906",
            "period": "Impressionism",
            "medium": "Oil on canvas",
            "dimensions": "89.9 cm × 94.1 cm",
            "location": "Art Institute of Chicago",
            "image_url": "https://images.unsplash.com/photo-1580136579312-94651dfd596d?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1580136579312-94651dfd596d?w=400",
            "description": "Part of Monet's famous series depicting his water garden at Giverny.",
            "provenance": [
                {"year": "1906", "event": "Painted at Giverny"},
                {"year": "1933", "event": "Acquired by Art Institute of Chicago"}
            ],
            "forensic_data": {
                "pigments": ["Cobalt blue", "Viridian", "Chrome yellow", "Lead white"],
                "technique": "Broken color, wet-on-wet application, atmospheric effects",
                "signature_markers": "Characteristic loose brushwork, reflection studies",
                "canvas_info": "Standard French canvas, commercial priming, thick impasto"
            },
            "is_featured": True,
            "story_id": "story_water_lilies"
        },
        # 10. The Night Watch
        {
            "artwork_id": "art_night_watch",
            "title": "The Night Watch",
            "artist": "Rembrandt van Rijn",
            "year": "1642",
            "period": "Dutch Golden Age",
            "medium": "Oil on canvas",
            "dimensions": "363 cm × 437 cm",
            "location": "Rijksmuseum, Amsterdam",
            "image_url": "https://images.unsplash.com/photo-1577720643272-265f09367456?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1577720643272-265f09367456?w=400",
            "description": "Rembrandt's masterpiece depicting a militia company in dramatic action.",
            "provenance": [
                {"year": "1642", "event": "Commissioned by militia company of Captain Frans Banning Cocq"},
                {"year": "1715", "event": "Trimmed to fit new location in Amsterdam Town Hall"},
                {"year": "1885", "event": "Moved to Rijksmuseum"}
            ],
            "forensic_data": {
                "pigments": ["Lead white", "Yellow ochre", "Bone black", "Smalt"],
                "technique": "Dramatic chiaroscuro, dynamic composition, thick impasto highlights",
                "signature_markers": "Characteristic dramatic lighting, psychological depth",
                "canvas_info": "Large linen canvas, multiple pieces joined, period stretcher"
            },
            "is_featured": True,
            "story_id": "story_night_watch"
        },
        # 11. American Gothic
        {
            "artwork_id": "art_american_gothic",
            "title": "American Gothic",
            "artist": "Grant Wood",
            "year": "1930",
            "period": "Regionalism",
            "medium": "Oil on beaverboard",
            "dimensions": "78 cm × 65.3 cm",
            "location": "Art Institute of Chicago",
            "image_url": "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?w=400",
            "description": "An iconic image of rural American values and Midwestern character.",
            "provenance": [
                {"year": "1930", "event": "Won bronze medal at Art Institute of Chicago exhibition"},
                {"year": "1930", "event": "Purchased by Art Institute of Chicago for $300"}
            ],
            "forensic_data": {
                "pigments": ["Earth tones", "Prussian blue", "Lead white", "Zinc white"],
                "technique": "Precise, detailed realism inspired by Flemish masters",
                "signature_markers": "Hard-edged forms, meticulous detail, flat Midwestern light",
                "canvas_info": "Beaverboard (composition board), unusual support material"
            },
            "is_featured": True,
            "story_id": "story_american_gothic"
        },
        # 12. The Kiss
        {
            "artwork_id": "art_the_kiss",
            "title": "The Kiss",
            "artist": "Gustav Klimt",
            "year": "1907-1908",
            "period": "Art Nouveau/Symbolism",
            "medium": "Oil and gold leaf on canvas",
            "dimensions": "180 cm × 180 cm",
            "location": "Österreichische Galerie Belvedere, Vienna",
            "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400",
            "description": "Klimt's masterpiece of his 'Golden Phase', depicting an embracing couple.",
            "provenance": [
                {"year": "1908", "event": "Exhibited at Kunstschau Vienna"},
                {"year": "1908", "event": "Purchased by Austrian state gallery"}
            ],
            "forensic_data": {
                "pigments": ["Gold leaf (23.5 karat)", "Silver leaf", "Platinum leaf", "Oil pigments"],
                "technique": "Byzantine-inspired gold technique, decorative patterns, flat space",
                "signature_markers": "Geometric patterns, spiral motifs, gold leaf application",
                "canvas_info": "Square format canvas, complex layering of gold and paint"
            },
            "is_featured": True,
            "story_id": "story_the_kiss"
        },
        # 13. Las Meninas
        {
            "artwork_id": "art_las_meninas",
            "title": "Las Meninas",
            "artist": "Diego Velázquez",
            "year": "1656",
            "period": "Spanish Golden Age",
            "medium": "Oil on canvas",
            "dimensions": "318 cm × 276 cm",
            "location": "Museo del Prado, Madrid",
            "image_url": "https://images.unsplash.com/photo-1582555172866-f73bb12a2ab3?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1582555172866-f73bb12a2ab3?w=400",
            "description": "A complex composition featuring the Infanta Margarita Teresa and her entourage.",
            "provenance": [
                {"year": "1656", "event": "Painted for King Philip IV's private office"},
                {"year": "1819", "event": "Transferred to Museo del Prado"}
            ],
            "forensic_data": {
                "pigments": ["Lead white", "Vermillion", "Azurite", "Yellow ochre", "Bone black"],
                "technique": "Loose brushwork, atmospheric perspective, mirror reflection illusion",
                "signature_markers": "Visible brushstrokes at distance, precise detail up close",
                "canvas_info": "Large-scale canvas, Spanish linen, period stretcher bars"
            },
            "is_featured": True,
            "story_id": "story_las_meninas"
        },
        # 14. The Great Wave off Kanagawa
        {
            "artwork_id": "art_great_wave",
            "title": "The Great Wave off Kanagawa",
            "artist": "Katsushika Hokusai",
            "year": "c. 1831",
            "period": "Edo Period",
            "medium": "Woodblock print (nishiki-e)",
            "dimensions": "25.7 cm × 37.9 cm",
            "location": "Multiple collections worldwide",
            "image_url": "https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=400",
            "description": "The most recognized work of Japanese art, showing boats beneath a huge wave.",
            "provenance": [
                {"year": "1831", "event": "Published as part of 'Thirty-six Views of Mount Fuji'"},
                {"year": "1850s", "event": "Introduced to Europe, influenced Impressionists"}
            ],
            "forensic_data": {
                "pigments": ["Prussian blue (imported)", "Indigo", "Organic yellow"],
                "technique": "Woodblock printing (mokuhanga), multiple impressions",
                "signature_markers": "Distinctive wave pattern, Mount Fuji composition",
                "canvas_info": "Mulberry paper (washi), carved cherry wood blocks"
            },
            "is_featured": True,
            "story_id": "story_great_wave"
        },
        # 15. A Sunday on La Grande Jatte
        {
            "artwork_id": "art_grande_jatte",
            "title": "A Sunday Afternoon on the Island of La Grande Jatte",
            "artist": "Georges Seurat",
            "year": "1884-1886",
            "period": "Post-Impressionism/Pointillism",
            "medium": "Oil on canvas",
            "dimensions": "207.6 cm × 308 cm",
            "location": "Art Institute of Chicago",
            "image_url": "https://images.unsplash.com/photo-1578926288207-a90a5366759d?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578926288207-a90a5366759d?w=400",
            "description": "The masterpiece of Pointillism, depicting Parisians relaxing by the Seine.",
            "provenance": [
                {"year": "1886", "event": "Exhibited at final Impressionist exhibition"},
                {"year": "1924", "event": "Acquired by Art Institute of Chicago"}
            ],
            "forensic_data": {
                "pigments": ["Chrome yellow", "Cadmium yellow", "Vermillion", "Emerald green", "Ultramarine"],
                "technique": "Pointillism/Divisionism, thousands of tiny dots of pure color",
                "signature_markers": "Scientific color theory application, painted border",
                "canvas_info": "Large canvas, over 2 years of labor, painted frame border"
            },
            "is_featured": True,
            "story_id": "story_grande_jatte"
        },
        # 16. The Creation of Adam
        {
            "artwork_id": "art_creation_adam",
            "title": "The Creation of Adam",
            "artist": "Michelangelo",
            "year": "c. 1512",
            "period": "High Renaissance",
            "medium": "Fresco",
            "dimensions": "280 cm × 570 cm",
            "location": "Sistine Chapel, Vatican City",
            "image_url": "https://images.unsplash.com/photo-1562604609-b9c81e714a78?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1562604609-b9c81e714a78?w=400",
            "description": "The iconic image of God giving life to Adam on the Sistine Chapel ceiling.",
            "provenance": [
                {"year": "1512", "event": "Completed as part of Sistine Chapel ceiling"},
                {"year": "1980-1994", "event": "Major restoration revealed original colors"}
            ],
            "forensic_data": {
                "pigments": ["Earth pigments", "Azurite", "Malachite", "Lead white", "Vermillion"],
                "technique": "Buon fresco (pigment applied to wet plaster)",
                "signature_markers": "Anatomical precision, dynamic composition, monumental scale",
                "canvas_info": "Ceiling plaster (intonaco), multiple giornate sections"
            },
            "is_featured": True,
            "story_id": "story_creation_adam"
        },
        # 17. Impression, Sunrise
        {
            "artwork_id": "art_impression_sunrise",
            "title": "Impression, Sunrise",
            "artist": "Claude Monet",
            "year": "1872",
            "period": "Impressionism",
            "medium": "Oil on canvas",
            "dimensions": "48 cm × 63 cm",
            "location": "Musée Marmottan Monet, Paris",
            "image_url": "https://images.unsplash.com/photo-1578301978018-3005759f48f7?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578301978018-3005759f48f7?w=400",
            "description": "The painting that gave Impressionism its name, depicting Le Havre harbor at sunrise.",
            "provenance": [
                {"year": "1874", "event": "Exhibited at first Impressionist exhibition"},
                {"year": "1985", "event": "Stolen and recovered in 1990"}
            ],
            "forensic_data": {
                "pigments": ["Cobalt blue", "Viridian", "Vermillion", "Chrome orange"],
                "technique": "Rapid brushwork, plein air painting, atmospheric effects",
                "signature_markers": "Loose handling, emphasis on light effects",
                "canvas_info": "Standard French canvas, rapid execution, thin paint layers"
            },
            "is_featured": True,
            "story_id": "story_impression_sunrise"
        },
        # 18. Café Terrace at Night
        {
            "artwork_id": "art_cafe_terrace",
            "title": "Café Terrace at Night",
            "artist": "Vincent van Gogh",
            "year": "1888",
            "period": "Post-Impressionism",
            "medium": "Oil on canvas",
            "dimensions": "80.7 cm × 65.3 cm",
            "location": "Kröller-Müller Museum, Netherlands",
            "image_url": "https://images.unsplash.com/photo-1579783901586-d88db74b4fe4?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1579783901586-d88db74b4fe4?w=400",
            "description": "A nocturnal scene painted on site in Arles, using no black pigment.",
            "provenance": [
                {"year": "1888", "event": "Painted in Arles, France"},
                {"year": "1890", "event": "Inherited by Theo van Gogh"},
                {"year": "1938", "event": "Acquired by Kröller-Müller Museum"}
            ],
            "forensic_data": {
                "pigments": ["Prussian blue", "Chrome yellow", "Zinc white (no black used)"],
                "technique": "Night scene with artificial and natural light, impasto",
                "signature_markers": "Swirling sky, vibrant yellows, starlight depiction",
                "canvas_info": "Standard canvas, thick impasto application"
            },
            "is_featured": True,
            "story_id": "story_cafe_terrace"
        },
        # 19. The Arnolfini Portrait
        {
            "artwork_id": "art_arnolfini",
            "title": "The Arnolfini Portrait",
            "artist": "Jan van Eyck",
            "year": "1434",
            "period": "Northern Renaissance",
            "medium": "Oil on oak panel",
            "dimensions": "82.2 cm × 60 cm",
            "location": "National Gallery, London",
            "image_url": "https://images.unsplash.com/photo-1578301978162-7aae4d755744?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578301978162-7aae4d755744?w=400",
            "description": "A revolutionary double portrait showcasing Van Eyck's mastery of oil painting.",
            "provenance": [
                {"year": "1434", "event": "Painted in Bruges"},
                {"year": "1842", "event": "Acquired by National Gallery, London"}
            ],
            "forensic_data": {
                "pigments": ["Vermillion", "Malachite", "Azurite", "Lead-tin yellow", "Gold leaf"],
                "technique": "Pioneering oil glazing technique, extreme detail, light effects",
                "signature_markers": "Mirror reflection, meticulous textile rendering",
                "canvas_info": "Oak panel, multiple thin oil glazes, remarkably preserved"
            },
            "is_featured": True,
            "story_id": "story_arnolfini"
        },
        # 20. Nighthawks
        {
            "artwork_id": "art_nighthawks",
            "title": "Nighthawks",
            "artist": "Edward Hopper",
            "year": "1942",
            "period": "American Realism",
            "medium": "Oil on canvas",
            "dimensions": "84.1 cm × 152.4 cm",
            "location": "Art Institute of Chicago",
            "image_url": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=400",
            "description": "An iconic image of urban isolation, depicting a late-night diner scene.",
            "provenance": [
                {"year": "1942", "event": "Completed shortly after Pearl Harbor attack"},
                {"year": "1942", "event": "Purchased by Art Institute of Chicago for $3,000"}
            ],
            "forensic_data": {
                "pigments": ["Cadmium red", "Viridian", "Ultramarine", "Zinc white"],
                "technique": "Sharp geometric composition, artificial light study",
                "signature_markers": "Characteristic Hopper light, urban alienation theme",
                "canvas_info": "Standard canvas, smooth paint application, careful planning"
            },
            "is_featured": True,
            "story_id": "story_nighthawks"
        }
    ]
    
    # Generate stories for all artworks
    stories = []
    for artwork in artworks:
        story = {
            "story_id": artwork["story_id"],
            "artwork_id": artwork["artwork_id"],
            "title": f"The Story of {artwork['title']}",
            "description": f"Journey through the creation, history, and authentication DNA of {artwork['artist']}'s masterpiece '{artwork['title']}'.",
            "duration_minutes": 5,
            "price_narrative": 9.99,
            "price_full": 49.00,
            "is_featured": artwork["is_featured"],
            "narrative_content": [
                {
                    "timestamp": 0,
                    "scene": "The Artist's World",
                    "narration": f"Step into the {artwork['period']} era. {artwork['artist']} begins work on what will become one of history's most celebrated artworks..."
                },
                {
                    "timestamp": 60,
                    "scene": "Creation Process",
                    "narration": f"Using {artwork['medium']}, the artist employs techniques that would influence generations. The work measures {artwork['dimensions']}..."
                },
                {
                    "timestamp": 120,
                    "scene": "Hidden Secrets",
                    "narration": f"Forensic analysis reveals the authentication DNA: {', '.join(artwork['forensic_data']['pigments'][:3])}..."
                },
                {
                    "timestamp": 180,
                    "scene": "Journey Through Time",
                    "narration": f"From {artwork['provenance'][0]['year']} to today, this masterpiece has witnessed history..."
                },
                {
                    "timestamp": 240,
                    "scene": "Legacy",
                    "narration": f"Now housed at {artwork['location']}, '{artwork['title']}' continues to inspire millions..."
                }
            ],
            "forensic_content": {
                "pigment_analysis": ", ".join(artwork["forensic_data"]["pigments"]),
                "signature_markers": artwork["forensic_data"]["signature_markers"],
                "canvas_analysis": artwork["forensic_data"]["canvas_info"],
                "technique_notes": artwork["forensic_data"]["technique"],
                "authentication_score": 98.7,
                "key_markers": [
                    f"Pigment profile matches {artwork['period']} materials",
                    f"Technique consistent with {artwork['artist']}'s documented methods",
                    f"Provenance verified through {len(artwork['provenance'])} historical records"
                ]
            }
        }
        stories.append(story)
    
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
    
    # Create indexes for CRM
    await db.user_activities.create_index([("user_id", 1), ("created_at", -1)])
    await db.user_activities.create_index([("activity_type", 1)])
    await db.users.create_index([("email", 1)], unique=True)
    await db.users.create_index([("subscription_tier", 1)])
    await db.users.create_index([("last_active", -1)])
    await db.users.create_index([("total_spent", -1)])
    
    return {"message": "Data seeded successfully", "artworks": len(artworks), "stories": len(stories)}

# Include routers
api_router.include_router(auth_router)
api_router.include_router(artworks_router)
api_router.include_router(stories_router)
api_router.include_router(forensics_router)
api_router.include_router(payments_router)
api_router.include_router(subscriptions_router)
api_router.include_router(dashboard_router)
api_router.include_router(crm_router)

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
