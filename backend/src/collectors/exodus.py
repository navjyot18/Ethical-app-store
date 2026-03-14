import requests
from typing import Dict, List, Optional
import time
class ExodusCollector:
    BASE_URL = "https://reports.exodus-privacy.eu.org/api"

    def __init__(self, api_key: Optional[str] = None, user_agent: str = "ethical-app-store/1.0"):
        """Initialize the collector.

        Args:
            api_key: (Optional) Exodus API key to use for authenticated requests.
            user_agent: User-Agent header value to send (recommended by Exodus API).
        """
        self.api_key = api_key
        self.user_agent = user_agent

    def get_report(self, package_name: str) -> Dict:
        """Fetch the latest Exodus report for a given package.

        Uses the documented `/api/search/{handle}/details` endpoint. This returns a
        list of reports; we use the first report (most recent) when available.
        """
        url = f"{self.BASE_URL}/search/{package_name}/details"

        headers = {"User-Agent": self.user_agent}
        if self.api_key:
            headers["Authorization"] = f"Token {self.api_key}"

        try:
            print(f"   Fetching Exodus data for {package_name}...")
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()

            # /search/{handle}/details returns a list. Use the first (most recent) entry.
            if isinstance(data, list) and data:
                return data[0]

            # Older endpoints might return a dict keyed by handle.
            if isinstance(data, dict):
                # Example: {"com.app.handle": {...}}
                if package_name in data:
                    reports = data[package_name].get("reports") or []
                    if reports:
                        return reports[-1] if isinstance(reports, list) else data[package_name]
                # Unexpected dict form.
            print(f"   ⚠ No Exodus report found for {package_name}")
            return {}

        except requests.exceptions.RequestException as e:
            print(f"   ✗ Exodus API error: {e}")
            return {}
        
    def get_tracker_details(self, tracker_id: int) -> Optional[Dict]:
        """Get details for a specific tracker"""
        url = f"{self.BASE_URL}/trackers/{tracker_id}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"   ✗ Error fetching tracker {tracker_id}: {e}")
            return None

    def analyze(self, package_name: str) -> Dict:
        """
        Complete analysis with tracker details
        
        Returns:
            {
                'trackers': [{'name': '...', 'category': '...', ...}],
                'permissions': ['CAMERA', 'LOCATION', ...],
                'app_version': '1.0.0',
                'error': None or error message
            }
        """
        report = self.get_report(package_name)
        
        if not report:
            return {
                'trackers': [],
                'permissions': [],
                'app_version': None,
                'error': 'No Exodus report found'
            }
        
        # Get tracker IDs from report
        tracker_ids = report.get('trackers', [])
        
        # Fetch details for each tracker
        trackers = []
        for tracker_id in tracker_ids:
            details = self.get_tracker_details(tracker_id)
            if details:
                trackers.append({
                    'id': tracker_id,
                    'name': details.get('name', 'Unknown'),
                    'category': details.get('categories', ['Unknown'])[0] if details.get('categories') else 'Unknown',
                    'website': details.get('website', ''),
                    'description': details.get('description', '')[:200]  # Truncate description
                })
            time.sleep(0.2)  # Be nice to their API
        
        return {
            'trackers': trackers,
            'permissions': report.get('permissions', []),
            'app_version': report.get('version_name', 'Unknown'),
            'error': None
        }
    

# Test the collector
if __name__ == '__main__':
    print("\nTesting Exodus Collector\n" + "="*50)
    
    collector = ExodusCollector()
    
    # Test with Instagram
    print("\nAnalyzing Instagram...")
    result = collector.analyze('com.instagram.android')
    
    print(f"\n✓ Trackers found: {len(result['trackers'])}")
    print(f"✓ Permissions found: {len(result['permissions'])}")
    print(f"✓ App version: {result['app_version']}")
    
    if result['trackers']:
        print("\nFirst 3 trackers:")
        for tracker in result['trackers'][:3]:
            print(f"  - {tracker['name']} ({tracker['category']})")
    
    if result['permissions']:
        print("\nFirst 5 permissions:")
        for perm in result['permissions'][:5]:
            print(f"  - {perm}")
