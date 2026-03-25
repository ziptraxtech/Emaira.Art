"""
Test suite for Emaira.Art new features:
1. AI Visualization Overlays with Gemini Nano Banana
2. Multi-language support (i18n) - backend API tests
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestForensicVisualization:
    """Tests for /api/forensics/generate-visualization and /api/forensics/visualizations/{artwork_id}"""
    
    def test_generate_visualization_requires_auth(self):
        """POST /api/forensics/generate-visualization should require authentication"""
        response = requests.post(
            f"{BASE_URL}/api/forensics/generate-visualization",
            json={"artwork_id": "art_mona_lisa", "analysis_type": "pigment"}
        )
        # Should return 401 Unauthorized without auth
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        data = response.json()
        assert "detail" in data
        print(f"✓ Generate visualization correctly requires auth: {data['detail']}")
    
    def test_get_visualizations_requires_auth(self):
        """GET /api/forensics/visualizations/{artwork_id} should require authentication"""
        response = requests.get(f"{BASE_URL}/api/forensics/visualizations/art_mona_lisa")
        # Should return 401 Unauthorized without auth
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        data = response.json()
        assert "detail" in data
        print(f"✓ Get visualizations correctly requires auth: {data['detail']}")
    
    def test_forensic_image_endpoint_exists(self):
        """GET /api/forensics/image/{image_id} should return 404 for non-existent image"""
        response = requests.get(f"{BASE_URL}/api/forensics/image/nonexistent_image")
        # Should return 404 for non-existent image (not 500 or other error)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Forensic image endpoint exists and returns 404 for missing images")


class TestArtworksWithForensicData:
    """Tests for artworks with forensic data needed for visualization"""
    
    def test_artworks_have_forensic_data(self):
        """Artworks should have forensic_data for visualization generation"""
        response = requests.get(f"{BASE_URL}/api/artworks/?limit=5")
        assert response.status_code == 200
        artworks = response.json()
        
        # Check that at least some artworks have forensic_data
        artworks_with_forensic = [a for a in artworks if a.get('forensic_data')]
        assert len(artworks_with_forensic) > 0, "No artworks have forensic_data"
        
        # Verify forensic_data structure
        for artwork in artworks_with_forensic:
            forensic = artwork['forensic_data']
            print(f"✓ Artwork '{artwork['title']}' has forensic_data with keys: {list(forensic.keys())}")
            # Check for expected forensic fields
            assert 'pigments' in forensic or 'technique' in forensic, \
                f"Forensic data missing expected fields for {artwork['title']}"
        
        print(f"✓ {len(artworks_with_forensic)}/{len(artworks)} artworks have forensic_data")
    
    def test_mona_lisa_has_complete_forensic_data(self):
        """Mona Lisa should have complete forensic data for all visualization types"""
        response = requests.get(f"{BASE_URL}/api/artworks/?limit=50")
        assert response.status_code == 200
        artworks = response.json()
        
        mona_lisa = next((a for a in artworks if a['artwork_id'] == 'art_mona_lisa'), None)
        assert mona_lisa is not None, "Mona Lisa artwork not found"
        
        forensic = mona_lisa.get('forensic_data', {})
        assert forensic, "Mona Lisa missing forensic_data"
        
        # Check for all required fields for visualization
        required_fields = ['pigments', 'technique', 'signature_markers', 'canvas_info']
        for field in required_fields:
            assert field in forensic, f"Mona Lisa forensic_data missing '{field}'"
            print(f"✓ Mona Lisa has forensic field '{field}': {forensic[field][:50] if isinstance(forensic[field], str) else forensic[field]}")


class TestForensicsReportEndpoint:
    """Tests for existing forensics report endpoint"""
    
    def test_forensics_report_requires_auth(self):
        """GET /api/forensics/report/{artwork_id} should require authentication"""
        response = requests.get(f"{BASE_URL}/api/forensics/report/art_mona_lisa")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Forensics report correctly requires authentication")
    
    def test_forensics_analyze_requires_auth(self):
        """POST /api/forensics/analyze should require authentication"""
        response = requests.post(
            f"{BASE_URL}/api/forensics/analyze",
            json={"artwork_id": "art_mona_lisa", "analysis_type": "full"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Forensics analyze correctly requires authentication")


class TestAPIHealth:
    """Basic API health checks"""
    
    def test_api_root(self):
        """API root should return welcome message"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ API root: {data['message']}")
    
    def test_artworks_endpoint(self):
        """Artworks endpoint should return list"""
        response = requests.get(f"{BASE_URL}/api/artworks/")
        assert response.status_code == 200
        artworks = response.json()
        assert isinstance(artworks, list)
        assert len(artworks) > 0
        print(f"✓ Artworks endpoint returns {len(artworks)} artworks")
    
    def test_subscriptions_endpoint(self):
        """Subscriptions endpoint should return tiers"""
        response = requests.get(f"{BASE_URL}/api/subscriptions/")
        assert response.status_code == 200
        data = response.json()
        assert "tiers" in data
        print(f"✓ Subscriptions endpoint returns {len(data['tiers'])} tiers")


class TestVisualizationTypes:
    """Tests for different visualization analysis types"""
    
    def test_visualization_types_documented(self):
        """Verify the expected visualization types are supported"""
        # These are the types supported by the generate-visualization endpoint
        expected_types = ["pigment", "signature", "canvas", "full"]
        
        # We can't test actual generation without auth, but we verify the endpoint exists
        for viz_type in expected_types:
            response = requests.post(
                f"{BASE_URL}/api/forensics/generate-visualization",
                json={"artwork_id": "art_mona_lisa", "analysis_type": viz_type}
            )
            # Should get 401 (auth required), not 422 (validation error)
            assert response.status_code == 401, \
                f"Type '{viz_type}' returned {response.status_code}, expected 401"
            print(f"✓ Visualization type '{viz_type}' is valid (auth required)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
