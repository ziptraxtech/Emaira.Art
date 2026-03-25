"""
Test suite for Emaira.Art P0 Business Upgrades
Tests: Subscriptions API (5 tiers), VR Narrative, Enhanced Forensics, Modern Art Categories
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestSubscriptionsAPI:
    """Test Subscriptions API - should return 5 tiers including Collector's Advisory"""
    
    def test_subscriptions_returns_5_tiers(self):
        """Subscriptions endpoint should return exactly 5 tiers"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/")
        assert response.status_code == 200
        data = response.json()
        
        assert "tiers" in data
        tiers = data["tiers"]
        assert len(tiers) == 5, f"Expected 5 tiers, got {len(tiers)}"
        print(f"✓ Subscriptions API returns {len(tiers)} tiers")
        
    def test_subscriptions_tier_ids(self):
        """All expected tier IDs should be present"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/")
        assert response.status_code == 200
        tiers = response.json()["tiers"]
        
        tier_ids = [t["tier_id"] for t in tiers]
        expected_ids = ["short_story", "deep_dive", "connoisseur", "pro_collector", "collectors_advisory"]
        
        for expected_id in expected_ids:
            assert expected_id in tier_ids, f"Missing tier: {expected_id}"
        print(f"✓ All 5 tier IDs present: {tier_ids}")
        
    def test_collectors_advisory_tier_details(self):
        """Collector's Advisory tier should have correct price and features"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/")
        assert response.status_code == 200
        tiers = response.json()["tiers"]
        
        advisory_tier = next((t for t in tiers if t["tier_id"] == "collectors_advisory"), None)
        assert advisory_tier is not None, "Collector's Advisory tier not found"
        
        assert advisory_tier["price"] == 2499.0, f"Expected price $2499, got ${advisory_tier['price']}"
        assert advisory_tier["period"] == "year"
        assert "Collector's Advisory" in advisory_tier["name"]
        
        # Check for key features
        features = " ".join(advisory_tier.get("features", []))
        assert "advisory" in features.lower() or "consultation" in features.lower()
        print(f"✓ Collector's Advisory tier: ${advisory_tier['price']}/year with {len(advisory_tier['features'])} features")


class TestSubscriptionTierEndpoint:
    """Test individual subscription tier endpoint"""
    
    def test_connoisseur_tier_details(self):
        """GET /api/subscriptions/connoisseur should return tier details"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/connoisseur")
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Annual Connoisseur"
        assert data["price"] == 249.0
        assert data["period"] == "year"
        assert "features" in data
        assert len(data["features"]) >= 3
        print(f"✓ Connoisseur tier: ${data['price']}/year")
        
    def test_invalid_tier_returns_404(self):
        """Invalid tier ID should return 404"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/invalid_tier")
        assert response.status_code == 404
        print("✓ Invalid tier returns 404")


class TestVRNarrativeAPI:
    """Test VR Narrative endpoint"""
    
    def test_vr_narrative_for_mona_lisa(self):
        """GET /api/vr/narrative/art_mona_lisa should return VR narrative with scenes"""
        response = requests.get(f"{BASE_URL}/api/vr/narrative/art_mona_lisa")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "narrative_id" in data
        assert "artwork_id" in data
        assert data["artwork_id"] == "art_mona_lisa"
        assert "title" in data
        assert "scenes" in data
        
        # Check scenes structure
        scenes = data["scenes"]
        assert isinstance(scenes, list)
        assert len(scenes) >= 3, f"Expected at least 3 scenes, got {len(scenes)}"
        
        # Check scene structure
        for scene in scenes:
            assert "scene" in scene or "title" in scene
            assert "narration" in scene
        
        print(f"✓ VR Narrative for Mona Lisa: {len(scenes)} scenes")
        
    def test_vr_narrative_has_forensic_content(self):
        """VR narrative should include forensic content"""
        response = requests.get(f"{BASE_URL}/api/vr/narrative/art_mona_lisa")
        assert response.status_code == 200
        data = response.json()
        
        # Check for forensic content
        if "forensic_content" in data:
            forensic = data["forensic_content"]
            assert isinstance(forensic, dict)
            print(f"✓ Forensic content present with keys: {list(forensic.keys())}")
        else:
            # Forensic content may be in scenes
            scenes_text = str(data.get("scenes", []))
            assert "forensic" in scenes_text.lower() or "pigment" in scenes_text.lower()
            print("✓ Forensic content found in scenes")
            
    def test_vr_narrative_invalid_artwork_returns_404(self):
        """Invalid artwork ID should return 404"""
        response = requests.get(f"{BASE_URL}/api/vr/narrative/invalid_artwork_id")
        assert response.status_code == 404
        print("✓ Invalid artwork returns 404 for VR narrative")


class TestForensicsReportAPI:
    """Test Enhanced Forensics Report endpoint (requires auth)"""
    
    def test_forensics_report_requires_auth(self):
        """GET /api/forensics/report/{artwork_id} should require authentication"""
        response = requests.get(f"{BASE_URL}/api/forensics/report/art_mona_lisa")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "authenticated" in data["detail"].lower() or "not authenticated" in data["detail"].lower()
        print("✓ Forensics report correctly requires authentication")


class TestArtworksCount:
    """Test that artworks collection has 38 total artworks"""
    
    def test_artworks_count_is_38(self):
        """Should return 38 artworks total"""
        response = requests.get(f"{BASE_URL}/api/artworks/?limit=100")
        assert response.status_code == 200
        artworks = response.json()
        
        assert len(artworks) == 38, f"Expected 38 artworks, got {len(artworks)}"
        print(f"✓ Total artworks: {len(artworks)}")
        
    def test_artworks_have_diverse_periods(self):
        """Artworks should span multiple periods"""
        response = requests.get(f"{BASE_URL}/api/artworks/?limit=100")
        assert response.status_code == 200
        artworks = response.json()
        
        periods = set(a.get("period") for a in artworks)
        assert len(periods) >= 10, f"Expected at least 10 periods, got {len(periods)}"
        print(f"✓ Artworks span {len(periods)} different periods")


class TestArtworkPeriods:
    """Test artwork periods including modern art categories"""
    
    def test_periods_include_modern_art(self):
        """Periods should include Pop Art, Contemporary, Neo-Expressionism"""
        response = requests.get(f"{BASE_URL}/api/artworks/periods")
        assert response.status_code == 200
        data = response.json()
        
        periods = data.get("periods", [])
        
        # Check for modern art periods
        modern_periods = ["Pop Art", "Contemporary", "Neo-Expressionism"]
        found_modern = [p for p in modern_periods if p in periods]
        
        assert len(found_modern) >= 3, f"Expected all 3 modern periods, found: {found_modern}"
        print(f"✓ Modern art periods found: {found_modern}")
        
    def test_periods_include_street_art(self):
        """Periods should include Street Art"""
        response = requests.get(f"{BASE_URL}/api/artworks/periods")
        assert response.status_code == 200
        periods = response.json().get("periods", [])
        
        assert "Street Art" in periods, "Street Art period not found"
        print("✓ Street Art period found")
        
    def test_periods_include_abstract_expressionism(self):
        """Periods should include Abstract Expressionism"""
        response = requests.get(f"{BASE_URL}/api/artworks/periods")
        assert response.status_code == 200
        periods = response.json().get("periods", [])
        
        assert "Abstract Expressionism" in periods, "Abstract Expressionism period not found"
        print("✓ Abstract Expressionism period found")


class TestAdminRolesAPI:
    """Test Admin Roles endpoint (requires auth)"""
    
    def test_admin_roles_requires_auth(self):
        """GET /api/admin/roles should require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/roles")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        print("✓ Admin roles correctly requires authentication")


class TestCampaignTemplates:
    """Test Campaign Templates endpoint"""
    
    def test_templates_returns_4_templates(self):
        """GET /api/campaigns/templates should return 4 email templates"""
        response = requests.get(f"{BASE_URL}/api/campaigns/templates")
        assert response.status_code == 200
        data = response.json()
        
        assert "templates" in data
        templates = data["templates"]
        assert len(templates) == 4, f"Expected 4 templates, got {len(templates)}"
        
        # Check template IDs
        template_ids = [t["id"] for t in templates]
        expected_ids = ["welcome", "new_artwork", "advisory_reminder", "subscription_expiring"]
        for expected_id in expected_ids:
            assert expected_id in template_ids, f"Missing template: {expected_id}"
        
        print(f"✓ Campaign templates: {template_ids}")


class TestMuseumPartnersAPI:
    """Test Museum Partners endpoint"""
    
    def test_museums_returns_5_partners(self):
        """GET /api/museums/ should return 5 museum partners"""
        response = requests.get(f"{BASE_URL}/api/museums/")
        assert response.status_code == 200
        data = response.json()
        
        assert "partners" in data
        partners = data["partners"]
        assert len(partners) >= 5, f"Expected at least 5 partners, got {len(partners)}"
        
        # Check partner names
        partner_names = [p["name"] for p in partners]
        print(f"✓ Museum partners: {partner_names}")
        
    def test_museums_include_major_institutions(self):
        """Museum partners should include major institutions"""
        response = requests.get(f"{BASE_URL}/api/museums/")
        assert response.status_code == 200
        partners = response.json()["partners"]
        
        partner_names = [p["name"] for p in partners]
        
        # Check for at least some major museums
        major_museums = ["Louvre Museum", "Museum of Modern Art", "The Metropolitan Museum of Art"]
        found_major = [m for m in major_museums if m in partner_names]
        
        assert len(found_major) >= 2, f"Expected at least 2 major museums, found: {found_major}"
        print(f"✓ Major museums found: {found_major}")


class TestPaymentTiers:
    """Test Payment Tiers endpoint (alternative to subscriptions)"""
    
    def test_payment_tiers_endpoint(self):
        """GET /api/payments/tiers should return subscription tiers"""
        response = requests.get(f"{BASE_URL}/api/payments/tiers")
        assert response.status_code == 200
        tiers = response.json()
        
        assert isinstance(tiers, list)
        assert len(tiers) >= 4
        
        tier_ids = [t.get("tier_id") for t in tiers]
        print(f"✓ Payment tiers: {tier_ids}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
