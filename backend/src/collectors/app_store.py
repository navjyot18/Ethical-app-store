"""
Apple App Store Collector
Fetches app metadata from iTunes Search API
No API key required!
"""
import requests
from typing import Dict, List
import time

class AppStoreCollector:
    """
    Collects data from Apple App Store using iTunes Search API
    """
    
    SEARCH_URL = "https://itunes.apple.com/search"
    LOOKUP_URL = "https://itunes.apple.com/lookup"
    
    def search_app(self, app_name: str, country: str = 'us') -> Dict:
        """
        Search for an app by name
        
        Args:
            app_name: App name (e.g., "Instagram", "Signal")
            country: Country code (default: 'us')
        
        Returns:
            First matching app or empty dict
        """
        try:
            print(f"   Searching App Store for '{app_name}'...")
            
            params = {
                'term': app_name,
                'entity': 'software',
                'country': country,
                'limit': 1
            }
            
            response = requests.get(self.SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('resultCount', 0) > 0:
                return data['results'][0]
            else:
                print(f"   ⚠ No results found for '{app_name}'")
                return {}
                
        except Exception as e:
            print(f"   ✗ Search error: {e}")
            return {}
    
    def parse_app_data(self, app_data: Dict) -> Dict:
        """Parse raw iTunes API response into our format"""
        
        if not app_data:
            return {}
        
        return {
            'app_id': app_data.get('trackId'),
            'bundle_id': app_data.get('bundleId'),
            'app_name': app_data.get('trackName'),
            'developer': app_data.get('artistName'),
            'developer_id': app_data.get('artistId'),
            'category': app_data.get('primaryGenreName'),
            'description': app_data.get('description', '')[:500],
            'icon_url': app_data.get('artworkUrl512'),
            'screenshots': app_data.get('screenshotUrls', []),
            'privacy_policy_url': app_data.get('sellerUrl'),
            'rating': app_data.get('averageUserRating', 0),
            'rating_count': app_data.get('userRatingCount', 0),
            'version': app_data.get('version'),
            'release_date': app_data.get('releaseDate'),
            'price': app_data.get('price', 0),
            'app_store_url': app_data.get('trackViewUrl'),
            'content_rating': app_data.get('contentAdvisoryRating'),
            'file_size_bytes': app_data.get('fileSizeBytes'),
            'minimum_os_version': app_data.get('minimumOsVersion')
        }
    
    def analyze(self, app_name_or_id: str) -> Dict:
        """
        Complete App Store analysis
        
        Args:
            app_name_or_id: Either app name ("Instagram") or Apple ID
        
        Returns:
            {
                'metadata': {...},
                'privacy_labels': {...},
                'error': None or error message
            }
        """
        
        # Search by name
        app_data = self.search_app(app_name_or_id)
        
        if not app_data:
            return {
                'metadata': {},
                'privacy_labels': {},
                'error': 'App not found'
            }
        
        metadata = self.parse_app_data(app_data)
        
        print(f"   ✓ Found: {metadata.get('app_name')}")
        
        return {
            'metadata': metadata,
            'privacy_labels': {},
            'error': None
        }


# Test the collector
if __name__ == '__main__':
    print("\nTesting Apple App Store Collector\n" + "="*50)
    
    collector = AppStoreCollector()
    
    # Test with Instagram
    print("\n--- Instagram ---")
    result = collector.analyze('Instagram')
    
    if result.get('error'):
        print(f"✗ Error: {result['error']}")
    else:
        metadata = result['metadata']
        print(f"✓ Bundle ID: {metadata.get('bundle_id')}")
        print(f"✓ Developer: {metadata.get('developer')}")
        print(f"✓ Category: {metadata.get('category')}")
        print(f"✓ Rating: {metadata.get('rating')}/5")
        print(f"✓ Version: {metadata.get('version')}")
