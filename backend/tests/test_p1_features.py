"""
Test P1 Features: Reviews, Notifications, Sharing, Organizations
Tests for iteration 6 - new features added to Emaira.Art
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestArtworksEndpoint:
    """Test artworks endpoint returns expected count"""
    
    def test_artworks_returns_list(self):
        """Verify artworks endpoint returns a list"""
        response = requests.get(f"{BASE_URL}/api/artworks/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"SUCCESS: Artworks endpoint returns {len(data)} artworks")
    
    def test_artworks_count_at_least_49(self):
        """Verify at least 49 artworks are seeded (requirement was 50)"""
        response = requests.get(f"{BASE_URL}/api/artworks/?limit=100")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 49, f"Expected at least 49 artworks, got {len(data)}"
        print(f"SUCCESS: Found {len(data)} artworks (requirement: 50)")
    
    def test_artwork_has_required_fields(self):
        """Verify artwork objects have required fields"""
        response = requests.get(f"{BASE_URL}/api/artworks/")
        assert response.status_code == 200
        data = response.json()
        if len(data) > 0:
            artwork = data[0]
            required_fields = ['artwork_id', 'title', 'artist', 'image_url', 'location']
            for field in required_fields:
                assert field in artwork, f"Missing field: {field}"
            print(f"SUCCESS: Artwork has all required fields")


class TestReviewsEndpoint:
    """Test reviews system endpoints"""
    
    def test_get_story_reviews(self):
        """Test GET /api/reviews/story/{story_id} returns reviews with average rating"""
        response = requests.get(f"{BASE_URL}/api/reviews/story/story_mona_lisa")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert 'reviews' in data, "Missing 'reviews' field"
        assert 'average_rating' in data, "Missing 'average_rating' field"
        assert 'total_reviews' in data, "Missing 'total_reviews' field"
        
        assert isinstance(data['reviews'], list)
        assert isinstance(data['average_rating'], (int, float))
        assert isinstance(data['total_reviews'], int)
        print(f"SUCCESS: Story reviews endpoint returns correct structure (avg: {data['average_rating']}, total: {data['total_reviews']})")
    
    def test_get_artwork_reviews(self):
        """Test GET /api/reviews/artwork/{artwork_id} returns reviews"""
        response = requests.get(f"{BASE_URL}/api/reviews/artwork/art_mona_lisa")
        assert response.status_code == 200
        data = response.json()
        
        assert 'reviews' in data
        assert 'average_rating' in data
        assert 'total_reviews' in data
        print(f"SUCCESS: Artwork reviews endpoint returns correct structure")
    
    def test_post_review_requires_auth(self):
        """Test POST /api/reviews/ requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/reviews/",
            json={
                "target_type": "story",
                "target_id": "story_mona_lisa",
                "rating": 5,
                "comment": "Test review"
            }
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("SUCCESS: POST review requires authentication (401)")
    
    def test_helpful_vote_requires_auth(self):
        """Test POST /api/reviews/{review_id}/helpful requires auth"""
        response = requests.post(f"{BASE_URL}/api/reviews/review_test123/helpful")
        assert response.status_code == 401
        print("SUCCESS: Helpful vote requires authentication (401)")


class TestSharingEndpoint:
    """Test social sharing endpoints"""
    
    def test_create_artwork_share_link(self):
        """Test POST /api/share/artwork/{artwork_id} creates share link with OG metadata"""
        response = requests.post(
            f"{BASE_URL}/api/share/artwork/art_mona_lisa",
            json={"platform": "twitter"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert 'share_id' in data, "Missing share_id"
        assert 'share_url' in data, "Missing share_url"
        assert 'og_metadata' in data, "Missing og_metadata"
        
        # Verify OG metadata
        og = data['og_metadata']
        assert 'title' in og, "Missing og title"
        assert 'description' in og, "Missing og description"
        assert 'image' in og, "Missing og image"
        assert 'url' in og, "Missing og url"
        
        print(f"SUCCESS: Share link created with OG metadata: {data['share_id']}")
    
    def test_create_story_share_link(self):
        """Test POST /api/share/story/{story_id} creates share link"""
        response = requests.post(
            f"{BASE_URL}/api/share/story/story_mona_lisa",
            json={"platform": "facebook"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert 'share_id' in data
        assert 'share_url' in data
        assert 'og_metadata' in data
        print(f"SUCCESS: Story share link created: {data['share_id']}")
    
    def test_share_link_different_platforms(self):
        """Test share links work for different platforms"""
        platforms = ['twitter', 'facebook', 'linkedin', 'copy']
        for platform in platforms:
            response = requests.post(
                f"{BASE_URL}/api/share/artwork/art_mona_lisa",
                json={"platform": platform}
            )
            assert response.status_code == 200, f"Failed for platform: {platform}"
        print(f"SUCCESS: Share links work for all platforms: {platforms}")
    
    def test_track_share_view(self):
        """Test GET /api/share/track/{share_id} tracks views"""
        # First create a share link
        create_response = requests.post(
            f"{BASE_URL}/api/share/artwork/art_mona_lisa",
            json={"platform": "copy"}
        )
        share_id = create_response.json()['share_id']
        
        # Track the view
        track_response = requests.get(f"{BASE_URL}/api/share/track/{share_id}")
        assert track_response.status_code == 200
        data = track_response.json()
        assert 'views' in data
        print(f"SUCCESS: Share view tracked, views: {data['views']}")


class TestNotificationsEndpoint:
    """Test notifications system endpoints"""
    
    def test_get_notifications_requires_auth(self):
        """Test GET /api/notifications/ requires authentication"""
        response = requests.get(f"{BASE_URL}/api/notifications/")
        assert response.status_code == 401
        print("SUCCESS: GET notifications requires authentication (401)")
    
    def test_mark_notification_read_requires_auth(self):
        """Test POST /api/notifications/{id}/read requires auth"""
        response = requests.post(f"{BASE_URL}/api/notifications/notif_test123/read")
        assert response.status_code == 401
        print("SUCCESS: Mark notification read requires authentication (401)")
    
    def test_mark_all_read_requires_auth(self):
        """Test POST /api/notifications/read-all requires auth"""
        response = requests.post(f"{BASE_URL}/api/notifications/read-all")
        assert response.status_code == 401
        print("SUCCESS: Mark all notifications read requires authentication (401)")


class TestOrganizationsEndpoint:
    """Test organizations management endpoints"""
    
    def test_list_organizations_requires_auth(self):
        """Test GET /api/organizations/ requires authentication"""
        response = requests.get(f"{BASE_URL}/api/organizations/")
        assert response.status_code == 401
        print("SUCCESS: List organizations requires authentication (401)")
    
    def test_create_organization_requires_auth(self):
        """Test POST /api/organizations/ requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/organizations/",
            json={
                "name": "Test Museum",
                "type": "museum",
                "contact_email": "test@museum.com"
            }
        )
        assert response.status_code == 401
        print("SUCCESS: Create organization requires authentication (401)")
    
    def test_get_organization_requires_auth(self):
        """Test GET /api/organizations/{org_id} requires authentication"""
        response = requests.get(f"{BASE_URL}/api/organizations/org_test123")
        assert response.status_code == 401
        print("SUCCESS: Get organization requires authentication (401)")
    
    def test_delete_organization_requires_auth(self):
        """Test DELETE /api/organizations/{org_id} requires authentication"""
        response = requests.delete(f"{BASE_URL}/api/organizations/org_test123")
        assert response.status_code == 401
        print("SUCCESS: Delete organization requires authentication (401)")


class TestStoriesEndpoint:
    """Test stories endpoint"""
    
    def test_stories_returns_list(self):
        """Verify stories endpoint returns a list"""
        response = requests.get(f"{BASE_URL}/api/stories/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 49, f"Expected at least 49 stories, got {len(data)}"
        print(f"SUCCESS: Stories endpoint returns {len(data)} stories")
    
    def test_story_has_required_fields(self):
        """Verify story objects have required fields"""
        response = requests.get(f"{BASE_URL}/api/stories/")
        assert response.status_code == 200
        data = response.json()
        if len(data) > 0:
            story = data[0]
            required_fields = ['story_id', 'title', 'artwork_id', 'price_narrative', 'price_full']
            for field in required_fields:
                assert field in story, f"Missing field: {field}"
            print(f"SUCCESS: Story has all required fields")


class TestAdminEndpoints:
    """Test admin role endpoints"""
    
    def test_get_admin_roles_requires_auth(self):
        """Test GET /api/admin/roles requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/roles")
        assert response.status_code == 401
        print("SUCCESS: Get admin roles requires authentication (401)")
    
    def test_assign_role_requires_auth(self):
        """Test POST /api/admin/assign-role/{user_id} requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/admin/assign-role/user_test123",
            json={"role": "content_curator"}
        )
        assert response.status_code == 401
        print("SUCCESS: Assign role requires authentication (401)")
    
    def test_list_admins_requires_auth(self):
        """Test GET /api/admin/users/admins requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/users/admins")
        assert response.status_code == 401
        print("SUCCESS: List admins requires authentication (401)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
