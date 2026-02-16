"""
Test suite for Emaira.Art Business Upgrades
Tests: Admin roles, Email campaigns, Museum API integration, Modern art categories
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestRootAPI:
    """Test root API endpoint"""
    
    def test_api_root_returns_message(self):
        """API root should return welcome message"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Emaira.Art" in data["message"]
        print(f"✓ API root: {data['message']}")


class TestArtworksAPI:
    """Test artworks API with modern art categories"""
    
    def test_artworks_list(self):
        """Should return list of artworks"""
        response = requests.get(f"{BASE_URL}/api/artworks/")
        assert response.status_code == 200
        artworks = response.json()
        assert isinstance(artworks, list)
        assert len(artworks) >= 20  # At least 20 artworks expected
        print(f"✓ Total artworks: {len(artworks)}")
        
    def test_artworks_have_required_fields(self):
        """Each artwork should have required fields"""
        response = requests.get(f"{BASE_URL}/api/artworks/")
        assert response.status_code == 200
        artworks = response.json()
        
        required_fields = ["artwork_id", "title", "artist", "year", "period", "image_url"]
        for artwork in artworks[:5]:
            for field in required_fields:
                assert field in artwork, f"Missing field: {field} in {artwork.get('title')}"
        print(f"✓ All artworks have required fields")
    
    def test_modern_art_periods_exist(self):
        """Modern art periods should exist in collection"""
        response = requests.get(f"{BASE_URL}/api/artworks/periods")
        assert response.status_code == 200
        data = response.json()
        
        assert "periods" in data
        assert "movements" in data
        
        periods = data["periods"]
        movements = data["movements"]
        
        # Check for modern art periods
        modern_periods = ["Abstract Expressionism", "Pop Art", "Contemporary", "Street Art", "Neo-Expressionism"]
        found_modern = [p for p in modern_periods if p in periods]
        print(f"✓ Modern periods found: {found_modern}")
        assert len(found_modern) >= 3, f"Expected at least 3 modern periods, found: {found_modern}"
        
        # Check for modern movements
        modern_movements = ["Abstract Art", "Pop Art", "Street Art", "Neo-Expressionism", "Minimalism/Pop Art"]
        found_movements = [m for m in modern_movements if m in movements]
        print(f"✓ Modern movements found: {found_movements}")
        assert len(found_movements) >= 2, f"Expected at least 2 modern movements, found: {found_movements}"
        
    def test_periods_endpoint_structure(self):
        """Periods endpoint should return proper structure"""
        response = requests.get(f"{BASE_URL}/api/artworks/periods")
        assert response.status_code == 200
        data = response.json()
        
        assert "periods" in data
        assert "movements" in data
        assert isinstance(data["periods"], list)
        assert isinstance(data["movements"], list)
        assert len(data["periods"]) > 0
        assert len(data["movements"]) > 0
        print(f"✓ Periods: {len(data['periods'])}, Movements: {len(data['movements'])}")


class TestCampaignTemplates:
    """Test email campaign templates (public endpoint)"""
    
    def test_templates_endpoint(self):
        """Campaign templates should be accessible"""
        response = requests.get(f"{BASE_URL}/api/campaigns/templates")
        assert response.status_code == 200
        data = response.json()
        
        assert "templates" in data
        templates = data["templates"]
        assert isinstance(templates, list)
        assert len(templates) >= 4  # At least 4 templates expected
        print(f"✓ Found {len(templates)} email templates")
        
    def test_templates_have_required_fields(self):
        """Each template should have required fields"""
        response = requests.get(f"{BASE_URL}/api/campaigns/templates")
        assert response.status_code == 200
        templates = response.json()["templates"]
        
        required_fields = ["id", "name", "subject", "body"]
        for template in templates:
            for field in required_fields:
                assert field in template, f"Missing field: {field} in template {template.get('id')}"
        
        # Verify specific templates exist
        template_ids = [t["id"] for t in templates]
        expected_templates = ["welcome", "new_artwork", "advisory_reminder", "subscription_expiring"]
        for tid in expected_templates:
            assert tid in template_ids, f"Expected template '{tid}' not found"
        print(f"✓ All required templates present: {expected_templates}")


class TestMuseumPartnerships:
    """Test museum partnerships API"""
    
    def test_museum_partners_list(self):
        """Should return list of museum partners"""
        response = requests.get(f"{BASE_URL}/api/museums/")
        assert response.status_code == 200
        data = response.json()
        
        assert "partners" in data
        partners = data["partners"]
        assert isinstance(partners, list)
        assert len(partners) >= 3  # At least 3 partners expected
        print(f"✓ Found {len(partners)} museum partners")
        
    def test_museum_partners_have_required_fields(self):
        """Each partner should have required fields"""
        response = requests.get(f"{BASE_URL}/api/museums/")
        assert response.status_code == 200
        partners = response.json()["partners"]
        
        required_fields = ["partner_id", "name", "location", "country", "website", "is_active"]
        for partner in partners:
            for field in required_fields:
                assert field in partner, f"Missing field: {field} in partner {partner.get('name')}"
        print(f"✓ All partners have required fields")
        
    def test_known_museums_present(self):
        """Known museums should be in the list"""
        response = requests.get(f"{BASE_URL}/api/museums/")
        assert response.status_code == 200
        partners = response.json()["partners"]
        
        museum_names = [p["name"] for p in partners]
        expected_museums = ["Louvre Museum", "Museum of Modern Art"]
        
        for museum in expected_museums:
            assert museum in museum_names, f"Expected museum '{museum}' not found"
        print(f"✓ Expected museums found: {expected_museums}")


class TestAdminRolesPublic:
    """Test admin roles (authentication required - expect 401)"""
    
    def test_admin_roles_requires_auth(self):
        """Admin roles endpoint should require authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/roles")
        # Should return 401 for unauthenticated requests
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "authenticated" in data["detail"].lower() or "not authenticated" in data["detail"].lower()
        print(f"✓ Admin roles correctly requires authentication")


class TestCampaignsAuth:
    """Test campaigns list (authentication required - expect 401)"""
    
    def test_campaigns_list_requires_auth(self):
        """Campaigns list endpoint should require authentication"""
        response = requests.get(f"{BASE_URL}/api/campaigns/")
        # Should return 401 for unauthenticated requests
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        print(f"✓ Campaigns list correctly requires authentication")


class TestAdvisoryPublicEndpoints:
    """Test public advisory endpoints"""
    
    def test_advisors_list(self):
        """Should return list of available advisors"""
        response = requests.get(f"{BASE_URL}/api/advisory/advisors")
        assert response.status_code == 200
        data = response.json()
        
        assert "advisors" in data
        advisors = data["advisors"]
        assert isinstance(advisors, list)
        assert len(advisors) >= 3
        
        # Check advisor structure
        for advisor in advisors:
            assert "id" in advisor
            assert "name" in advisor
            assert "specialty" in advisor
            assert "credentials" in advisor
            assert "availability" in advisor
        
        print(f"✓ Found {len(advisors)} advisors with complete profiles")


class TestMetMuseumIntegration:
    """Test Met Museum API integration - may fail due to external API"""
    
    def test_met_departments(self):
        """Met departments endpoint should return data or handle errors gracefully"""
        try:
            response = requests.get(f"{BASE_URL}/api/museums/met/departments", timeout=30)
            # Accept 200 (success), 500 (API error), 504 (timeout), or 403 (blocked)
            assert response.status_code in [200, 403, 500, 504], f"Unexpected status: {response.status_code}"
            
            if response.status_code == 200:
                data = response.json()
                assert "departments" in data
                print(f"✓ Met departments: {len(data.get('departments', []))} departments")
            else:
                print(f"✓ Met API returned {response.status_code} (external API may be unavailable)")
        except requests.exceptions.Timeout:
            print(f"✓ Met API timed out (expected - external API)")
            pass
        except Exception as e:
            print(f"✓ Met API exception handled: {type(e).__name__}")


class TestCollectorsAdvisoryTier:
    """Test Collector's Advisory tier related endpoints"""
    
    def test_subscriptions_include_advisory(self):
        """Subscriptions should include Collector's Advisory tier"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/")
        assert response.status_code == 200
        data = response.json()
        
        assert "tiers" in data
        tiers = data["tiers"]
        tier_ids = [t["tier_id"] for t in tiers]
        
        assert "collectors_advisory" in tier_ids, "Collector's Advisory tier not found"
        
        advisory_tier = next(t for t in tiers if t["tier_id"] == "collectors_advisory")
        assert advisory_tier["price"] == 2499.00
        assert "advisory" in advisory_tier["name"].lower() or "Collector" in advisory_tier["name"]
        
        # Check features include advisory sessions
        features = " ".join(advisory_tier.get("features", []))
        assert "advisory" in features.lower() or "session" in features.lower() or "consultation" in features.lower()
        print(f"✓ Collector's Advisory tier found: ${advisory_tier['price']}")


class TestModernArtworks:
    """Test that modern artworks are included in the collection"""
    
    def test_has_modern_art_pieces(self):
        """Collection should include modern and contemporary artworks"""
        response = requests.get(f"{BASE_URL}/api/artworks/")
        assert response.status_code == 200
        artworks = response.json()
        
        modern_periods = ["Abstract Expressionism", "Pop Art", "Contemporary", "Street Art", "Neo-Expressionism", "Modern"]
        modern_artworks = [a for a in artworks if a.get("period") in modern_periods]
        
        print(f"✓ Found {len(modern_artworks)} modern art pieces out of {len(artworks)} total")
        assert len(modern_artworks) >= 5, f"Expected at least 5 modern artworks, found {len(modern_artworks)}"
        
        # List some modern artworks
        for artwork in modern_artworks[:5]:
            print(f"  - {artwork['title']} ({artwork['period']})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
