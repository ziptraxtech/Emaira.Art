import requests
import sys
import json
from datetime import datetime

class EmairaAPITester:
    def __init__(self, base_url="https://narrative-detective.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.errors = []

    def log_result(self, test_name, success, response_data=None, error_msg=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name} - PASSED")
            if response_data:
                print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
        else:
            print(f"❌ {test_name} - FAILED")
            if error_msg:
                print(f"   Error: {error_msg}")
                self.errors.append(f"{test_name}: {error_msg}")

    def test_root_endpoint(self):
        """Test root API endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            data = response.json() if success else {}
            self.log_result("Root API Endpoint", success, data, 
                          f"Status {response.status_code}" if not success else None)
            return success
        except Exception as e:
            self.log_result("Root API Endpoint", False, error_msg=str(e))
            return False

    def test_seed_data(self):
        """Test seeding initial data"""
        try:
            response = requests.post(f"{self.api_url}/seed", timeout=30)
            success = response.status_code == 200
            data = response.json() if success else {}
            self.log_result("Seed Data", success, data, 
                          f"Status {response.status_code}" if not success else None)
            return success
        except Exception as e:
            self.log_result("Seed Data", False, error_msg=str(e))
            return False

    def test_get_artworks(self):
        """Test getting all artworks - should return 20 masterpieces"""
        try:
            response = requests.get(f"{self.api_url}/artworks/?limit=50", timeout=10)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            if success and isinstance(data, list) and len(data) >= 20:
                print(f"   Found {len(data)} artworks")
                # Check first artwork structure and forensic data
                artwork = data[0]
                required_fields = ['artwork_id', 'title', 'artist', 'year', 'period', 'provenance', 'forensic_data']
                has_required = all(field in artwork for field in required_fields)
                
                # Check forensic data structure
                forensic_data = artwork.get('forensic_data', {})
                forensic_fields = ['pigments', 'signature_markers', 'canvas_info']
                has_forensic = all(field in forensic_data for field in forensic_fields)
                
                if not has_required:
                    success = False
                    self.log_result("Get 20 Artworks with Forensic Data", False, error_msg="Missing required artwork fields")
                elif not has_forensic:
                    success = False
                    self.log_result("Get 20 Artworks with Forensic Data", False, error_msg="Missing forensic data fields")
                elif len(data) < 20:
                    success = False
                    self.log_result("Get 20 Artworks with Forensic Data", False, error_msg=f"Expected 20 artworks, got {len(data)}")
                else:
                    self.log_result("Get 20 Artworks with Forensic Data", True, {
                        "count": len(data), 
                        "sample_title": artwork.get('title'),
                        "has_forensic_data": bool(forensic_data),
                        "provenance_entries": len(artwork.get('provenance', []))
                    })
            else:
                error_msg = "No artworks returned" if not data else f"Expected 20+ artworks, got {len(data)}"
                self.log_result("Get 20 Artworks with Forensic Data", False, error_msg=error_msg)
                
            return success
        except Exception as e:
            self.log_result("Get 20 Artworks with Forensic Data", False, error_msg=str(e))
            return False

    def test_get_featured_artworks(self):
        """Test getting featured artworks"""
        try:
            response = requests.get(f"{self.api_url}/artworks/?featured=true&limit=4", timeout=10)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            if success and isinstance(data, list):
                print(f"   Found {len(data)} featured artworks")
                self.log_result("Get Featured Artworks", True, {"count": len(data)})
            else:
                self.log_result("Get Featured Artworks", False, error_msg="Invalid response format")
                
            return success
        except Exception as e:
            self.log_result("Get Featured Artworks", False, error_msg=str(e))
            return False

    def test_get_stories(self):
        """Test getting all stories - should return 20 stories with narrative and forensic content"""
        try:
            response = requests.get(f"{self.api_url}/stories/?limit=50", timeout=10)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            if success and isinstance(data, list) and len(data) >= 20:
                print(f"   Found {len(data)} stories")
                story = data[0]
                required_fields = ['story_id', 'title', 'artwork_id', 'price_narrative', 'price_full', 'narrative_content', 'forensic_content']
                has_required = all(field in story for field in required_fields)
                
                # Check narrative content structure (should have 5 scenes)
                narrative_content = story.get('narrative_content', [])
                forensic_content = story.get('forensic_content', {})
                
                if not has_required:
                    success = False
                    self.log_result("Get 20 Stories with Narrative & Forensic", False, error_msg="Missing required story fields")
                elif len(data) < 20:
                    success = False
                    self.log_result("Get 20 Stories with Narrative & Forensic", False, error_msg=f"Expected 20 stories, got {len(data)}")
                elif len(narrative_content) < 5:
                    success = False
                    self.log_result("Get 20 Stories with Narrative & Forensic", False, error_msg=f"Expected 5 narrative scenes, got {len(narrative_content)}")
                else:
                    self.log_result("Get 20 Stories with Narrative & Forensic", True, {
                        "count": len(data), 
                        "sample_title": story.get('title'),
                        "narrative_scenes": len(narrative_content),
                        "has_forensic_content": bool(forensic_content)
                    })
            else:
                error_msg = "No stories returned" if not data else f"Expected 20+ stories, got {len(data)}"
                self.log_result("Get 20 Stories with Narrative & Forensic", False, error_msg=error_msg)
                
            return success
        except Exception as e:
            self.log_result("Get 20 Stories with Narrative & Forensic", False, error_msg=str(e))
            return False

    def test_get_subscription_tiers(self):
        """Test getting subscription tiers"""
        try:
            response = requests.get(f"{self.api_url}/payments/tiers", timeout=10)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            if success and isinstance(data, list) and len(data) == 4:
                print(f"   Found {len(data)} subscription tiers")
                tier_names = [tier.get('name', 'Unknown') for tier in data]
                print(f"   Tiers: {', '.join(tier_names)}")
                self.log_result("Get Subscription Tiers", True, {"tiers": tier_names})
            else:
                self.log_result("Get Subscription Tiers", False, 
                              error_msg=f"Expected 4 tiers, got {len(data) if isinstance(data, list) else 'invalid format'}")
                
            return success
        except Exception as e:
            self.log_result("Get Subscription Tiers", False, error_msg=str(e))
            return False

    def test_individual_artwork(self):
        """Test getting individual artwork"""
        try:
            # First get artworks to find a valid ID
            artworks_response = requests.get(f"{self.api_url}/artworks/?limit=1", timeout=10)
            if artworks_response.status_code != 200 or not artworks_response.json():
                self.log_result("Individual Artwork", False, error_msg="No artworks available for testing")
                return False
                
            artwork_id = artworks_response.json()[0]['artwork_id']
            
            # Test individual artwork
            response = requests.get(f"{self.api_url}/artworks/{artwork_id}", timeout=10)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            if success:
                required_fields = ['artwork_id', 'title', 'artist', 'description', 'image_url']
                has_required = all(field in data for field in required_fields)
                if has_required:
                    self.log_result("Individual Artwork", True, {"artwork_id": artwork_id, "title": data.get('title')})
                else:
                    success = False
                    self.log_result("Individual Artwork", False, error_msg="Missing required fields in artwork detail")
            else:
                self.log_result("Individual Artwork", False, error_msg=f"Status {response.status_code}")
                
            return success
        except Exception as e:
            self.log_result("Individual Artwork", False, error_msg=str(e))
            return False

    def test_individual_story(self):
        """Test getting individual story"""
        try:
            # First get stories to find a valid ID
            stories_response = requests.get(f"{self.api_url}/stories/?limit=1", timeout=10)
            if stories_response.status_code != 200 or not stories_response.json():
                self.log_result("Individual Story", False, error_msg="No stories available for testing")
                return False
                
            story_id = stories_response.json()[0]['story_id']
            
            # Test individual story
            response = requests.get(f"{self.api_url}/stories/{story_id}", timeout=10)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            if success:
                required_fields = ['story_id', 'title', 'artwork_id', 'description', 'has_access']
                has_required = all(field in data for field in required_fields)
                if has_required:
                    self.log_result("Individual Story", True, {
                        "story_id": story_id, 
                        "title": data.get('title'),
                        "has_access": data.get('has_access')
                    })
                else:
                    success = False
                    self.log_result("Individual Story", False, error_msg="Missing required fields in story detail")
            else:
                self.log_result("Individual Story", False, error_msg=f"Status {response.status_code}")
                
            return success
        except Exception as e:
            self.log_result("Individual Story", False, error_msg=str(e))
            return False

    def test_auth_endpoints(self):
        """Test authentication endpoints (without actual auth)"""
        try:
            # Test /auth/me without authentication - should return 401
            response = requests.get(f"{self.api_url}/auth/me", timeout=10)
            success = response.status_code == 401
            
            if success:
                self.log_result("Auth Endpoint (Unauthorized)", True, {"status": "Correctly returns 401 for unauthorized"})
            else:
                self.log_result("Auth Endpoint (Unauthorized)", False, 
                              error_msg=f"Expected 401, got {response.status_code}")
                
            return success
        except Exception as e:
            self.log_result("Auth Endpoint (Unauthorized)", False, error_msg=str(e))
            return False

    def test_server_health(self):
        """Test overall server health"""
        try:
            # Test basic server connectivity
            response = requests.get(self.base_url, timeout=10)
            success = response.status_code in [200, 404]  # 404 is fine, means server is up
            
            self.log_result("Server Health", success, 
                          {"status": f"Server responding with {response.status_code}"},
                          f"Server not responding - Status: {response.status_code}" if not success else None)
            return success
        except Exception as e:
            self.log_result("Server Health", False, error_msg=str(e))
            return False

    def test_crm_analytics(self):
        """Test CRM analytics endpoint"""
        try:
            response = requests.get(f"{self.api_url}/crm/analytics", timeout=10)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            if success:
                required_fields = ['total_users', 'subscription_breakdown', 'revenue', 'active_users_7d']
                has_required = all(field in data for field in required_fields)
                if has_required:
                    self.log_result("CRM Analytics", True, {
                        "total_users": data.get('total_users', 0),
                        "revenue": data.get('revenue', {}).get('total', 0),
                        "active_users": data.get('active_users_7d', 0)
                    })
                else:
                    success = False
                    self.log_result("CRM Analytics", False, error_msg="Missing required analytics fields")
            else:
                self.log_result("CRM Analytics", False, error_msg=f"Status {response.status_code}")
                
            return success
        except Exception as e:
            self.log_result("CRM Analytics", False, error_msg=str(e))
            return False

    def test_crm_segments(self):
        """Test CRM user segments endpoint"""
        try:
            response = requests.get(f"{self.api_url}/crm/segments", timeout=10)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            if success and isinstance(data, dict):
                expected_segments = ['high_value', 'subscribers', 'one_time_buyers', 'free_users', 'inactive_30d', 'forensics_enthusiasts']
                has_segments = all(segment in data for segment in expected_segments)
                if has_segments:
                    self.log_result("CRM User Segments", True, {
                        "total_segments": len(data),
                        "high_value_users": data.get('high_value', 0),
                        "subscribers": data.get('subscribers', 0)
                    })
                else:
                    success = False
                    missing = [s for s in expected_segments if s not in data]
                    self.log_result("CRM User Segments", False, error_msg=f"Missing segments: {missing}")
            else:
                self.log_result("CRM User Segments", False, error_msg="Invalid response format")
                
            return success
        except Exception as e:
            self.log_result("CRM User Segments", False, error_msg=str(e))
            return False

    def test_crm_users(self):
        """Test CRM users endpoint with pagination"""
        try:
            response = requests.get(f"{self.api_url}/crm/users?page=1&limit=10", timeout=10)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            if success and isinstance(data, dict):
                required_fields = ['users', 'total', 'page', 'limit', 'total_pages']
                has_required = all(field in data for field in required_fields)
                if has_required and isinstance(data['users'], list):
                    self.log_result("CRM Paginated Users", True, {
                        "total_users": data.get('total', 0),
                        "returned_users": len(data.get('users', [])),
                        "current_page": data.get('page', 0)
                    })
                else:
                    success = False
                    self.log_result("CRM Paginated Users", False, error_msg="Missing required pagination fields")
            else:
                self.log_result("CRM Paginated Users", False, error_msg=f"Status {response.status_code}")
                
            return success
        except Exception as e:
            self.log_result("CRM Paginated Users", False, error_msg=str(e))
            return False

    def test_crm_activities(self):
        """Test CRM activities endpoint"""
        try:
            response = requests.get(f"{self.api_url}/crm/activities?limit=20", timeout=10)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            if success and isinstance(data, dict):
                required_fields = ['activities', 'total', 'page', 'limit']
                has_required = all(field in data for field in required_fields)
                if has_required and isinstance(data['activities'], list):
                    activities = data['activities']
                    activity_types = set(act.get('activity_type') for act in activities if act.get('activity_type'))
                    self.log_result("CRM Activities Log", True, {
                        "total_activities": data.get('total', 0),
                        "returned_activities": len(activities),
                        "activity_types": list(activity_types)
                    })
                else:
                    success = False
                    self.log_result("CRM Activities Log", False, error_msg="Missing required activity fields")
            else:
                self.log_result("CRM Activities Log", False, error_msg=f"Status {response.status_code}")
                
            return success
        except Exception as e:
            self.log_result("CRM Activities Log", False, error_msg=str(e))
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print("🔍 Starting Emaira.Art API Testing...")
        print(f"Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test server health first
        if not self.test_server_health():
            print("❌ Server is not responding. Cannot proceed with API tests.")
            return False
            
        # Seed data first
        self.test_seed_data()
        
        # Core API tests
        self.test_root_endpoint()
        self.test_get_artworks()
        self.test_get_featured_artworks()
        self.test_individual_artwork()
        self.test_get_stories()
        self.test_individual_story()
        self.test_get_subscription_tiers()
        
        # CRM API tests
        self.test_crm_analytics()
        self.test_crm_segments()
        self.test_crm_users()
        self.test_crm_activities()
        
        # Auth tests
        self.test_auth_endpoints()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary:")
        print(f"✅ Passed: {self.tests_passed}/{self.tests_run}")
        print(f"❌ Failed: {self.tests_run - self.tests_passed}/{self.tests_run}")
        
        if self.errors:
            print("\n🐛 Errors found:")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"   - {error}")
            if len(self.errors) > 5:
                print(f"   ... and {len(self.errors) - 5} more errors")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    tester = EmairaAPITester()
    success = tester.run_all_tests()
    
    # Return exit code
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())