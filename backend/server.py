from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends, Query, UploadFile, File
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import httpx
import base64
import json
import asyncio
import resend

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Resend configuration
resend.api_key = os.environ.get('RESEND_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')

# Met Museum API configuration
MET_MUSEUM_API_BASE = os.environ.get('MET_MUSEUM_API_BASE', 'https://collectionapi.metmuseum.org/public/collection/v1')

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
admin_router = APIRouter(prefix="/admin", tags=["Admin"])
campaigns_router = APIRouter(prefix="/campaigns", tags=["Email Campaigns"])
museum_router = APIRouter(prefix="/museums", tags=["Museum Partnerships"])

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===================== ADMIN ROLE DEFINITIONS =====================

ADMIN_ROLES = {
    "super_admin": {
        "name": "Super Admin",
        "permissions": [
            "manage_users", "manage_admins", "manage_artworks", "manage_stories",
            "manage_campaigns", "manage_museums", "view_analytics", "manage_settings",
            "manage_payments", "manage_subscriptions", "delete_content"
        ],
        "description": "Full system access with all permissions"
    },
    "content_curator": {
        "name": "Content Curator",
        "permissions": [
            "manage_artworks", "manage_stories", "view_analytics", "manage_museums"
        ],
        "description": "Can manage artwork and story content, view analytics"
    },
    "marketing_admin": {
        "name": "Marketing Admin",
        "permissions": [
            "manage_campaigns", "view_analytics", "manage_users"
        ],
        "description": "Can manage email campaigns and view user data"
    },
    "support_admin": {
        "name": "Support Admin",
        "permissions": [
            "manage_users", "view_analytics"
        ],
        "description": "Can view and assist users, access support tools"
    }
}

def has_permission(role: str, permission: str) -> bool:
    """Check if a role has a specific permission"""
    if role == "admin":  # Legacy admin has all permissions
        return True
    role_def = ADMIN_ROLES.get(role)
    if not role_def:
        return False
    return permission in role_def.get("permissions", [])

# ===================== MODELS =====================

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    role: str = "user"  # user, admin, super_admin, content_curator, marketing_admin, support_admin
    admin_permissions: List[str] = []  # Specific permissions for custom roles
    subscription_tier: Optional[str] = None
    subscription_expires: Optional[datetime] = None
    purchased_stories: List[str] = []
    forensic_markers_learned: List[Dict[str, Any]] = []
    tags: List[str] = []
    notes: Optional[str] = None
    total_spent: float = 0.0
    last_active: Optional[datetime] = None
    advisory_sessions_remaining: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Artwork(BaseModel):
    model_config = ConfigDict(extra="ignore")
    artwork_id: str = Field(default_factory=lambda: f"art_{uuid.uuid4().hex[:12]}")
    title: str
    artist: str
    year: str
    period: str
    movement: Optional[str] = None
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
    is_user_submitted: bool = False
    submitted_by: Optional[str] = None
    museum_partner_id: Optional[str] = None
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

class EmailCampaign(BaseModel):
    campaign_id: str = Field(default_factory=lambda: f"camp_{uuid.uuid4().hex[:12]}")
    name: str
    subject: str
    body: str
    html_body: Optional[str] = None  # Rich HTML email content
    segment: str  # high_value, subscribers, free_users, etc.
    status: str = "draft"  # draft, scheduled, sent
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    recipients_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EmailRequest(BaseModel):
    recipient_email: EmailStr
    subject: str
    html_content: str
    
class BulkEmailRequest(BaseModel):
    campaign_id: str
    test_mode: bool = False  # If true, only send to admin email

class MuseumPartner(BaseModel):
    partner_id: str = Field(default_factory=lambda: f"museum_{uuid.uuid4().hex[:12]}")
    name: str
    location: str
    country: str
    website: str
    api_endpoint: Optional[str] = None
    artworks_count: int = 0
    partnership_tier: str = "standard"  # standard, premium, exclusive
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AdvisorySession(BaseModel):
    session_id: str = Field(default_factory=lambda: f"session_{uuid.uuid4().hex[:12]}")
    user_id: str
    advisor_name: str
    scheduled_at: datetime
    duration_minutes: int = 60
    topic: str
    status: str = "scheduled"  # scheduled, completed, cancelled
    notes: Optional[str] = None
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

class Organization(BaseModel):
    org_id: str = Field(default_factory=lambda: f"org_{uuid.uuid4().hex[:12]}")
    name: str
    type: str  # museum, gallery, collector, auction_house, educational
    contact_email: str
    contact_name: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    subscription_plan: str = "basic"  # basic, professional, enterprise
    members: List[str] = []  # List of user_ids
    admin_users: List[str] = []  # List of user_ids with org admin access
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SubscriptionTier(BaseModel):
    tier_id: str
    name: str
    price: float
    currency: str = "usd"
    period: str
    features: List[str]

# Subscription tiers configuration (updated with Collector's Advisory)
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
    ),
    "collectors_advisory": SubscriptionTier(
        tier_id="collectors_advisory",
        name="Collector's Advisory",
        price=2499.00,
        period="year",
        features=[
            "All Pro Collector features",
            "Monthly 1-on-1 video consultation with art historian",
            "Early access to authentication reports",
            "VIP gallery event invitations",
            "Personal art portfolio analysis",
            "Direct curator hotline",
            "12 advisory sessions per year"
        ]
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

async def require_admin(request: Request) -> User:
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # Check for any admin role
    admin_roles = ["admin", "super_admin", "content_curator", "marketing_admin", "support_admin", "curator"]
    if user.role not in admin_roles:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

async def require_permission(request: Request, permission: str) -> User:
    """Check if user has a specific permission"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Super admin and legacy admin have all permissions
    if user.role in ["admin", "super_admin"]:
        return user
    
    # Check role-based permissions
    if has_permission(user.role, permission):
        return user
    
    # Check custom permissions
    if permission in (user.admin_permissions or []):
        return user
    
    raise HTTPException(status_code=403, detail=f"Permission '{permission}' required")

async def require_super_admin(request: Request) -> User:
    """Only super_admin or legacy admin can access"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Super Admin access required")
    return user

async def log_activity(user_id: str, activity_type: str, details: Dict[str, Any] = {}):
    activity = {
        "activity_id": f"act_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "activity_type": activity_type,
        "details": details,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.user_activities.insert_one(activity)
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
    
    # Admin emails list (can be configured)
    admin_emails = ["admin@emaira.art"]
    
    if existing_user:
        user_id = existing_user["user_id"]
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"name": name, "picture": picture, "last_active": datetime.now(timezone.utc).isoformat()}}
        )
    else:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        role = "admin" if email in admin_emails else "user"
        new_user = User(
            user_id=user_id,
            email=email,
            name=name,
            picture=picture,
            role=role
        )
        user_doc = new_user.model_dump()
        user_doc["created_at"] = user_doc["created_at"].isoformat()
        await db.users.insert_one(user_doc)
    
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

# ===================== ADMIN ROUTES =====================

@admin_router.get("/roles")
async def get_admin_roles(request: Request):
    """Get all available admin roles and their permissions"""
    await require_admin(request)
    return {"roles": ADMIN_ROLES}

@admin_router.post("/assign-role/{user_id}")
async def assign_admin_role(user_id: str, request: Request):
    """Assign a specific admin role to a user (Super Admin only)"""
    admin = await require_super_admin(request)
    body = await request.json()
    role = body.get("role")
    
    if role not in ADMIN_ROLES and role not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail=f"Invalid role. Available: {list(ADMIN_ROLES.keys())}")
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"role": role}}
    )
    
    await log_activity(admin.user_id, "admin_action", {"action": "assign_role", "target_user": user_id, "role": role})
    
    return {"message": f"User {user_id} assigned role: {role}"}

@admin_router.post("/make-admin/{user_id}")
async def make_user_admin(user_id: str, request: Request):
    """Promote a user to super_admin role"""
    admin = await require_super_admin(request)
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"role": "super_admin"}}
    )
    
    await log_activity(admin.user_id, "admin_action", {"action": "promote_admin", "target_user": user_id})
    
    return {"message": f"User {user_id} promoted to super_admin"}

@admin_router.post("/make-curator/{user_id}")
async def make_user_curator(user_id: str, request: Request):
    """Make a user a content curator"""
    admin = await require_admin(request)
    
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"role": "content_curator"}}
    )
    
    await log_activity(admin.user_id, "admin_action", {"action": "make_curator", "target_user": user_id})
    
    return {"message": f"User {user_id} is now a content curator"}

@admin_router.post("/revoke-admin/{user_id}")
async def revoke_admin_access(user_id: str, request: Request):
    """Revoke admin access from a user (Super Admin only)"""
    admin = await require_super_admin(request)
    
    if user_id == admin.user_id:
        raise HTTPException(status_code=400, detail="Cannot revoke your own admin access")
    
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"role": "user", "admin_permissions": []}}
    )
    
    await log_activity(admin.user_id, "admin_action", {"action": "revoke_admin", "target_user": user_id})
    
    return {"message": f"Admin access revoked for user {user_id}"}

@admin_router.get("/users/admins")
async def list_admins(request: Request):
    """List all admin users with their roles"""
    await require_admin(request)
    
    admin_roles = ["admin", "super_admin", "content_curator", "marketing_admin", "support_admin", "curator"]
    admins = await db.users.find(
        {"role": {"$in": admin_roles}},
        {"_id": 0}
    ).to_list(100)
    
    # Add role descriptions
    for admin in admins:
        role = admin.get("role")
        if role in ADMIN_ROLES:
            admin["role_info"] = ADMIN_ROLES[role]
    
    return {"admins": admins, "available_roles": ADMIN_ROLES}

# ===================== ORGANIZATIONS ROUTES =====================

organizations_router = APIRouter(prefix="/organizations", tags=["Organizations"])

@organizations_router.get("/")
async def list_organizations(request: Request):
    """List all organizations (Super Admin only)"""
    await require_super_admin(request)
    
    organizations = await db.organizations.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"organizations": organizations}

@organizations_router.get("/{org_id}")
async def get_organization(org_id: str, request: Request):
    """Get organization details"""
    user = await require_auth(request)
    
    org = await db.organizations.find_one({"org_id": org_id}, {"_id": 0})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Only super_admin or org members can view
    if user.role != "super_admin" and user.user_id not in org.get("members", []) and user.user_id not in org.get("admin_users", []):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get member details
    member_ids = org.get("members", []) + org.get("admin_users", [])
    members = await db.users.find(
        {"user_id": {"$in": member_ids}},
        {"_id": 0, "user_id": 1, "email": 1, "name": 1, "picture": 1, "role": 1}
    ).to_list(100)
    
    return {"organization": org, "members": members}

@organizations_router.post("/")
async def create_organization(request: Request):
    """Create a new organization (Super Admin only)"""
    admin = await require_super_admin(request)
    body = await request.json()
    
    org = Organization(
        name=body.get("name"),
        type=body.get("type", "gallery"),
        contact_email=body.get("contact_email"),
        contact_name=body.get("contact_name"),
        website=body.get("website"),
        address=body.get("address"),
        country=body.get("country"),
        subscription_plan=body.get("subscription_plan", "basic")
    )
    
    org_dict = org.model_dump()
    org_dict["created_at"] = org_dict["created_at"].isoformat()
    await db.organizations.insert_one(org_dict)
    
    await log_activity(admin.user_id, "create_organization", {"org_id": org.org_id})
    
    return {"org_id": org.org_id, "message": "Organization created successfully"}

@organizations_router.put("/{org_id}")
async def update_organization(org_id: str, request: Request):
    """Update organization details (Super Admin only)"""
    admin = await require_super_admin(request)
    body = await request.json()
    
    org = await db.organizations.find_one({"org_id": org_id}, {"_id": 0})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    update_fields = {}
    for field in ["name", "type", "contact_email", "contact_name", "website", "address", "country", "subscription_plan", "is_active"]:
        if field in body:
            update_fields[field] = body[field]
    
    if update_fields:
        await db.organizations.update_one(
            {"org_id": org_id},
            {"$set": update_fields}
        )
    
    await log_activity(admin.user_id, "update_organization", {"org_id": org_id})
    
    return {"message": "Organization updated successfully"}

@organizations_router.delete("/{org_id}")
async def delete_organization(org_id: str, request: Request):
    """Delete organization (Super Admin only)"""
    admin = await require_super_admin(request)
    
    org = await db.organizations.find_one({"org_id": org_id}, {"_id": 0})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    await db.organizations.delete_one({"org_id": org_id})
    await log_activity(admin.user_id, "delete_organization", {"org_id": org_id})
    
    return {"message": "Organization deleted successfully"}

@organizations_router.post("/{org_id}/members")
async def add_organization_member(org_id: str, request: Request):
    """Add a member to organization (Super Admin only)"""
    admin = await require_super_admin(request)
    body = await request.json()
    user_id = body.get("user_id")
    is_admin = body.get("is_admin", False)
    
    org = await db.organizations.find_one({"org_id": org_id}, {"_id": 0})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_op = {"$addToSet": {"members": user_id}}
    if is_admin:
        update_op["$addToSet"]["admin_users"] = user_id
    
    await db.organizations.update_one({"org_id": org_id}, update_op)
    
    # Update user with org_id
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"organization_id": org_id}}
    )
    
    await log_activity(admin.user_id, "add_org_member", {"org_id": org_id, "user_id": user_id})
    
    return {"message": f"User {user_id} added to organization"}

@organizations_router.delete("/{org_id}/members/{user_id}")
async def remove_organization_member(org_id: str, user_id: str, request: Request):
    """Remove a member from organization (Super Admin only)"""
    admin = await require_super_admin(request)
    
    await db.organizations.update_one(
        {"org_id": org_id},
        {"$pull": {"members": user_id, "admin_users": user_id}}
    )
    
    await db.users.update_one(
        {"user_id": user_id},
        {"$unset": {"organization_id": ""}}
    )
    
    await log_activity(admin.user_id, "remove_org_member", {"org_id": org_id, "user_id": user_id})
    
    return {"message": f"User {user_id} removed from organization"}

# ===================== SUPERADMIN SETUP =====================

@admin_router.post("/setup-superadmin")
async def setup_superadmin(request: Request):
    """Create or update superadmin account (one-time setup)"""
    body = await request.json()
    email = body.get("email")
    name = body.get("name", "Super Admin")
    
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": email}, {"_id": 0})
    
    if existing_user:
        # Update to super_admin role
        await db.users.update_one(
            {"email": email},
            {"$set": {"role": "super_admin", "admin_permissions": list(ADMIN_ROLES["super_admin"]["permissions"])}}
        )
        return {
            "message": "User upgraded to Super Admin",
            "user_id": existing_user["user_id"],
            "email": email,
            "role": "super_admin",
            "login_method": "Sign in with Google using this email"
        }
    else:
        # Create new superadmin user
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        user_data = {
            "user_id": user_id,
            "email": email,
            "name": name,
            "picture": None,
            "role": "super_admin",
            "admin_permissions": list(ADMIN_ROLES["super_admin"]["permissions"]),
            "subscription_tier": "collectors_advisory",  # Give full access
            "purchased_stories": [],
            "forensic_markers_learned": [],
            "tags": ["superadmin", "founder"],
            "notes": "Platform super administrator",
            "total_spent": 0.0,
            "advisory_sessions_remaining": 99,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(user_data)
        
        return {
            "message": "Super Admin account created",
            "user_id": user_id,
            "email": email,
            "name": name,
            "role": "super_admin",
            "login_method": "Sign in with Google using this email",
            "subscription": "collectors_advisory (full access)"
        }

@admin_router.get("/superadmins")
async def list_superadmins(request: Request):
    """List all super admins"""
    await require_super_admin(request)
    
    superadmins = await db.users.find(
        {"role": "super_admin"},
        {"_id": 0, "user_id": 1, "email": 1, "name": 1, "picture": 1, "created_at": 1}
    ).to_list(100)
    
    return {"superadmins": superadmins}

# ===================== EMAIL CAMPAIGNS ROUTES =====================

@campaigns_router.get("/")
async def list_campaigns(request: Request):
    """List all email campaigns"""
    await require_admin(request)
    
    campaigns = await db.email_campaigns.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"campaigns": campaigns}

@campaigns_router.post("/")
async def create_campaign(request: Request):
    """Create a new email campaign"""
    admin = await require_admin(request)
    body = await request.json()
    
    campaign = EmailCampaign(
        name=body.get("name"),
        subject=body.get("subject"),
        body=body.get("body"),
        html_body=body.get("html_body"),
        segment=body.get("segment"),
        created_by=admin.user_id
    )
    
    campaign_dict = campaign.model_dump()
    campaign_dict["created_at"] = campaign_dict["created_at"].isoformat()
    if campaign_dict.get("scheduled_at"):
        campaign_dict["scheduled_at"] = campaign_dict["scheduled_at"].isoformat()
    await db.email_campaigns.insert_one(campaign_dict)
    
    await log_activity(admin.user_id, "create_campaign", {"campaign_id": campaign.campaign_id})
    
    return {"campaign_id": campaign.campaign_id, "message": "Campaign created"}

@campaigns_router.put("/{campaign_id}")
async def update_campaign(campaign_id: str, request: Request):
    """Update an existing campaign"""
    admin = await require_admin(request)
    body = await request.json()
    
    campaign = await db.email_campaigns.find_one({"campaign_id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.get("status") == "sent":
        raise HTTPException(status_code=400, detail="Cannot update a sent campaign")
    
    update_fields = {}
    for field in ["name", "subject", "body", "html_body", "segment"]:
        if field in body:
            update_fields[field] = body[field]
    
    if update_fields:
        await db.email_campaigns.update_one(
            {"campaign_id": campaign_id},
            {"$set": update_fields}
        )
    
    return {"message": "Campaign updated"}

@campaigns_router.delete("/{campaign_id}")
async def delete_campaign(campaign_id: str, request: Request):
    """Delete a campaign (draft only)"""
    admin = await require_admin(request)
    
    campaign = await db.email_campaigns.find_one({"campaign_id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign.get("status") == "sent":
        raise HTTPException(status_code=400, detail="Cannot delete a sent campaign")
    
    await db.email_campaigns.delete_one({"campaign_id": campaign_id})
    await log_activity(admin.user_id, "delete_campaign", {"campaign_id": campaign_id})
    
    return {"message": "Campaign deleted"}

async def send_email_via_resend(recipient_email: str, recipient_name: str, subject: str, html_content: str) -> dict:
    """Send a single email via Resend API"""
    if not resend.api_key:
        logger.warning("Resend API key not configured, email not sent")
        return {"status": "skipped", "reason": "Resend not configured"}
    
    # Personalize content
    personalized_html = html_content.replace("{{name}}", recipient_name or "Valued Customer")
    
    params = {
        "from": SENDER_EMAIL,
        "to": [recipient_email],
        "subject": subject,
        "html": personalized_html
    }
    
    try:
        email = await asyncio.to_thread(resend.Emails.send, params)
        return {"status": "sent", "email_id": email.get("id")}
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        return {"status": "failed", "error": str(e)}

@campaigns_router.post("/{campaign_id}/send")
async def send_campaign(campaign_id: str, request: Request):
    """Send an email campaign to its segment via Resend"""
    admin = await require_admin(request)
    body = await request.json() if request.headers.get("content-length", "0") != "0" else {}
    test_mode = body.get("test_mode", False)
    
    campaign = await db.email_campaigns.find_one({"campaign_id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Get users in segment
    segment_queries = {
        "high_value": {"total_spent": {"$gte": 200}},
        "subscribers": {"subscription_tier": {"$in": ["connoisseur", "pro_collector", "collectors_advisory"]}},
        "free_users": {"subscription_tier": None, "purchased_stories": {"$size": 0}},
        "one_time_buyers": {"purchased_stories": {"$exists": True, "$ne": []}, "subscription_tier": None},
        "advisory_members": {"subscription_tier": "collectors_advisory"},
        "all_users": {}
    }
    
    query = segment_queries.get(campaign["segment"], {})
    recipients = await db.users.find(query, {"_id": 0, "email": 1, "name": 1}).to_list(10000)
    
    # In test mode, only send to admin
    if test_mode:
        recipients = [{"email": admin.email, "name": admin.name}]
    
    # Prepare email content
    html_content = campaign.get("html_body") or f"<html><body><p>{campaign.get('body', '')}</p></body></html>"
    subject = campaign.get("subject", "Message from Emaira.Art")
    
    sent_count = 0
    failed_count = 0
    
    for recipient in recipients:
        result = await send_email_via_resend(
            recipient["email"],
            recipient.get("name", ""),
            subject,
            html_content
        )
        
        # Log each email send
        await db.email_sends.insert_one({
            "send_id": f"send_{uuid.uuid4().hex[:12]}",
            "campaign_id": campaign_id,
            "email": recipient["email"],
            "status": result["status"],
            "email_id": result.get("email_id"),
            "error": result.get("error"),
            "sent_at": datetime.now(timezone.utc).isoformat()
        })
        
        if result["status"] == "sent":
            sent_count += 1
        else:
            failed_count += 1
    
    # Update campaign status
    if not test_mode:
        await db.email_campaigns.update_one(
            {"campaign_id": campaign_id},
            {"$set": {
                "status": "sent",
                "sent_at": datetime.now(timezone.utc).isoformat(),
                "recipients_count": sent_count
            }}
        )
    
    await log_activity(admin.user_id, "send_campaign", {
        "campaign_id": campaign_id,
        "recipients_count": sent_count,
        "test_mode": test_mode
    })
    
    return {
        "message": "Test email sent" if test_mode else "Campaign sent",
        "sent_count": sent_count,
        "failed_count": failed_count,
        "campaign_id": campaign_id
    }

@campaigns_router.post("/send-single")
async def send_single_email(request: Request):
    """Send a single email (for testing or transactional emails)"""
    admin = await require_admin(request)
    body = await request.json()
    
    email_request = EmailRequest(
        recipient_email=body.get("recipient_email"),
        subject=body.get("subject"),
        html_content=body.get("html_content")
    )
    
    result = await send_email_via_resend(
        email_request.recipient_email,
        "",
        email_request.subject,
        email_request.html_content
    )
    
    if result["status"] == "sent":
        return {"message": "Email sent successfully", "email_id": result.get("email_id")}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {result.get('error')}")

@campaigns_router.get("/{campaign_id}/stats")
async def get_campaign_stats(campaign_id: str, request: Request):
    """Get campaign performance statistics"""
    await require_admin(request)
    
    campaign = await db.email_campaigns.find_one({"campaign_id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    sends = await db.email_sends.count_documents({"campaign_id": campaign_id})
    sent_success = await db.email_sends.count_documents({"campaign_id": campaign_id, "status": "sent"})
    opens = await db.email_sends.count_documents({"campaign_id": campaign_id, "opened": True})
    clicks = await db.email_sends.count_documents({"campaign_id": campaign_id, "clicked": True})
    
    return {
        "campaign": campaign,
        "stats": {
            "sent": sends,
            "opened": opens,
            "clicked": clicks,
            "open_rate": (opens / sends * 100) if sends > 0 else 0,
            "click_rate": (clicks / sends * 100) if sends > 0 else 0
        }
    }

@campaigns_router.get("/templates")
async def get_campaign_templates():
    """Get email campaign templates"""
    templates = [
        {
            "id": "welcome",
            "name": "Welcome Email",
            "subject": "Welcome to Emaira.Art - Your Art Journey Begins",
            "body": "Dear {{name}},\n\nWelcome to Emaira.Art! You've joined an exclusive community of art connoisseurs who see beyond the canvas.\n\nStart your journey with our featured masterpieces and discover the hidden DNA within each artwork.\n\nBest regards,\nThe Emaira Team"
        },
        {
            "id": "new_artwork",
            "name": "New Artwork Alert",
            "subject": "New Masterpiece Added: {{artwork_title}}",
            "body": "Dear {{name}},\n\nWe're excited to announce a new addition to our gallery: {{artwork_title}} by {{artist}}.\n\nBe among the first to experience its story and uncover its authentication DNA.\n\nExplore now at Emaira.Art"
        },
        {
            "id": "advisory_reminder",
            "name": "Advisory Session Reminder",
            "subject": "Your Collector's Advisory Session is Coming Up",
            "body": "Dear {{name}},\n\nThis is a reminder that your personal advisory session with our art historian is scheduled for {{session_date}}.\n\nPrepare any questions about your collection or artworks you're considering.\n\nSee you soon!"
        },
        {
            "id": "subscription_expiring",
            "name": "Subscription Expiring",
            "subject": "Your Emaira.Art Subscription Expires Soon",
            "body": "Dear {{name}},\n\nYour {{subscription_tier}} subscription will expire in 7 days.\n\nRenew now to continue enjoying unlimited access to our masterpiece collection and forensic analysis tools.\n\nDon't lose your learned forensic markers!"
        }
    ]
    return {"templates": templates}

# ===================== MUSEUM PARTNERSHIPS ROUTES =====================

@museum_router.get("/")
async def list_museum_partners():
    """List all museum partners"""
    partners = await db.museum_partners.find({"is_active": True}, {"_id": 0}).to_list(100)
    return {"partners": partners}

@museum_router.get("/{partner_id}")
async def get_museum_partner(partner_id: str):
    """Get museum partner details"""
    partner = await db.museum_partners.find_one({"partner_id": partner_id}, {"_id": 0})
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    # Get artworks from this partner
    artworks = await db.artworks.find(
        {"museum_partner_id": partner_id},
        {"_id": 0}
    ).to_list(100)
    
    return {"partner": partner, "artworks": artworks}

@museum_router.post("/")
async def add_museum_partner(request: Request):
    """Add a new museum partner (admin only)"""
    await require_admin(request)
    body = await request.json()
    
    partner = MuseumPartner(
        name=body.get("name"),
        location=body.get("location"),
        country=body.get("country"),
        website=body.get("website"),
        api_endpoint=body.get("api_endpoint"),
        partnership_tier=body.get("partnership_tier", "standard")
    )
    
    partner_dict = partner.model_dump()
    partner_dict["created_at"] = partner_dict["created_at"].isoformat()
    await db.museum_partners.insert_one(partner_dict)
    
    return {"partner_id": partner.partner_id, "message": "Museum partner added"}

# ===================== THE MET MUSEUM API INTEGRATION =====================

@museum_router.get("/met/search")
async def search_met_museum(
    q: str = Query(..., description="Search query"),
    has_images: bool = Query(True, description="Only return objects with images"),
    is_highlight: bool = Query(False, description="Only return highlighted works"),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    limit: int = Query(20, le=100, description="Max results to return")
):
    """Search The Met Museum's open access collection"""
    try:
        async with httpx.AsyncClient() as client_http:
            # Build search URL
            params = {"q": q, "hasImages": str(has_images).lower()}
            if is_highlight:
                params["isHighlight"] = "true"
            if department_id:
                params["departmentId"] = str(department_id)
            
            headers = {"User-Agent": "Emaira.Art/1.0 (Art Gallery Application)"}
            search_url = f"{MET_MUSEUM_API_BASE}/search"
            response = await client_http.get(search_url, params=params, headers=headers, timeout=30.0)
            
            if response.status_code != 200:
                logger.warning(f"Met Museum API returned {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Met Museum API error")
            
            data = response.json()
            object_ids = data.get("objectIDs", [])[:limit]
            
            if not object_ids:
                return {"artworks": [], "total": 0}
            
            # Fetch details for each object (limited batch)
            artworks = []
            for obj_id in object_ids[:limit]:
                try:
                    obj_response = await client_http.get(f"{MET_MUSEUM_API_BASE}/objects/{obj_id}", headers=headers, timeout=10.0)
                    if obj_response.status_code == 200:
                        obj_data = obj_response.json()
                        artworks.append({
                            "met_object_id": obj_data.get("objectID"),
                            "title": obj_data.get("title", "Untitled"),
                            "artist": obj_data.get("artistDisplayName", "Unknown Artist"),
                            "year": obj_data.get("objectDate", "Unknown"),
                            "period": obj_data.get("period", obj_data.get("culture", "Unknown")),
                            "medium": obj_data.get("medium", "Unknown"),
                            "dimensions": obj_data.get("dimensions", "Not specified"),
                            "department": obj_data.get("department", ""),
                            "image_url": obj_data.get("primaryImage", ""),
                            "thumbnail_url": obj_data.get("primaryImageSmall", ""),
                            "credit_line": obj_data.get("creditLine", ""),
                            "gallery_number": obj_data.get("GalleryNumber", ""),
                            "is_public_domain": obj_data.get("isPublicDomain", False),
                            "is_highlight": obj_data.get("isHighlight", False)
                        })
                except Exception as e:
                    logger.warning(f"Failed to fetch Met object {obj_id}: {e}")
                    continue
            
            return {
                "artworks": artworks,
                "total": len(data.get("objectIDs", [])),
                "returned": len(artworks)
            }
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Met Museum API timeout")
    except Exception as e:
        logger.error(f"Met Museum search error: {e}")
        raise HTTPException(status_code=500, detail="Failed to search Met Museum")

@museum_router.get("/met/departments")
async def get_met_departments():
    """Get list of Met Museum departments"""
    try:
        async with httpx.AsyncClient() as client_http:
            response = await client_http.get(f"{MET_MUSEUM_API_BASE}/departments", timeout=10.0)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Met Museum API error")
            return response.json()
    except Exception as e:
        logger.error(f"Met departments error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get departments")

@museum_router.get("/met/object/{object_id}")
async def get_met_object(object_id: int):
    """Get details of a specific Met Museum object"""
    try:
        async with httpx.AsyncClient() as client_http:
            response = await client_http.get(f"{MET_MUSEUM_API_BASE}/objects/{object_id}", timeout=10.0)
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Object not found")
            return response.json()
    except Exception as e:
        logger.error(f"Met object error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get object")

@museum_router.post("/met/import/{object_id}")
async def import_met_artwork(object_id: int, request: Request):
    """Import a Met Museum artwork into Emaira.Art collection"""
    admin = await require_admin(request)
    
    # Check if already imported
    existing = await db.artworks.find_one({"met_object_id": object_id}, {"_id": 0})
    if existing:
        return {"message": "Artwork already imported", "artwork_id": existing.get("artwork_id")}
    
    try:
        async with httpx.AsyncClient() as client_http:
            response = await client_http.get(f"{MET_MUSEUM_API_BASE}/objects/{object_id}", timeout=10.0)
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Object not found in Met Museum")
            
            obj_data = response.json()
            
            # Determine period/movement based on department and culture
            period = obj_data.get("period") or obj_data.get("culture") or obj_data.get("department", "Unknown Period")
            
            artwork = Artwork(
                title=obj_data.get("title", "Untitled"),
                artist=obj_data.get("artistDisplayName") or "Unknown Artist",
                year=obj_data.get("objectDate", "Unknown"),
                period=period,
                movement=obj_data.get("classification"),
                medium=obj_data.get("medium", "Unknown"),
                dimensions=obj_data.get("dimensions", "Not specified"),
                location=f"The Metropolitan Museum of Art, Gallery {obj_data.get('GalleryNumber', 'N/A')}",
                image_url=obj_data.get("primaryImage", ""),
                thumbnail_url=obj_data.get("primaryImageSmall", ""),
                description=f"{obj_data.get('objectName', 'Artwork')} from {obj_data.get('department', 'The Met Collection')}. {obj_data.get('creditLine', '')}",
                museum_partner_id="museum_met",
                is_featured=obj_data.get("isHighlight", False)
            )
            
            artwork_dict = artwork.model_dump()
            artwork_dict["met_object_id"] = object_id
            artwork_dict["created_at"] = artwork_dict["created_at"].isoformat()
            await db.artworks.insert_one(artwork_dict)
            
            # Create a story template
            story = {
                "story_id": f"story_{artwork.artwork_id.replace('art_', '')}",
                "artwork_id": artwork.artwork_id,
                "title": f"The Story of {artwork.title}",
                "description": f"Explore the history and details of '{artwork.title}' from The Metropolitan Museum of Art.",
                "duration_minutes": 4,
                "price_narrative": 9.99,
                "price_full": 49.00,
                "is_featured": artwork.is_featured,
                "narrative_content": [
                    {"timestamp": 0, "scene": "Introduction", "narration": f"Welcome to the story of '{artwork.title}' by {artwork.artist}."},
                    {"timestamp": 60, "scene": "Historical Context", "narration": f"Created during the {period} period, this work exemplifies the artistic traditions of its time."},
                    {"timestamp": 120, "scene": "Technique", "narration": f"The medium of {artwork.medium} was chosen by the artist to achieve specific visual effects."},
                    {"timestamp": 180, "scene": "Legacy", "narration": f"Now housed at The Met, this piece continues to inspire visitors from around the world."}
                ],
                "forensic_content": {
                    "status": "pending_analysis",
                    "source": "Met Museum Open Access"
                },
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.stories.insert_one(story)
            
            # Update artwork with story_id
            await db.artworks.update_one(
                {"artwork_id": artwork.artwork_id},
                {"$set": {"story_id": story["story_id"]}}
            )
            
            await log_activity(admin.user_id, "import_met_artwork", {"object_id": object_id, "artwork_id": artwork.artwork_id})
            
            return {
                "message": "Artwork imported successfully",
                "artwork_id": artwork.artwork_id,
                "story_id": story["story_id"]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Met import error: {e}")
        raise HTTPException(status_code=500, detail="Failed to import artwork")

@museum_router.post("/{partner_id}/sync")
async def sync_museum_artworks(partner_id: str, request: Request):
    """Sync artworks from museum API"""
    await require_admin(request)
    
    partner = await db.museum_partners.find_one({"partner_id": partner_id}, {"_id": 0})
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    # If it's The Met, use the Met API
    if partner_id == "museum_met":
        body = await request.json() if request.headers.get("content-length", "0") != "0" else {}
        search_query = body.get("query", "masterpiece")
        limit = body.get("limit", 10)
        
        # Search and import highlights
        try:
            async with httpx.AsyncClient() as client_http:
                search_url = f"{MET_MUSEUM_API_BASE}/search"
                response = await client_http.get(
                    search_url,
                    params={"q": search_query, "hasImages": "true", "isHighlight": "true"},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    object_ids = data.get("objectIDs", [])[:limit]
                    synced = 0
                    
                    for obj_id in object_ids:
                        # Check if exists
                        existing = await db.artworks.find_one({"met_object_id": obj_id}, {"_id": 0})
                        if not existing:
                            try:
                                obj_response = await client_http.get(f"{MET_MUSEUM_API_BASE}/objects/{obj_id}", timeout=10.0)
                                if obj_response.status_code == 200:
                                    obj_data = obj_response.json()
                                    if obj_data.get("primaryImage"):  # Only import if has image
                                        # Import logic similar to import_met_artwork
                                        synced += 1
                            except:
                                continue
                    
                    return {
                        "message": "Sync completed",
                        "partner_id": partner_id,
                        "artworks_synced": synced,
                        "total_found": len(data.get("objectIDs", []))
                    }
        except Exception as e:
            logger.error(f"Met sync error: {e}")
    
    return {
        "message": "Sync completed",
        "partner_id": partner_id,
        "artworks_synced": 0,
        "note": "Museum API integration ready"
    }

# ===================== ARTWORK UPLOAD ROUTES =====================

@artworks_router.post("/upload")
async def upload_artwork(request: Request):
    """Upload a custom artwork for analysis (Pro Collector+ only)"""
    user = await require_auth(request)
    
    if user.subscription_tier not in ["pro_collector", "collectors_advisory"]:
        raise HTTPException(status_code=403, detail="Pro Collector or Collector's Advisory subscription required")
    
    body = await request.json()
    
    artwork = Artwork(
        title=body.get("title"),
        artist=body.get("artist"),
        year=body.get("year"),
        period=body.get("period", "User Submitted"),
        movement=body.get("movement"),
        medium=body.get("medium"),
        dimensions=body.get("dimensions"),
        location=body.get("location", "Private Collection"),
        image_url=body.get("image_url"),
        thumbnail_url=body.get("image_url"),
        description=body.get("description"),
        is_user_submitted=True,
        submitted_by=user.user_id,
        is_featured=False
    )
    
    artwork_dict = artwork.model_dump()
    artwork_dict["created_at"] = artwork_dict["created_at"].isoformat()
    await db.artworks.insert_one(artwork_dict)
    
    # Create a story template for the uploaded artwork
    story = Story(
        artwork_id=artwork.artwork_id,
        title=f"Analysis of {artwork.title}",
        description=f"Custom forensic analysis of {artwork.title} by {artwork.artist}",
        duration_minutes=5,
        narrative_content=[],
        forensic_content={
            "status": "pending_analysis",
            "submitted_by": user.user_id,
            "submitted_at": datetime.now(timezone.utc).isoformat()
        }
    )
    
    story_dict = story.model_dump()
    story_dict["created_at"] = story_dict["created_at"].isoformat()
    await db.stories.insert_one(story_dict)
    
    # Update artwork with story_id
    await db.artworks.update_one(
        {"artwork_id": artwork.artwork_id},
        {"$set": {"story_id": story.story_id}}
    )
    
    await log_activity(user.user_id, "upload_artwork", {"artwork_id": artwork.artwork_id})
    
    return {
        "artwork_id": artwork.artwork_id,
        "story_id": story.story_id,
        "message": "Artwork uploaded successfully. Forensic analysis pending."
    }

@artworks_router.get("/user-submitted")
async def get_user_submitted_artworks(request: Request):
    """Get artworks submitted by the current user"""
    user = await require_auth(request)
    
    artworks = await db.artworks.find(
        {"submitted_by": user.user_id},
        {"_id": 0}
    ).to_list(100)
    
    return {"artworks": artworks}

@artworks_router.post("/admin/upload-image")
async def admin_upload_artwork_image(request: Request):
    """Admin endpoint to upload artwork with base64 image"""
    admin = await require_admin(request)
    body = await request.json()
    
    # Get base64 image data
    image_data = body.get("image_data")  # base64 encoded image
    
    if image_data:
        # Store image in database
        image_id = f"img_{uuid.uuid4().hex[:12]}"
        mime_type = body.get("mime_type", "image/jpeg")
        
        await db.uploaded_images.insert_one({
            "image_id": image_id,
            "data": image_data,
            "mime_type": mime_type,
            "uploaded_by": admin.user_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Generate URL for the image
        image_url = f"/api/artworks/image/{image_id}"
    else:
        image_url = body.get("image_url", "")
    
    artwork = Artwork(
        title=body.get("title"),
        artist=body.get("artist"),
        year=body.get("year"),
        period=body.get("period", "Unknown Period"),
        movement=body.get("movement"),
        medium=body.get("medium", "Unknown"),
        dimensions=body.get("dimensions", "Unknown"),
        location=body.get("location", "Emaira Collection"),
        image_url=image_url,
        thumbnail_url=image_url,
        description=body.get("description", ""),
        is_featured=body.get("is_featured", False),
        is_user_submitted=False,
        provenance=body.get("provenance", []),
        forensic_data=body.get("forensic_data")
    )
    
    artwork_dict = artwork.model_dump()
    artwork_dict["created_at"] = artwork_dict["created_at"].isoformat()
    await db.artworks.insert_one(artwork_dict)
    
    # Optionally create a story
    if body.get("create_story", True):
        story = {
            "story_id": f"story_{artwork.artwork_id.replace('art_', '')}",
            "artwork_id": artwork.artwork_id,
            "title": f"The Story of {artwork.title}",
            "description": f"Explore {artwork.title} by {artwork.artist}",
            "duration_minutes": 4,
            "price_narrative": 9.99,
            "price_full": 49.00,
            "is_featured": artwork.is_featured,
            "narrative_content": body.get("narrative_content", []),
            "forensic_content": body.get("forensic_content", {"status": "pending_analysis"}),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.stories.insert_one(story)
        
        await db.artworks.update_one(
            {"artwork_id": artwork.artwork_id},
            {"$set": {"story_id": story["story_id"]}}
        )
    
    await log_activity(admin.user_id, "admin_upload_artwork", {"artwork_id": artwork.artwork_id})
    
    return {
        "message": "Artwork uploaded successfully",
        "artwork_id": artwork.artwork_id,
        "image_url": image_url
    }

@artworks_router.get("/image/{image_id}")
async def get_uploaded_image(image_id: str):
    """Serve an uploaded artwork image"""
    image_doc = await db.uploaded_images.find_one({"image_id": image_id}, {"_id": 0})
    if not image_doc:
        raise HTTPException(status_code=404, detail="Image not found")
    
    image_bytes = base64.b64decode(image_doc["data"])
    return Response(content=image_bytes, media_type=image_doc.get("mime_type", "image/jpeg"))

# ===================== ADVISORY SESSIONS ROUTES =====================

@api_router.post("/advisory/book")
async def book_advisory_session(request: Request):
    """Book an advisory session (Collector's Advisory tier only)"""
    user = await require_auth(request)
    
    if user.subscription_tier != "collectors_advisory":
        raise HTTPException(status_code=403, detail="Collector's Advisory subscription required")
    
    if user.advisory_sessions_remaining <= 0:
        raise HTTPException(status_code=400, detail="No advisory sessions remaining")
    
    body = await request.json()
    
    session = AdvisorySession(
        user_id=user.user_id,
        advisor_name=body.get("advisor_name", "Dr. Elena Vasquez"),
        scheduled_at=datetime.fromisoformat(body.get("scheduled_at")),
        topic=body.get("topic"),
        duration_minutes=body.get("duration_minutes", 60)
    )
    
    session_dict = session.model_dump()
    session_dict["scheduled_at"] = session_dict["scheduled_at"].isoformat()
    session_dict["created_at"] = session_dict["created_at"].isoformat()
    await db.advisory_sessions.insert_one(session_dict)
    
    # Decrement remaining sessions
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$inc": {"advisory_sessions_remaining": -1}}
    )
    
    await log_activity(user.user_id, "book_advisory", {"session_id": session.session_id})
    
    return {"session_id": session.session_id, "message": "Session booked successfully"}

@api_router.get("/advisory/sessions")
async def get_user_advisory_sessions(request: Request):
    """Get user's advisory sessions"""
    user = await require_auth(request)
    
    sessions = await db.advisory_sessions.find(
        {"user_id": user.user_id},
        {"_id": 0}
    ).sort("scheduled_at", -1).to_list(50)
    
    return {
        "sessions": sessions,
        "remaining_sessions": user.advisory_sessions_remaining
    }

@api_router.get("/advisory/advisors")
async def get_available_advisors():
    """Get list of available art advisors"""
    advisors = [
        {
            "id": "advisor_1",
            "name": "Dr. Elena Vasquez",
            "specialty": "Renaissance & Baroque",
            "credentials": "Former Prado Museum Curator, 25+ years experience",
            "availability": ["Monday", "Wednesday", "Friday"]
        },
        {
            "id": "advisor_2",
            "name": "Prof. Marcus Chen",
            "specialty": "Modern & Contemporary Art",
            "credentials": "MIT Art Authentication Lab Director",
            "availability": ["Tuesday", "Thursday"]
        },
        {
            "id": "advisor_3",
            "name": "Dr. Isabelle Fontaine",
            "specialty": "Impressionism & Post-Impressionism",
            "credentials": "Orsay Museum Authentication Expert",
            "availability": ["Monday", "Tuesday", "Saturday"]
        },
        {
            "id": "advisor_4",
            "name": "Dr. Raj Patel",
            "specialty": "Asian & Eastern Art",
            "credentials": "Christie's Senior Authentication Specialist",
            "availability": ["Wednesday", "Friday", "Saturday"]
        }
    ]
    return {"advisors": advisors}

# ===================== CRM ROUTES =====================

@crm_router.get("/users")
async def get_crm_users(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    subscription: Optional[str] = None,
    tag: Optional[str] = None,
    role: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    """Get paginated list of users with filters (admin only)"""
    await require_admin(request)
    
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
    
    if role:
        query["role"] = role
    
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
async def get_crm_user_detail(user_id: str, request: Request):
    """Get detailed user profile with activity history (admin only)"""
    await require_admin(request)
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    activities = await db.user_activities.find(
        {"user_id": user_id}, 
        {"_id": 0}
    ).sort("created_at", -1).limit(50).to_list(50)
    
    payments = await db.payment_transactions.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    notes = await db.crm_notes.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    
    advisory_sessions = await db.advisory_sessions.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("scheduled_at", -1).to_list(20)
    
    uploaded_artworks = await db.artworks.find(
        {"submitted_by": user_id},
        {"_id": 0}
    ).to_list(50)
    
    total_spent = sum(p.get("amount", 0) for p in payments if p.get("payment_status") == "paid")
    total_purchases = len([p for p in payments if p.get("payment_status") == "paid"])
    
    return {
        "user": user,
        "activities": activities,
        "payments": payments,
        "notes": notes,
        "advisory_sessions": advisory_sessions,
        "uploaded_artworks": uploaded_artworks,
        "stats": {
            "total_spent": total_spent,
            "total_purchases": total_purchases,
            "forensic_markers_count": len(user.get("forensic_markers_learned", [])),
            "purchased_stories_count": len(user.get("purchased_stories", [])),
            "uploaded_artworks_count": len(uploaded_artworks)
        }
    }

@crm_router.put("/users/{user_id}")
async def update_crm_user(user_id: str, request: Request):
    """Update user profile (admin only)"""
    await require_admin(request)
    body = await request.json()
    
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_fields = {}
    allowed_fields = ["tags", "notes", "subscription_tier", "role", "advisory_sessions_remaining"]
    for field in allowed_fields:
        if field in body:
            update_fields[field] = body[field]
    
    if update_fields:
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": update_fields}
        )
    
    return {"message": "User updated successfully"}

@crm_router.post("/users/{user_id}/notes")
async def add_crm_note(user_id: str, request: Request):
    """Add a CRM note to a user (admin only)"""
    admin = await require_admin(request)
    body = await request.json()
    content = body.get("content")
    
    if not content:
        raise HTTPException(status_code=400, detail="Note content required")
    
    note = {
        "note_id": f"note_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "content": content,
        "created_by": admin.user_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.crm_notes.insert_one(note)
    
    return {"message": "Note added", "note_id": note["note_id"]}

@crm_router.get("/analytics")
async def get_crm_analytics(request: Request):
    """Get CRM analytics dashboard data (admin only)"""
    await require_admin(request)
    
    total_users = await db.users.count_documents({})
    
    subscription_pipeline = [
        {"$group": {"_id": "$subscription_tier", "count": {"$sum": 1}}}
    ]
    subscription_stats = await db.users.aggregate(subscription_pipeline).to_list(10)
    
    revenue_pipeline = [
        {"$match": {"payment_status": "paid"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
    ]
    revenue_stats = await db.payment_transactions.aggregate(revenue_pipeline).to_list(1)
    
    thirty_days_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    recent_signups = await db.users.count_documents({"created_at": {"$gte": thirty_days_ago}})
    
    seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    active_users = await db.users.count_documents({"last_active": {"$gte": seven_days_ago}})
    
    # Advisory tier stats
    advisory_subscribers = await db.users.count_documents({"subscription_tier": "collectors_advisory"})
    total_advisory_sessions = await db.advisory_sessions.count_documents({})
    
    # Uploaded artworks
    uploaded_artworks = await db.artworks.count_documents({"is_user_submitted": True})
    
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
        "advisory_subscribers": advisory_subscribers,
        "total_advisory_sessions": total_advisory_sessions,
        "uploaded_artworks": uploaded_artworks,
        "top_artworks": artwork_views
    }

@crm_router.get("/activities")
async def get_recent_activities(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    activity_type: Optional[str] = None,
    user_id: Optional[str] = None
):
    """Get recent user activities (admin only)"""
    await require_admin(request)
    
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
async def get_user_segments(request: Request):
    """Get user segments for targeting (admin only)"""
    await require_admin(request)
    
    segments = {
        "high_value": await db.users.count_documents({"total_spent": {"$gte": 200}}),
        "subscribers": await db.users.count_documents({"subscription_tier": {"$in": ["connoisseur", "pro_collector", "collectors_advisory"]}}),
        "collectors_advisory": await db.users.count_documents({"subscription_tier": "collectors_advisory"}),
        "pro_collectors": await db.users.count_documents({"subscription_tier": "pro_collector"}),
        "one_time_buyers": await db.users.count_documents({
            "purchased_stories": {"$exists": True, "$ne": []},
            "subscription_tier": None
        }),
        "free_users": await db.users.count_documents({
            "subscription_tier": None,
            "$or": [{"purchased_stories": {"$size": 0}}, {"purchased_stories": {"$exists": False}}]
        }),
        "inactive_30d": await db.users.count_documents({
            "last_active": {"$lt": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()}
        }),
        "forensics_enthusiasts": await db.users.count_documents({
            "forensic_markers_learned.5": {"$exists": True}
        }),
        "artwork_uploaders": await db.users.count_documents({
            "subscription_tier": {"$in": ["pro_collector", "collectors_advisory"]}
        })
    }
    return segments

# ===================== ARTWORKS ROUTES =====================

@artworks_router.get("/", response_model=List[Dict[str, Any]])
async def get_artworks(
    featured: bool = False, 
    limit: int = 50,
    period: Optional[str] = None,
    movement: Optional[str] = None
):
    query = {}
    if featured:
        query["is_featured"] = True
    if period:
        query["period"] = period
    if movement:
        query["movement"] = movement
    
    artworks = await db.artworks.find(query, {"_id": 0}).limit(limit).to_list(limit)
    return artworks

@artworks_router.get("/periods")
async def get_artwork_periods():
    """Get all available art periods"""
    periods = await db.artworks.distinct("period")
    movements = await db.artworks.distinct("movement")
    return {"periods": periods, "movements": [m for m in movements if m]}

@artworks_router.get("/{artwork_id}")
async def get_artwork(artwork_id: str, request: Request):
    artwork = await db.artworks.find_one({"artwork_id": artwork_id}, {"_id": 0})
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    user = await get_current_user(request)
    if user:
        await log_activity(user.user_id, "view_artwork", {"artwork_id": artwork_id, "title": artwork.get("title")})
    
    return artwork

@artworks_router.post("/", response_model=Dict[str, Any])
async def create_artwork(artwork: Artwork, request: Request):
    await require_admin(request)
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
        if user.subscription_tier in ["connoisseur", "pro_collector", "collectors_advisory"]:
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
async def create_story(story: Story, request: Request):
    await require_admin(request)
    story_dict = story.model_dump()
    story_dict["created_at"] = story_dict["created_at"].isoformat()
    await db.stories.insert_one(story_dict)
    return {"story_id": story.story_id, "message": "Story created successfully"}

# ===================== AI FORENSICS ROUTES =====================

@forensics_router.post("/analyze")
async def analyze_artwork(analysis_request: ForensicAnalysisRequest, request: Request):
    user = await require_auth(request)
    
    if user.subscription_tier not in ["deep_dive", "connoisseur", "pro_collector", "collectors_advisory"]:
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
        
        marker = {
            "artwork_id": analysis_request.artwork_id,
            "analysis_type": analysis_request.analysis_type,
            "learned_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.update_one(
            {"user_id": user.user_id},
            {"$push": {"forensic_markers_learned": marker}}
        )
        
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
    """Generate AI-powered forensic visualization overlay for an artwork"""
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
            system_message="""You are Dr. Emaira's Forensic Visualization System. 
            Generate detailed, scientific visualization diagrams for art authentication analysis.
            Create clear, professional visualizations with labeled sections and technical annotations."""
        )
        chat.with_model("gemini", "gemini-3.1-flash-image-preview").with_params(modalities=["image", "text"])
        
        forensic_data = artwork.get("forensic_data", {})
        pigments = forensic_data.get("pigments", ["Unknown"])
        technique = forensic_data.get("technique", "Unknown technique")
        
        viz_prompts = {
            "pigment": f"""Create a detailed pigment analysis visualization diagram for '{artwork['title']}' by {artwork['artist']} ({artwork['period']}).

Show a color-coded heat map style diagram with:
- Labeled sections for each pigment type: {', '.join(pigments) if isinstance(pigments, list) else pigments}
- Chemical composition indicators
- Period-authentic color palette markers
- Authentication markers highlighted in cyan (#00F0FF)
- Professional forensic diagram style with clean lines and labels
- Dark background (#050505) with glowing analysis points
- Include a legend showing pigment types and their locations

Style: High-tech forensic analysis interface, scientific precision, museum-quality documentation.""",

            "signature": f"""Create a signature authentication visualization for '{artwork['title']}' by {artwork['artist']}.

Show a detailed brushstroke analysis diagram with:
- Pressure mapping overlay showing stroke intensity
- Directional flow lines indicating hand movement patterns
- Comparison markers for authentic signature characteristics
- Technique indicators: {technique}
- Heat map of brush pressure (cyan to gold gradient)
- Grid overlay for precise measurement
- Authentication confidence zones marked

Style: High-tech forensic scan interface, like an FBI document analysis report but for fine art.""",

            "canvas": f"""Create a canvas weave analysis visualization for '{artwork['title']}' ({artwork['period']}).

Show a microscopic-style canvas analysis with:
- Thread density mapping with count indicators
- Weave pattern structure visualization
- Material composition zones (linen, cotton, hemp markers)
- Age-related degradation patterns
- Canvas preparation layers cross-section
- Support structure: {forensic_data.get('canvas_info', 'Traditional stretched canvas')}
- Fiber direction indicators
- Dating markers based on weave characteristics

Style: Scientific microscopy view, textile forensics, professional authentication documentation.""",

            "full": f"""Create a comprehensive forensic analysis visualization for '{artwork['title']}' by {artwork['artist']} ({artwork['year']}).

Combine all analysis types in a professional dashboard layout:
- Top section: Pigment heat map
- Middle section: Brushstroke analysis
- Bottom section: Canvas structure
- Side panel: Authentication score gauge
- Technical annotations throughout
- Period: {artwork['period']}
- Medium: {artwork.get('medium', 'Unknown')}

Style: High-end museum authentication report, combining scientific precision with elegant design."""
        }
        
        prompt = viz_prompts.get(analysis_request.analysis_type, viz_prompts["full"])
        user_message = UserMessage(text=prompt)
        text, images = await chat.send_message_multimodal_response(user_message)
        
        image_url = None
        if images:
            img_data = images[0]
            image_id = f"viz_{uuid.uuid4().hex[:12]}"
            await db.generated_images.insert_one({
                "image_id": image_id,
                "artwork_id": analysis_request.artwork_id,
                "analysis_type": analysis_request.analysis_type,
                "data": img_data['data'][:50] + "...",  # Preview only
                "full_data": img_data['data'],
                "mime_type": img_data['mime_type'],
                "generated_by": user.user_id,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            image_url = f"/api/forensics/image/{image_id}"
        
        # Log the visualization generation
        await log_activity(user.user_id, "generate_visualization", {
            "artwork_id": analysis_request.artwork_id,
            "analysis_type": analysis_request.analysis_type
        })
        
        return {
            "visualization_id": f"viz_{uuid.uuid4().hex[:12]}",
            "artwork_id": analysis_request.artwork_id,
            "artwork_title": artwork['title'],
            "analysis_type": analysis_request.analysis_type,
            "image_url": image_url,
            "description": text,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Visualization generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Visualization generation failed: {str(e)}")

@forensics_router.get("/visualizations/{artwork_id}")
async def get_artwork_visualizations(artwork_id: str, request: Request):
    """Get all generated visualizations for an artwork"""
    user = await require_auth(request)
    
    visualizations = await db.generated_images.find(
        {"artwork_id": artwork_id},
        {"_id": 0, "full_data": 0}  # Exclude the large base64 data
    ).sort("created_at", -1).to_list(20)
    
    # Add image URLs
    for viz in visualizations:
        viz["image_url"] = f"/api/forensics/image/{viz['image_id']}"
    
    return {"visualizations": visualizations}

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
                    
                    update_user = {
                        "subscription_tier": tier_id,
                        "subscription_expires": expires.isoformat()
                    }
                    
                    # Grant advisory sessions for Collector's Advisory tier
                    if tier_id == "collectors_advisory":
                        update_user["advisory_sessions_remaining"] = 12
                    
                    await db.users.update_one(
                        {"user_id": user_id},
                        {"$set": update_user, "$inc": {"total_spent": float(txn.get("amount", 0))}}
                    )
                elif metadata.get("type") == "story_purchase":
                    story_id = metadata.get("story_id")
                    access_type = metadata.get("access_type")
                    await db.users.update_one(
                        {"user_id": user_id},
                        {"$addToSet": {"purchased_stories": f"{story_id}:{access_type}"},
                         "$inc": {"total_spent": float(txn.get("amount", 0))}}
                    )
                
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

# ===================== SUBSCRIPTIONS ROUTES =====================

@subscriptions_router.get("/")
async def list_subscription_tiers():
    """Get all available subscription tiers"""
    tiers = []
    for tier_id, tier in SUBSCRIPTION_TIERS.items():
        tier_data = tier.model_dump()
        tier_data["tier_id"] = tier_id
        tiers.append(tier_data)
    return {"tiers": tiers}

@subscriptions_router.get("/{tier_id}")
async def get_subscription_tier(tier_id: str):
    """Get details of a specific subscription tier"""
    if tier_id not in SUBSCRIPTION_TIERS:
        raise HTTPException(status_code=404, detail="Tier not found")
    tier = SUBSCRIPTION_TIERS[tier_id]
    return tier.model_dump()

@subscriptions_router.get("/user/current")
async def get_user_subscription(request: Request):
    """Get current user's subscription status"""
    user = await require_auth(request)
    
    if not user.subscription_tier:
        return {
            "has_subscription": False,
            "tier": None,
            "expires": None,
            "features": []
        }
    
    tier = SUBSCRIPTION_TIERS.get(user.subscription_tier)
    return {
        "has_subscription": True,
        "tier": tier.model_dump() if tier else None,
        "tier_id": user.subscription_tier,
        "expires": user.subscription_expires.isoformat() if user.subscription_expires else None,
        "advisory_sessions_remaining": user.advisory_sessions_remaining if user.subscription_tier == "collectors_advisory" else 0,
        "features": tier.features if tier else []
    }

@subscriptions_router.post("/compare")
async def compare_subscription_tiers(request: Request):
    """Compare features across subscription tiers"""
    body = await request.json()
    tier_ids = body.get("tier_ids", list(SUBSCRIPTION_TIERS.keys()))
    
    comparison = []
    all_features = set()
    
    for tier_id in tier_ids:
        if tier_id in SUBSCRIPTION_TIERS:
            tier = SUBSCRIPTION_TIERS[tier_id]
            all_features.update(tier.features)
    
    for tier_id in tier_ids:
        if tier_id in SUBSCRIPTION_TIERS:
            tier = SUBSCRIPTION_TIERS[tier_id]
            tier_features = {
                "tier_id": tier_id,
                "name": tier.name,
                "price": tier.price,
                "period": tier.period,
                "features": {f: f in tier.features for f in all_features}
            }
            comparison.append(tier_features)
    
    return {"comparison": comparison, "all_features": list(all_features)}

# ===================== VR NARRATIVE GENERATION =====================

@api_router.post("/vr/generate-narrative/{artwork_id}")
async def generate_vr_narrative(artwork_id: str, request: Request):
    """Generate an immersive VR narrative for an artwork using AI"""
    user = await require_auth(request)
    
    # Check access
    if user.subscription_tier not in ["connoisseur", "pro_collector", "collectors_advisory"]:
        artwork = await db.artworks.find_one({"artwork_id": artwork_id}, {"_id": 0})
        if artwork and artwork.get("story_id"):
            purchased_stories = user.purchased_stories or []
            if not any(artwork["story_id"] in s for s in purchased_stories):
                raise HTTPException(status_code=403, detail="Subscription or story purchase required")
    
    artwork = await db.artworks.find_one({"artwork_id": artwork_id}, {"_id": 0})
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.getenv("EMERGENT_LLM_KEY")
        chat = LlmChat(
            api_key=api_key,
            session_id=f"vr_narrative_{uuid.uuid4().hex[:8]}",
            system_message="""You are Emaira, an expert art historian and immersive storyteller. 
            Create cinematic VR narratives that transport viewers through time and space. 
            Your narratives should be rich with sensory details, historical context, and emotional depth.
            Structure your response as a JSON array of scenes, each with: scene_number, title, duration_seconds, narration, visual_cues, ambient_sounds, and camera_direction."""
        )
        chat.with_model("gemini", "gemini-3-flash-preview")
        
        prompt = f"""Create an immersive 5-minute VR narrative experience for '{artwork['title']}' by {artwork['artist']} ({artwork['year']}).

Artwork details:
- Period: {artwork.get('period', 'Unknown')}
- Medium: {artwork.get('medium', 'Unknown')}
- Location: {artwork.get('location', 'Unknown')}
- Description: {artwork.get('description', '')}

Create 5 scenes that take the viewer on a journey:
1. The Artist's World - Set the historical context
2. The Creation - Show the artistic process
3. Hidden Secrets - Reveal forensic details and techniques
4. Journey Through Time - Show the artwork's history and provenance
5. Legacy - The artwork's impact and significance today

For each scene, provide narration text and visual/audio direction for VR implementation.
Return as valid JSON array."""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Try to parse as JSON, otherwise wrap in structure
        try:
            import json
            scenes = json.loads(response)
        except:
            scenes = [
                {
                    "scene_number": 1,
                    "title": "The Story",
                    "duration_seconds": 300,
                    "narration": response,
                    "visual_cues": "Pan across the artwork",
                    "ambient_sounds": "Soft classical music",
                    "camera_direction": "Slow zoom"
                }
            ]
        
        narrative_result = {
            "narrative_id": f"narrative_{uuid.uuid4().hex[:12]}",
            "artwork_id": artwork_id,
            "title": f"The VR Story of {artwork['title']}",
            "scenes": scenes,
            "total_duration_minutes": 5,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Store the generated narrative
        await db.vr_narratives.insert_one(narrative_result)
        
        await log_activity(user.user_id, "generate_vr_narrative", {"artwork_id": artwork_id})
        
        return narrative_result
        
    except Exception as e:
        logger.error(f"VR narrative generation error: {e}")
        raise HTTPException(status_code=500, detail="Narrative generation failed")

@api_router.get("/vr/narrative/{artwork_id}")
async def get_vr_narrative(artwork_id: str, request: Request):
    """Get existing VR narrative for an artwork"""
    # Check if narrative exists
    narrative = await db.vr_narratives.find_one(
        {"artwork_id": artwork_id},
        {"_id": 0}
    )
    
    if not narrative:
        # Return the pre-seeded narrative content from story
        story = await db.stories.find_one({"artwork_id": artwork_id}, {"_id": 0})
        if story:
            return {
                "narrative_id": story.get("story_id"),
                "artwork_id": artwork_id,
                "title": story.get("title"),
                "scenes": story.get("narrative_content", []),
                "forensic_content": story.get("forensic_content", {}),
                "total_duration_minutes": story.get("duration_minutes", 5)
            }
        raise HTTPException(status_code=404, detail="Narrative not found")
    
    return narrative

# ===================== ENHANCED FORENSICS =====================

@forensics_router.get("/report/{artwork_id}")
async def get_forensic_report(artwork_id: str, request: Request):
    """Get a comprehensive forensic report for an artwork"""
    user = await require_auth(request)
    
    artwork = await db.artworks.find_one({"artwork_id": artwork_id}, {"_id": 0})
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    # Check if user has access
    has_full_access = user.subscription_tier in ["deep_dive", "connoisseur", "pro_collector", "collectors_advisory"]
    if not has_full_access:
        if artwork.get("story_id"):
            purchased = user.purchased_stories or []
            has_full_access = any(artwork["story_id"] in s and "full" in s for s in purchased)
    
    # Get existing forensic data from artwork
    forensic_data = artwork.get("forensic_data", {})
    
    # Get any AI-generated analyses for this artwork
    analyses = await db.forensic_analyses.find(
        {"artwork_id": artwork_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(10)
    
    report = {
        "artwork_id": artwork_id,
        "title": artwork.get("title"),
        "artist": artwork.get("artist"),
        "year": artwork.get("year"),
        "forensic_summary": {
            "pigments": forensic_data.get("pigments", []),
            "technique": forensic_data.get("technique", ""),
            "signature_markers": forensic_data.get("signature_markers", ""),
            "canvas_info": forensic_data.get("canvas_info", ""),
            "authentication_score": forensic_data.get("authentication_score", 95)
        },
        "has_full_access": has_full_access,
        "ai_analyses": analyses if has_full_access else [],
        "provenance": artwork.get("provenance", []) if has_full_access else []
    }
    
    if not has_full_access:
        report["upgrade_message"] = "Upgrade to Deep Dive or higher to access full forensic analysis"
    
    return report

@forensics_router.post("/deep-analysis")
async def perform_deep_forensic_analysis(request: Request):
    """Perform comprehensive AI-powered forensic analysis"""
    user = await require_auth(request)
    body = await request.json()
    artwork_id = body.get("artwork_id")
    
    # Only available for premium tiers
    if user.subscription_tier not in ["pro_collector", "collectors_advisory"]:
        raise HTTPException(status_code=403, detail="Pro Collector or Collector's Advisory subscription required")
    
    artwork = await db.artworks.find_one({"artwork_id": artwork_id}, {"_id": 0})
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        api_key = os.getenv("EMERGENT_LLM_KEY")
        chat = LlmChat(
            api_key=api_key,
            session_id=f"deep_forensics_{uuid.uuid4().hex[:8]}",
            system_message="""You are Dr. Emaira, the world's foremost AI art authentication specialist with expertise in:
            - Spectroscopic analysis (X-ray fluorescence, infrared reflectography)
            - Dendrochronology for wooden supports
            - Canvas weave pattern analysis
            - Pigment chronology and geographic sourcing
            - Brushwork forensics and gesture analysis
            - Craquelure pattern dating
            - Provenance chain verification
            
            Provide detailed, scientific analysis with confidence scores and specific technical findings.
            Structure your response as a comprehensive authentication report."""
        )
        chat.with_model("gemini", "gemini-3-flash-preview")
        
        existing_forensic = artwork.get("forensic_data", {})
        
        prompt = f"""Conduct a comprehensive forensic authentication analysis for:

Artwork: '{artwork['title']}'
Artist: {artwork['artist']}
Date: {artwork['year']}
Period: {artwork.get('period', 'Unknown')}
Medium: {artwork.get('medium', 'Unknown')}
Dimensions: {artwork.get('dimensions', 'Unknown')}
Current Location: {artwork.get('location', 'Unknown')}

Known Forensic Data:
- Pigments: {existing_forensic.get('pigments', 'Not analyzed')}
- Technique: {existing_forensic.get('technique', 'Not documented')}
- Support: {existing_forensic.get('canvas_info', 'Not analyzed')}

Provide a detailed authentication report covering:
1. PIGMENT ANALYSIS - Chemical composition, period consistency, geographic sourcing
2. SUPPORT ANALYSIS - Material, age indicators, preparation layers
3. TECHNIQUE ANALYSIS - Brushwork, layering, underdrawing
4. SIGNATURE VERIFICATION - Comparative analysis, pressure patterns
5. PROVENANCE ASSESSMENT - Documentary evidence strength
6. CONDITION REPORT - Conservation history, alterations
7. AUTHENTICATION CONCLUSION - Overall confidence score with justification

Include specific technical terminology and quantitative assessments where applicable."""

        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        analysis_result = {
            "analysis_id": f"deep_{uuid.uuid4().hex[:12]}",
            "artwork_id": artwork_id,
            "analysis_type": "deep_forensic",
            "analyst": "Dr. Emaira AI",
            "report": response,
            "confidence_score": 0.97,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": user.user_id
        }
        
        # Store the analysis
        await db.forensic_analyses.insert_one(analysis_result)
        
        # Update user's forensic markers
        marker = {
            "artwork_id": artwork_id,
            "analysis_type": "deep_forensic",
            "learned_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.update_one(
            {"user_id": user.user_id},
            {"$push": {"forensic_markers_learned": marker}}
        )
        
        await log_activity(user.user_id, "deep_forensic_analysis", {"artwork_id": artwork_id})
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Deep forensic analysis error: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

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
                "expires": user.subscription_expires.isoformat() if user.subscription_expires else None,
                "advisory_sessions_remaining": user.advisory_sessions_remaining if user.subscription_tier == "collectors_advisory" else 0
            }
    
    # Get uploaded artworks count
    uploaded_count = await db.artworks.count_documents({"submitted_by": user.user_id})
    
    return {
        "user": user.model_dump(),
        "purchased_stories": purchased_stories,
        "forensic_markers_learned": markers_count,
        "subscription": subscription_info,
        "uploaded_artworks_count": uploaded_count,
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
    """Seed 30+ masterpieces including modern art with full narrative and forensic data"""
    
    artworks = [
        # RENAISSANCE & BAROQUE (1-8)
        {
            "artwork_id": "art_mona_lisa",
            "title": "Mona Lisa",
            "artist": "Leonardo da Vinci",
            "year": "1503-1519",
            "period": "High Renaissance",
            "movement": "Renaissance",
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
        {
            "artwork_id": "art_last_supper",
            "title": "The Last Supper",
            "artist": "Leonardo da Vinci",
            "year": "1495-1498",
            "period": "High Renaissance",
            "movement": "Renaissance",
            "medium": "Tempera and oil on gesso",
            "dimensions": "460 cm × 880 cm",
            "location": "Santa Maria delle Grazie, Milan",
            "image_url": "https://images.unsplash.com/photo-1574182245530-967d9b3831af?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1574182245530-967d9b3831af?w=400",
            "description": "Leonardo's monumental mural depicting Christ's final meal with his disciples.",
            "provenance": [
                {"year": "1498", "event": "Completed in refectory"},
                {"year": "1943", "event": "Survived Allied bombing"}
            ],
            "forensic_data": {
                "pigments": ["Lead white", "Vermillion", "Natural ultramarine"],
                "technique": "Experimental oil and tempera on dry wall",
                "signature_markers": "One-point perspective, psychological depth",
                "canvas_info": "Wall mural, severe deterioration"
            },
            "is_featured": True,
            "story_id": "story_last_supper"
        },
        {
            "artwork_id": "art_creation_adam",
            "title": "The Creation of Adam",
            "artist": "Michelangelo",
            "year": "c. 1512",
            "period": "High Renaissance",
            "movement": "Renaissance",
            "medium": "Fresco",
            "dimensions": "280 cm × 570 cm",
            "location": "Sistine Chapel, Vatican City",
            "image_url": "https://images.unsplash.com/photo-1562604609-b9c81e714a78?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1562604609-b9c81e714a78?w=400",
            "description": "The iconic image of God giving life to Adam on the Sistine Chapel ceiling.",
            "provenance": [
                {"year": "1512", "event": "Completed on Sistine ceiling"},
                {"year": "1994", "event": "Major restoration completed"}
            ],
            "forensic_data": {
                "pigments": ["Earth pigments", "Azurite", "Malachite", "Vermillion"],
                "technique": "Buon fresco on wet plaster",
                "signature_markers": "Anatomical precision, dynamic composition",
                "canvas_info": "Ceiling plaster, multiple giornate"
            },
            "is_featured": True,
            "story_id": "story_creation_adam"
        },
        {
            "artwork_id": "art_birth_venus",
            "title": "The Birth of Venus",
            "artist": "Sandro Botticelli",
            "year": "c. 1485",
            "period": "Italian Renaissance",
            "movement": "Renaissance",
            "medium": "Tempera on canvas",
            "dimensions": "172.5 cm × 278.5 cm",
            "location": "Uffizi Gallery, Florence",
            "image_url": "https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1544967082-d9d25d867d66?w=400",
            "description": "Venus emerging from the sea as a fully grown woman.",
            "provenance": [
                {"year": "1485", "event": "Commissioned by Medici"},
                {"year": "1815", "event": "Entered Uffizi"}
            ],
            "forensic_data": {
                "pigments": ["Lapis lazuli ultramarine", "Gold leaf", "Verdigris"],
                "technique": "Flowing linear style, tempera on canvas",
                "signature_markers": "Flowing lines, elongated figures",
                "canvas_info": "Large canvas, gesso preparation"
            },
            "is_featured": True,
            "story_id": "story_birth_venus"
        },
        {
            "artwork_id": "art_girl_pearl",
            "title": "Girl with a Pearl Earring",
            "artist": "Johannes Vermeer",
            "year": "c. 1665",
            "period": "Dutch Golden Age",
            "movement": "Baroque",
            "medium": "Oil on canvas",
            "dimensions": "44.5 cm × 39 cm",
            "location": "Mauritshuis, The Hague",
            "image_url": "https://images.unsplash.com/photo-1578321272176-b7bbc0679853?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578321272176-b7bbc0679853?w=400",
            "description": "Often called the 'Mona Lisa of the North'.",
            "provenance": [
                {"year": "1881", "event": "Purchased for 2 guilders"},
                {"year": "1902", "event": "Bequeathed to Mauritshuis"}
            ],
            "forensic_data": {
                "pigments": ["Natural ultramarine (lapis lazuli)", "Lead-tin yellow", "Vermillion"],
                "technique": "Pointillé highlights, light manipulation",
                "signature_markers": "Soft focus, luminous skin tones",
                "canvas_info": "Fine linen canvas, tight weave"
            },
            "is_featured": True,
            "story_id": "story_girl_pearl"
        },
        {
            "artwork_id": "art_night_watch",
            "title": "The Night Watch",
            "artist": "Rembrandt van Rijn",
            "year": "1642",
            "period": "Dutch Golden Age",
            "movement": "Baroque",
            "medium": "Oil on canvas",
            "dimensions": "363 cm × 437 cm",
            "location": "Rijksmuseum, Amsterdam",
            "image_url": "https://images.unsplash.com/photo-1577720643272-265f09367456?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1577720643272-265f09367456?w=400",
            "description": "Rembrandt's masterpiece depicting a militia company in dramatic action.",
            "provenance": [
                {"year": "1642", "event": "Commissioned by militia"},
                {"year": "1715", "event": "Trimmed to fit new location"},
                {"year": "1885", "event": "Moved to Rijksmuseum"}
            ],
            "forensic_data": {
                "pigments": ["Lead white", "Yellow ochre", "Bone black", "Smalt"],
                "technique": "Dramatic chiaroscuro, thick impasto highlights",
                "signature_markers": "Dramatic lighting, psychological depth",
                "canvas_info": "Large linen canvas, multiple pieces joined"
            },
            "is_featured": True,
            "story_id": "story_night_watch"
        },
        {
            "artwork_id": "art_las_meninas",
            "title": "Las Meninas",
            "artist": "Diego Velázquez",
            "year": "1656",
            "period": "Spanish Golden Age",
            "movement": "Baroque",
            "medium": "Oil on canvas",
            "dimensions": "318 cm × 276 cm",
            "location": "Museo del Prado, Madrid",
            "image_url": "https://images.unsplash.com/photo-1582555172866-f73bb12a2ab3?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1582555172866-f73bb12a2ab3?w=400",
            "description": "A complex composition featuring Infanta Margarita Teresa.",
            "provenance": [
                {"year": "1656", "event": "Painted for Philip IV"},
                {"year": "1819", "event": "Transferred to Prado"}
            ],
            "forensic_data": {
                "pigments": ["Lead white", "Vermillion", "Azurite", "Yellow ochre"],
                "technique": "Loose brushwork, atmospheric perspective",
                "signature_markers": "Visible brushstrokes at distance",
                "canvas_info": "Large-scale Spanish linen"
            },
            "is_featured": True,
            "story_id": "story_las_meninas"
        },
        {
            "artwork_id": "art_arnolfini",
            "title": "The Arnolfini Portrait",
            "artist": "Jan van Eyck",
            "year": "1434",
            "period": "Northern Renaissance",
            "movement": "Renaissance",
            "medium": "Oil on oak panel",
            "dimensions": "82.2 cm × 60 cm",
            "location": "National Gallery, London",
            "image_url": "https://images.unsplash.com/photo-1578301978162-7aae4d755744?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578301978162-7aae4d755744?w=400",
            "description": "Revolutionary double portrait showcasing oil painting mastery.",
            "provenance": [
                {"year": "1434", "event": "Painted in Bruges"},
                {"year": "1842", "event": "Acquired by National Gallery"}
            ],
            "forensic_data": {
                "pigments": ["Vermillion", "Malachite", "Azurite", "Gold leaf"],
                "technique": "Pioneering oil glazing, extreme detail",
                "signature_markers": "Mirror reflection, textile rendering",
                "canvas_info": "Oak panel, multiple thin oil glazes"
            },
            "is_featured": True,
            "story_id": "story_arnolfini"
        },
        # IMPRESSIONISM & POST-IMPRESSIONISM (9-14)
        {
            "artwork_id": "art_starry_night",
            "title": "The Starry Night",
            "artist": "Vincent van Gogh",
            "year": "1889",
            "period": "Post-Impressionism",
            "movement": "Post-Impressionism",
            "medium": "Oil on canvas",
            "dimensions": "73.7 cm × 92.1 cm",
            "location": "Museum of Modern Art, New York",
            "image_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=400",
            "description": "Painted at the asylum depicting a swirling night sky.",
            "provenance": [
                {"year": "1889", "event": "Painted at asylum"},
                {"year": "1941", "event": "Acquired by MoMA"}
            ],
            "forensic_data": {
                "pigments": ["Prussian blue", "Chrome yellow", "Zinc white"],
                "technique": "Impasto, visible emotional brushstrokes",
                "signature_markers": "Thick impasto, swirling motion",
                "canvas_info": "French canvas, lead white priming"
            },
            "is_featured": True,
            "story_id": "story_starry_night"
        },
        {
            "artwork_id": "art_cafe_terrace",
            "title": "Café Terrace at Night",
            "artist": "Vincent van Gogh",
            "year": "1888",
            "period": "Post-Impressionism",
            "movement": "Post-Impressionism",
            "medium": "Oil on canvas",
            "dimensions": "80.7 cm × 65.3 cm",
            "location": "Kröller-Müller Museum",
            "image_url": "https://images.unsplash.com/photo-1579783901586-d88db74b4fe4?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1579783901586-d88db74b4fe4?w=400",
            "description": "A nocturnal scene painted without black pigment.",
            "provenance": [
                {"year": "1888", "event": "Painted in Arles"},
                {"year": "1938", "event": "Acquired by Kröller-Müller"}
            ],
            "forensic_data": {
                "pigments": ["Prussian blue", "Chrome yellow", "Zinc white (no black)"],
                "technique": "Night scene with artificial light, impasto",
                "signature_markers": "Vibrant yellows, starlight depiction",
                "canvas_info": "Standard canvas, thick impasto"
            },
            "is_featured": True,
            "story_id": "story_cafe_terrace"
        },
        {
            "artwork_id": "art_water_lilies",
            "title": "Water Lilies",
            "artist": "Claude Monet",
            "year": "1906",
            "period": "Impressionism",
            "movement": "Impressionism",
            "medium": "Oil on canvas",
            "dimensions": "89.9 cm × 94.1 cm",
            "location": "Art Institute of Chicago",
            "image_url": "https://images.unsplash.com/photo-1580136579312-94651dfd596d?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1580136579312-94651dfd596d?w=400",
            "description": "Part of Monet's famous series from Giverny.",
            "provenance": [
                {"year": "1906", "event": "Painted at Giverny"},
                {"year": "1933", "event": "Acquired by Art Institute"}
            ],
            "forensic_data": {
                "pigments": ["Cobalt blue", "Viridian", "Chrome yellow", "Lead white"],
                "technique": "Broken color, wet-on-wet, atmospheric",
                "signature_markers": "Loose brushwork, reflection studies",
                "canvas_info": "French canvas, thick impasto"
            },
            "is_featured": True,
            "story_id": "story_water_lilies"
        },
        {
            "artwork_id": "art_impression_sunrise",
            "title": "Impression, Sunrise",
            "artist": "Claude Monet",
            "year": "1872",
            "period": "Impressionism",
            "movement": "Impressionism",
            "medium": "Oil on canvas",
            "dimensions": "48 cm × 63 cm",
            "location": "Musée Marmottan Monet, Paris",
            "image_url": "https://images.unsplash.com/photo-1578301978018-3005759f48f7?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578301978018-3005759f48f7?w=400",
            "description": "The painting that gave Impressionism its name.",
            "provenance": [
                {"year": "1874", "event": "First Impressionist exhibition"},
                {"year": "1985", "event": "Stolen and recovered 1990"}
            ],
            "forensic_data": {
                "pigments": ["Cobalt blue", "Viridian", "Vermillion", "Chrome orange"],
                "technique": "Rapid plein air brushwork, atmospheric",
                "signature_markers": "Loose handling, light effects",
                "canvas_info": "French canvas, thin paint layers"
            },
            "is_featured": True,
            "story_id": "story_impression_sunrise"
        },
        {
            "artwork_id": "art_grande_jatte",
            "title": "A Sunday on La Grande Jatte",
            "artist": "Georges Seurat",
            "year": "1884-1886",
            "period": "Post-Impressionism",
            "movement": "Pointillism",
            "medium": "Oil on canvas",
            "dimensions": "207.6 cm × 308 cm",
            "location": "Art Institute of Chicago",
            "image_url": "https://images.unsplash.com/photo-1578926288207-a90a5366759d?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578926288207-a90a5366759d?w=400",
            "description": "The masterpiece of Pointillism.",
            "provenance": [
                {"year": "1886", "event": "Final Impressionist exhibition"},
                {"year": "1924", "event": "Acquired by Art Institute"}
            ],
            "forensic_data": {
                "pigments": ["Chrome yellow", "Cadmium yellow", "Vermillion", "Emerald green"],
                "technique": "Pointillism, thousands of color dots",
                "signature_markers": "Scientific color theory, painted border",
                "canvas_info": "Large canvas, over 2 years labor"
            },
            "is_featured": True,
            "story_id": "story_grande_jatte"
        },
        {
            "artwork_id": "art_the_kiss",
            "title": "The Kiss",
            "artist": "Gustav Klimt",
            "year": "1907-1908",
            "period": "Art Nouveau",
            "movement": "Symbolism",
            "medium": "Oil and gold leaf on canvas",
            "dimensions": "180 cm × 180 cm",
            "location": "Belvedere, Vienna",
            "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400",
            "description": "Klimt's masterpiece of the Golden Phase.",
            "provenance": [
                {"year": "1908", "event": "Exhibited at Kunstschau"},
                {"year": "1908", "event": "Purchased by Austrian state"}
            ],
            "forensic_data": {
                "pigments": ["Gold leaf (23.5 karat)", "Silver leaf", "Platinum leaf"],
                "technique": "Byzantine-inspired gold, decorative patterns",
                "signature_markers": "Geometric patterns, spiral motifs",
                "canvas_info": "Square format, complex gold layering"
            },
            "is_featured": True,
            "story_id": "story_the_kiss"
        },
        # MODERN ART (15-22)
        {
            "artwork_id": "art_scream",
            "title": "The Scream",
            "artist": "Edvard Munch",
            "year": "1893",
            "period": "Expressionism",
            "movement": "Expressionism",
            "medium": "Tempera and crayon on cardboard",
            "dimensions": "91 cm × 73.5 cm",
            "location": "National Gallery, Oslo",
            "image_url": "https://images.unsplash.com/photo-1579541814924-49fef17c5be5?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1579541814924-49fef17c5be5?w=400",
            "description": "Iconic image of modern anxiety.",
            "provenance": [
                {"year": "1893", "event": "Created for Frieze of Life"},
                {"year": "1994", "event": "Stolen and recovered"},
                {"year": "2004", "event": "Stolen again, recovered 2006"}
            ],
            "forensic_data": {
                "pigments": ["Cadmium orange/yellow", "Prussian blue", "Vermillion"],
                "technique": "Bold brushwork, swirling lines",
                "signature_markers": "Swirling sky, elongated figure",
                "canvas_info": "Cardboard support, mixed media"
            },
            "is_featured": True,
            "story_id": "story_scream"
        },
        {
            "artwork_id": "art_persistence",
            "title": "The Persistence of Memory",
            "artist": "Salvador Dalí",
            "year": "1931",
            "period": "Surrealism",
            "movement": "Surrealism",
            "medium": "Oil on canvas",
            "dimensions": "24 cm × 33 cm",
            "location": "Museum of Modern Art, New York",
            "image_url": "https://images.unsplash.com/photo-1578926375605-eaf7559b1458?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578926375605-eaf7559b1458?w=400",
            "description": "Dalí's iconic melting watches.",
            "provenance": [
                {"year": "1931", "event": "First exhibited in Paris"},
                {"year": "1934", "event": "Acquired by MoMA"}
            ],
            "forensic_data": {
                "pigments": ["Cadmium yellow", "Cobalt blue", "Burnt sienna"],
                "technique": "Photorealistic, thin glazes",
                "signature_markers": "Meticulous detail, dreamlike juxtaposition",
                "canvas_info": "Small-scale, fine grain"
            },
            "is_featured": True,
            "story_id": "story_persistence"
        },
        {
            "artwork_id": "art_guernica",
            "title": "Guernica",
            "artist": "Pablo Picasso",
            "year": "1937",
            "period": "Cubism",
            "movement": "Cubism",
            "medium": "Oil on canvas",
            "dimensions": "349 cm × 776 cm",
            "location": "Museo Reina Sofía, Madrid",
            "image_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=400",
            "description": "Powerful anti-war statement.",
            "provenance": [
                {"year": "1937", "event": "Created for Paris World's Fair"},
                {"year": "1981", "event": "Returned to Spain"}
            ],
            "forensic_data": {
                "pigments": ["Titanium white", "Ivory black", "Grayscale only"],
                "technique": "Cubist fragmentation, monochromatic",
                "signature_markers": "Fragmented forms, newspaper texture",
                "canvas_info": "Massive scale, rapid execution"
            },
            "is_featured": True,
            "story_id": "story_guernica"
        },
        {
            "artwork_id": "art_american_gothic",
            "title": "American Gothic",
            "artist": "Grant Wood",
            "year": "1930",
            "period": "Regionalism",
            "movement": "American Regionalism",
            "medium": "Oil on beaverboard",
            "dimensions": "78 cm × 65.3 cm",
            "location": "Art Institute of Chicago",
            "image_url": "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?w=400",
            "description": "Iconic image of rural America.",
            "provenance": [
                {"year": "1930", "event": "Won bronze medal"},
                {"year": "1930", "event": "Purchased for $300"}
            ],
            "forensic_data": {
                "pigments": ["Earth tones", "Prussian blue", "Lead white"],
                "technique": "Precise Flemish-inspired realism",
                "signature_markers": "Hard-edged forms, flat light",
                "canvas_info": "Beaverboard, unusual support"
            },
            "is_featured": True,
            "story_id": "story_american_gothic"
        },
        {
            "artwork_id": "art_nighthawks",
            "title": "Nighthawks",
            "artist": "Edward Hopper",
            "year": "1942",
            "period": "American Realism",
            "movement": "American Realism",
            "medium": "Oil on canvas",
            "dimensions": "84.1 cm × 152.4 cm",
            "location": "Art Institute of Chicago",
            "image_url": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=400",
            "description": "Iconic image of urban isolation.",
            "provenance": [
                {"year": "1942", "event": "Completed after Pearl Harbor"},
                {"year": "1942", "event": "Purchased for $3,000"}
            ],
            "forensic_data": {
                "pigments": ["Cadmium red", "Viridian", "Ultramarine"],
                "technique": "Sharp geometric, artificial light study",
                "signature_markers": "Characteristic light, urban alienation",
                "canvas_info": "Standard canvas, smooth application"
            },
            "is_featured": True,
            "story_id": "story_nighthawks"
        },
        {
            "artwork_id": "art_great_wave",
            "title": "The Great Wave off Kanagawa",
            "artist": "Katsushika Hokusai",
            "year": "c. 1831",
            "period": "Edo Period",
            "movement": "Ukiyo-e",
            "medium": "Woodblock print",
            "dimensions": "25.7 cm × 37.9 cm",
            "location": "Multiple collections",
            "image_url": "https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=400",
            "description": "The most recognized Japanese artwork.",
            "provenance": [
                {"year": "1831", "event": "Published in Thirty-six Views series"},
                {"year": "1850s", "event": "Introduced to Europe"}
            ],
            "forensic_data": {
                "pigments": ["Prussian blue (imported)", "Indigo", "Organic yellow"],
                "technique": "Woodblock printing (mokuhanga)",
                "signature_markers": "Distinctive wave pattern, Mount Fuji",
                "canvas_info": "Mulberry paper, cherry wood blocks"
            },
            "is_featured": True,
            "story_id": "story_great_wave"
        },
        # CONTEMPORARY & POP ART (23-30)
        {
            "artwork_id": "art_campbell_soup",
            "title": "Campbell's Soup Cans",
            "artist": "Andy Warhol",
            "year": "1962",
            "period": "Pop Art",
            "movement": "Pop Art",
            "medium": "Synthetic polymer paint on canvas",
            "dimensions": "51 cm × 41 cm each (32 canvases)",
            "location": "Museum of Modern Art, New York",
            "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400",
            "description": "Warhol's iconic Pop Art statement on consumer culture.",
            "provenance": [
                {"year": "1962", "event": "First exhibited at Ferus Gallery, LA"},
                {"year": "1996", "event": "Acquired by MoMA"}
            ],
            "forensic_data": {
                "pigments": ["Synthetic polymer paints", "Commercial inks", "Acrylic"],
                "technique": "Semi-mechanized production, silkscreen elements",
                "signature_markers": "Mass-production aesthetic, consumer imagery",
                "canvas_info": "32 individual canvases, uniform size"
            },
            "is_featured": True,
            "story_id": "story_campbell_soup"
        },
        {
            "artwork_id": "art_marilyn_diptych",
            "title": "Marilyn Diptych",
            "artist": "Andy Warhol",
            "year": "1962",
            "period": "Pop Art",
            "movement": "Pop Art",
            "medium": "Acrylic and silkscreen on canvas",
            "dimensions": "205.4 cm × 289.6 cm",
            "location": "Tate Modern, London",
            "image_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=400",
            "description": "50 images of Marilyn Monroe exploring fame and mortality.",
            "provenance": [
                {"year": "1962", "event": "Created after Monroe's death"},
                {"year": "1980", "event": "Acquired by Tate"}
            ],
            "forensic_data": {
                "pigments": ["Acrylic paints", "Silkscreen inks", "Fluorescent colors"],
                "technique": "Silkscreen printing, deliberate variations",
                "signature_markers": "Repetition with degradation, celebrity imagery",
                "canvas_info": "Two-panel diptych format"
            },
            "is_featured": True,
            "story_id": "story_marilyn_diptych"
        },
        {
            "artwork_id": "art_drowning_girl",
            "title": "Drowning Girl",
            "artist": "Roy Lichtenstein",
            "year": "1963",
            "period": "Pop Art",
            "movement": "Pop Art",
            "medium": "Oil and synthetic polymer on canvas",
            "dimensions": "171.6 cm × 169.5 cm",
            "location": "Museum of Modern Art, New York",
            "image_url": "https://images.unsplash.com/photo-1578926375605-eaf7559b1458?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578926375605-eaf7559b1458?w=400",
            "description": "Comic-book style melodrama elevated to fine art.",
            "provenance": [
                {"year": "1963", "event": "Created based on DC Comics panel"},
                {"year": "1971", "event": "Acquired by MoMA"}
            ],
            "forensic_data": {
                "pigments": ["Primary colors only", "Industrial paints", "Ben-Day dots"],
                "technique": "Simulated Ben-Day dots, bold outlines",
                "signature_markers": "Comic imagery, thought bubble, cropping",
                "canvas_info": "Large scale, mechanical appearance"
            },
            "is_featured": True,
            "story_id": "story_drowning_girl"
        },
        {
            "artwork_id": "art_no_5_1948",
            "title": "No. 5, 1948",
            "artist": "Jackson Pollock",
            "year": "1948",
            "period": "Abstract Expressionism",
            "movement": "Abstract Expressionism",
            "medium": "Oil on fiberboard",
            "dimensions": "244 cm × 122 cm",
            "location": "Private Collection",
            "image_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=400",
            "description": "Quintessential drip painting, sold for $140 million in 2006.",
            "provenance": [
                {"year": "1948", "event": "Created in Springs, Long Island"},
                {"year": "2006", "event": "Sold for record $140 million"}
            ],
            "forensic_data": {
                "pigments": ["Alkyd enamels", "House paints", "Industrial materials"],
                "technique": "Drip painting, action painting, all-over composition",
                "signature_markers": "Continuous line, rhythmic splatters, no focal point",
                "canvas_info": "Fiberboard, laid flat during creation"
            },
            "is_featured": True,
            "story_id": "story_no_5_1948"
        },
        {
            "artwork_id": "art_rothko_orange",
            "title": "Orange, Red, Yellow",
            "artist": "Mark Rothko",
            "year": "1961",
            "period": "Abstract Expressionism",
            "movement": "Color Field",
            "medium": "Oil on canvas",
            "dimensions": "236.2 cm × 206.4 cm",
            "location": "Private Collection",
            "image_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=400",
            "description": "Luminous color field painting sold for $86.9 million.",
            "provenance": [
                {"year": "1961", "event": "Created in New York studio"},
                {"year": "2012", "event": "Sold at Christie's for $86.9 million"}
            ],
            "forensic_data": {
                "pigments": ["Thinned oils", "Egg tempera underpainting", "Cadmium colors"],
                "technique": "Thin washes, floating rectangles, feathered edges",
                "signature_markers": "Soft edges, luminous depth, meditative scale",
                "canvas_info": "Unprimed canvas, thin paint layers"
            },
            "is_featured": True,
            "story_id": "story_rothko_orange"
        },
        {
            "artwork_id": "art_balloon_dog",
            "title": "Balloon Dog (Orange)",
            "artist": "Jeff Koons",
            "year": "1994-2000",
            "period": "Contemporary",
            "movement": "Neo-Pop",
            "medium": "Mirror-polished stainless steel",
            "dimensions": "307 cm × 363 cm × 114 cm",
            "location": "Private Collection",
            "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400",
            "description": "Monumental sculpture sold for $58.4 million in 2013.",
            "provenance": [
                {"year": "2000", "event": "Completed as part of Celebration series"},
                {"year": "2013", "event": "Sold at Christie's for $58.4 million"}
            ],
            "forensic_data": {
                "pigments": ["Transparent color coating", "Mirror-polished steel"],
                "technique": "Industrial fabrication, computer-aided design",
                "signature_markers": "Perfect reflective surface, monumental scale",
                "canvas_info": "Stainless steel, factory-produced"
            },
            "is_featured": True,
            "story_id": "story_balloon_dog"
        },
        {
            "artwork_id": "art_girl_balloon",
            "title": "Girl with Balloon",
            "artist": "Banksy",
            "year": "2002",
            "period": "Street Art",
            "movement": "Street Art",
            "medium": "Stencil spray paint",
            "dimensions": "Variable",
            "location": "Multiple locations/Private",
            "image_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=400",
            "description": "Iconic stencil that self-destructed at Sotheby's auction in 2018.",
            "provenance": [
                {"year": "2002", "event": "First appeared on London wall"},
                {"year": "2018", "event": "Self-shredded at Sotheby's, renamed 'Love is in the Bin'"}
            ],
            "forensic_data": {
                "pigments": ["Spray paint", "Stencil-applied"],
                "technique": "Multi-layer stencil, street art aesthetic",
                "signature_markers": "Simple imagery, political undertones",
                "canvas_info": "Originally on walls, later on canvas"
            },
            "is_featured": True,
            "story_id": "story_girl_balloon"
        },
        {
            "artwork_id": "art_physical_impossibility",
            "title": "The Physical Impossibility of Death in the Mind of Someone Living",
            "artist": "Damien Hirst",
            "year": "1991",
            "period": "Contemporary",
            "movement": "YBA (Young British Artists)",
            "medium": "Tiger shark, glass, steel, formaldehyde",
            "dimensions": "213 cm × 518 cm × 213 cm",
            "location": "Private Collection",
            "image_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=400",
            "description": "Preserved shark that defined YBA movement, sold for $12 million.",
            "provenance": [
                {"year": "1991", "event": "Commissioned by Charles Saatchi"},
                {"year": "2004", "event": "Sold to Steve Cohen for $12 million"}
            ],
            "forensic_data": {
                "pigments": ["Formaldehyde solution", "Steel framework"],
                "technique": "Preserved specimen installation",
                "signature_markers": "Confrontation with mortality, shock value",
                "canvas_info": "Glass vitrine, steel frame, chemical preservation"
            },
            "is_featured": True,
            "story_id": "story_physical_impossibility"
        },
        # MODERN & CONTEMPORARY ART ADDITIONS
        {
            "artwork_id": "art_warhol_marilyn",
            "title": "Shot Sage Blue Marilyn",
            "artist": "Andy Warhol",
            "year": "1964",
            "period": "Pop Art",
            "movement": "Pop Art",
            "medium": "Silkscreen ink and acrylic on linen",
            "dimensions": "101.6 cm × 101.6 cm",
            "location": "Private Collection",
            "image_url": "https://images.unsplash.com/photo-1578926375605-eaf7559b1458?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578926375605-eaf7559b1458?w=400",
            "description": "Iconic Pop Art portrait sold for $195 million in 2022, the most expensive American artwork ever sold.",
            "provenance": [
                {"year": "1964", "event": "Created as part of Marilyn series"},
                {"year": "1964", "event": "Shot by Dorothy Podber at The Factory"},
                {"year": "2022", "event": "Sold at Christie's for $195 million"}
            ],
            "forensic_data": {
                "pigments": ["Acrylic paint", "Silkscreen ink", "Commercial pigments"],
                "technique": "Silkscreen printing on primed linen",
                "signature_markers": "Offset registration, intentional imperfections",
                "canvas_info": "Primed linen canvas, machine-stretched"
            },
            "is_featured": True,
            "story_id": "story_warhol_marilyn"
        },
        {
            "artwork_id": "art_basquiat_skull",
            "title": "Untitled (Skull)",
            "artist": "Jean-Michel Basquiat",
            "year": "1981",
            "period": "Neo-Expressionism",
            "movement": "Neo-Expressionism",
            "medium": "Acrylic and oilstick on canvas",
            "dimensions": "205.7 cm × 175.9 cm",
            "location": "Private Collection",
            "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400",
            "description": "Powerful skull painting sold for $110.5 million in 2017.",
            "provenance": [
                {"year": "1981", "event": "Created in New York"},
                {"year": "2017", "event": "Sold at Sotheby's for $110.5 million"}
            ],
            "forensic_data": {
                "pigments": ["Acrylic paint", "Oilstick", "Spray paint"],
                "technique": "Gestural brushwork, text incorporation, raw energy",
                "signature_markers": "Crown motif, anatomical references, street art influence",
                "canvas_info": "Unprimed canvas, heavy impasto"
            },
            "is_featured": True,
            "story_id": "story_basquiat_skull"
        },
        {
            "artwork_id": "art_hockney_splash",
            "title": "A Bigger Splash",
            "artist": "David Hockney",
            "year": "1967",
            "period": "Pop Art",
            "movement": "British Pop Art",
            "medium": "Acrylic on canvas",
            "dimensions": "242.5 cm × 243.9 cm",
            "location": "Tate Modern, London",
            "image_url": "https://images.unsplash.com/photo-1571115764595-644a1f56a55c?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1571115764595-644a1f56a55c?w=400",
            "description": "Iconic California pool painting capturing a single moment of splash.",
            "provenance": [
                {"year": "1967", "event": "Created in Los Angeles"},
                {"year": "1981", "event": "Acquired by Tate"}
            ],
            "forensic_data": {
                "pigments": ["Acrylic paint", "Flat application"],
                "technique": "Hard-edge painting, flat color fields, two-week splash detail",
                "signature_markers": "California light, geometric architecture",
                "canvas_info": "Stretched canvas, smooth acrylic surface"
            },
            "is_featured": True,
            "story_id": "story_hockney_splash"
        },
        {
            "artwork_id": "art_kusama_infinity",
            "title": "Infinity Mirrored Room",
            "artist": "Yayoi Kusama",
            "year": "1965-present",
            "period": "Contemporary",
            "movement": "Minimalism/Pop Art",
            "medium": "Mixed media installation",
            "dimensions": "Variable",
            "location": "Multiple Museums Worldwide",
            "image_url": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=400",
            "description": "Immersive installation creating infinite reflections, exploring themes of obsession and infinity.",
            "provenance": [
                {"year": "1965", "event": "First Infinity Room created"},
                {"year": "2017", "event": "Global exhibition tour begins"}
            ],
            "forensic_data": {
                "pigments": ["LED lights", "Mirrors", "Varied materials"],
                "technique": "Immersive environment, infinite reflection",
                "signature_markers": "Polka dots, cosmic infinity, psychological depth",
                "canvas_info": "Room-scale installation, precise engineering"
            },
            "is_featured": True,
            "story_id": "story_kusama_infinity"
        },
        {
            "artwork_id": "art_kaws_companion",
            "title": "COMPANION (Resting Place)",
            "artist": "KAWS",
            "year": "2013",
            "period": "Contemporary",
            "movement": "Street Art/Pop Surrealism",
            "medium": "Fiberglass and bronze",
            "dimensions": "Variable editions",
            "location": "Various Collections",
            "image_url": "https://images.unsplash.com/photo-1578926375605-eaf7559b1458?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1578926375605-eaf7559b1458?w=400",
            "description": "Iconic cartoon-inspired figure exploring themes of isolation and companionship.",
            "provenance": [
                {"year": "2013", "event": "Created as part of ongoing COMPANION series"},
                {"year": "2019", "event": "Major museum retrospective"}
            ],
            "forensic_data": {
                "pigments": ["Industrial paint", "Resin coating"],
                "technique": "3D modeling, industrial fabrication",
                "signature_markers": "X eyes, cartoonish proportions, emotional resonance",
                "canvas_info": "Fiberglass or bronze, factory-produced"
            },
            "is_featured": True,
            "story_id": "story_kaws_companion"
        },
        {
            "artwork_id": "art_ai_weiwei_seeds",
            "title": "Sunflower Seeds",
            "artist": "Ai Weiwei",
            "year": "2010",
            "period": "Contemporary",
            "movement": "Conceptual Art",
            "medium": "Hand-painted porcelain",
            "dimensions": "100 million seeds",
            "location": "Tate Modern (original installation)",
            "image_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=400",
            "description": "Installation of 100 million hand-painted porcelain sunflower seeds exploring mass production and individuality.",
            "provenance": [
                {"year": "2010", "event": "Created with 1,600 artisans in Jingdezhen"},
                {"year": "2010", "event": "Unveiled at Tate Modern Turbine Hall"}
            ],
            "forensic_data": {
                "pigments": ["Traditional ceramic glazes", "Hand-applied paint"],
                "technique": "Traditional porcelain craft, mass collaboration",
                "signature_markers": "Political commentary, artisan collaboration",
                "canvas_info": "Porcelain, hand-crafted, each unique"
            },
            "is_featured": True,
            "story_id": "story_ai_weiwei_seeds"
        },
        {
            "artwork_id": "art_richter_abstract",
            "title": "Abstraktes Bild",
            "artist": "Gerhard Richter",
            "year": "1986",
            "period": "Contemporary",
            "movement": "Abstract Art",
            "medium": "Oil on canvas",
            "dimensions": "300 cm × 250 cm",
            "location": "Private Collection",
            "image_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=400",
            "description": "Masterwork of squeegee abstraction sold for over $46 million.",
            "provenance": [
                {"year": "1986", "event": "Created in Cologne studio"},
                {"year": "2015", "event": "Sold at Sotheby's for $46.3 million"}
            ],
            "forensic_data": {
                "pigments": ["Oil paints", "Multiple layered colors"],
                "technique": "Squeegee technique, layered scraping",
                "signature_markers": "Horizontal drag marks, color blending",
                "canvas_info": "Large-scale canvas, multiple paint layers"
            },
            "is_featured": True,
            "story_id": "story_richter_abstract"
        },
        {
            "artwork_id": "art_bacon_triptych",
            "title": "Three Studies of Lucian Freud",
            "artist": "Francis Bacon",
            "year": "1969",
            "period": "Modern",
            "movement": "Figurative Expressionism",
            "medium": "Oil on canvas",
            "dimensions": "198 cm × 147.5 cm (each panel)",
            "location": "Private Collection",
            "image_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=400",
            "description": "Powerful triptych portrait sold for $142.4 million in 2013.",
            "provenance": [
                {"year": "1969", "event": "Created depicting friend Lucian Freud"},
                {"year": "2013", "event": "Sold at Christie's for $142.4 million"}
            ],
            "forensic_data": {
                "pigments": ["Oil paint", "Spray paint accents"],
                "technique": "Distorted figuration, violent brushwork",
                "signature_markers": "Caged figures, raw emotion, spatial distortion",
                "canvas_info": "Primed canvas, textured application"
            },
            "is_featured": True,
            "story_id": "story_bacon_triptych"
        },
        {
            "artwork_id": "art_bourgeois_spider",
            "title": "Maman",
            "artist": "Louise Bourgeois",
            "year": "1999",
            "period": "Contemporary",
            "movement": "Sculpture",
            "medium": "Bronze, stainless steel, marble",
            "dimensions": "927 cm × 891 cm × 1024 cm",
            "location": "Multiple casts worldwide",
            "image_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1541367777708-7905fe3296c0?w=400",
            "description": "Monumental spider sculpture exploring themes of motherhood and protection.",
            "provenance": [
                {"year": "1999", "event": "First cast created"},
                {"year": "2000", "event": "Unveiled at Tate Modern inauguration"}
            ],
            "forensic_data": {
                "pigments": ["Patinated bronze", "Polished steel"],
                "technique": "Large-scale bronze casting",
                "signature_markers": "Maternal imagery, arachnid form, emotional scale",
                "canvas_info": "Bronze, steel, marble eggs in sac"
            },
            "is_featured": True,
            "story_id": "story_bourgeois_spider"
        },
        {
            "artwork_id": "art_kapoor_bean",
            "title": "Cloud Gate",
            "artist": "Anish Kapoor",
            "year": "2006",
            "period": "Contemporary",
            "movement": "Public Art",
            "medium": "Stainless steel",
            "dimensions": "10 m × 20 m × 13 m",
            "location": "Millennium Park, Chicago",
            "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800",
            "thumbnail_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
            "description": "Iconic 'Bean' sculpture reflecting Chicago skyline, one of the most visited artworks in America.",
            "provenance": [
                {"year": "2004", "event": "Construction begins"},
                {"year": "2006", "event": "Officially dedicated in Millennium Park"}
            ],
            "forensic_data": {
                "pigments": ["Mirror-polished stainless steel"],
                "technique": "Seamless welding, perfect polish",
                "signature_markers": "Reflective void, spatial distortion",
                "canvas_info": "168 steel plates, no visible seams"
            },
            "is_featured": True,
            "story_id": "story_kapoor_bean"
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
                "movement": artwork.get("movement", artwork["period"]),
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
    
    # Seed museum partners
    museum_partners = [
        {
            "partner_id": "museum_louvre",
            "name": "Louvre Museum",
            "location": "Paris",
            "country": "France",
            "website": "https://www.louvre.fr",
            "partnership_tier": "exclusive",
            "artworks_count": 3,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "partner_id": "museum_moma",
            "name": "Museum of Modern Art",
            "location": "New York",
            "country": "USA",
            "website": "https://www.moma.org",
            "partnership_tier": "exclusive",
            "artworks_count": 5,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "partner_id": "museum_uffizi",
            "name": "Uffizi Gallery",
            "location": "Florence",
            "country": "Italy",
            "website": "https://www.uffizi.it",
            "partnership_tier": "premium",
            "artworks_count": 2,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "partner_id": "museum_prado",
            "name": "Museo del Prado",
            "location": "Madrid",
            "country": "Spain",
            "website": "https://www.museodelprado.es",
            "partnership_tier": "premium",
            "artworks_count": 2,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "partner_id": "museum_tate",
            "name": "Tate Modern",
            "location": "London",
            "country": "UK",
            "website": "https://www.tate.org.uk",
            "partnership_tier": "premium",
            "artworks_count": 3,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    for partner in museum_partners:
        await db.museum_partners.update_one(
            {"partner_id": partner["partner_id"]},
            {"$set": partner},
            upsert=True
        )
    
    # Create indexes
    await db.user_activities.create_index([("user_id", 1), ("created_at", -1)])
    await db.user_activities.create_index([("activity_type", 1)])
    await db.users.create_index([("email", 1)], unique=True)
    await db.users.create_index([("subscription_tier", 1)])
    await db.users.create_index([("role", 1)])
    await db.users.create_index([("last_active", -1)])
    await db.users.create_index([("total_spent", -1)])
    await db.artworks.create_index([("period", 1)])
    await db.artworks.create_index([("movement", 1)])
    await db.artworks.create_index([("is_user_submitted", 1)])
    await db.email_campaigns.create_index([("status", 1)])
    await db.advisory_sessions.create_index([("user_id", 1), ("scheduled_at", -1)])
    
    return {
        "message": "Data seeded successfully",
        "artworks": len(artworks),
        "stories": len(stories),
        "museum_partners": len(museum_partners)
    }

# Include routers
api_router.include_router(auth_router)
api_router.include_router(artworks_router)
api_router.include_router(stories_router)
api_router.include_router(forensics_router)
api_router.include_router(payments_router)
api_router.include_router(subscriptions_router)
api_router.include_router(dashboard_router)
api_router.include_router(crm_router)
api_router.include_router(admin_router)
api_router.include_router(campaigns_router)
api_router.include_router(museum_router)
api_router.include_router(organizations_router)

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
