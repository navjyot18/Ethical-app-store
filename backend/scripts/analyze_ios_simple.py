"""
Simple iOS app analyzer - No privacy policy analysis
Just fetches App Store data and saves basic info
"""
from calendar import c
import sys

from fastapi import requests
sys.path.insert(0, '../src')

from collectors.app_store import AppStoreCollector
from models.database import SessionLocal
from models.app import App, AnalysisResult
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def analyze_ios_simple(app_name: str):
    """
    Simple iOS analysis - just App Store data
    """
    print(f"\n{'='*70}")
    print(f"ANALYZING: {app_name}")
    print(f"{'='*70}\n")
    
    # Get App Store data
    collector = AppStoreCollector()
    result = collector.analyze(app_name)
    
    if result.get('error'):
        print(f"❌ Error: {result['error']}")
        return None
    
    metadata = result['metadata']
    
    # Display what we found
    print("✅ App Found!")
    print(f"\n📱 Name: {metadata['app_name']}")
    print(f"👤 Developer: {metadata['developer']}")
    print(f"📦 Bundle ID: {metadata['bundle_id']}")
    print(f"📂 Category: {metadata['category']}")
    print(f"⭐ Rating: {metadata['rating']}/5 ({metadata['rating_count']} reviews)")
    print(f"📱 Version: {metadata['version']}")
    file_size_bytes = metadata.get('file_size_bytes', 0)
    try:
        file_size_bytes = int(file_size_bytes)
    except (ValueError, TypeError):
        file_size_bytes = 0
    print(f"💾 Size: {file_size_bytes / 1024 / 1024:.1f} MB")
    
    # Calculate simple scores
    # For iOS without trackers/permissions, we use basic heuristics
    
    # Privacy score: Start at 70 (we don't know about trackers)
    privacy_score = 70
    trackers = []
    # Try to get trackers and privacy label data using get_apple_privacy_data
    policy_analysis = {
        "platform": "ios",
        "source": "Apple Privacy Nutrition Labels",
        "verified": False,
        "type": "self_reported",
        "data_used_for_tracking": [],
        "data_linked_to_identity": [],
        "data_not_linked_to_you": []
    }
    try:
        app_store_url = metadata.get('app_store_url')
        if app_store_url and '/id' in app_store_url:
            app_id = app_store_url.split('/id')[-1].split('?')[0]
            privacy_data = get_apple_privacy_data(app_id)
            # Map privacy_data to policy_analysis fields
            for item in privacy_data:
                title = item.get('title', '').lower()
                categories = item.get('categories', [])
                if 'track' in title:
                    policy_analysis['data_used_for_tracking'].extend(categories)
                elif 'linked' in title:
                    policy_analysis['data_linked_to_identity'].extend(categories)
                elif 'not linked' in title:
                    policy_analysis['data_not_linked_to_you'].extend(categories)
            # Remove duplicates
            policy_analysis['data_used_for_tracking'] = list(set(policy_analysis['data_used_for_tracking']))
            policy_analysis['data_linked_to_identity'] = list(set(policy_analysis['data_linked_to_identity']))
            policy_analysis['data_not_linked_to_you'] = list(set(policy_analysis['data_not_linked_to_you']))
            # For backward compatibility, trackers can be the full privacy_data
            trackers = privacy_data
            privacy_score = 50 if trackers else 70  # Lower score if trackers found
    except Exception as e:
        print(f"[WARN] Could not fetch Apple privacy data: {e}")
        trackers = [{
            'note': 'iOS does not expose tracker data via API',
            'limitation': 'Use App Privacy Report on device to see actual trackers'
        }]
        policy_analysis['note'] = 'Privacy policy analysis skipped for speed'
        policy_analysis['app_store_url'] = metadata.get('app_store_url')

    # Transparency score: Based on if they have privacy policy
    transparency_score = 60 if metadata.get('privacy_policy_url') else 40
    # Resource score: Based on app size (smaller is better)
    size_mb = file_size_bytes / 1024 / 1024
    if size_mb < 100:
        resource_score = 90
    elif size_mb < 300:
        resource_score = 70
    else:
        resource_score = 50
        

    # Design score: Based on rating
    rating = metadata.get('rating', 0)
    design_score = int((rating / 5) * 100)

    # Overall score
    overall_score = int(
        privacy_score * 0.4 +
        transparency_score * 0.3 +
        resource_score * 0.15 +
        design_score * 0.15
    )
    
    print(f"\n📊 Scores:")
    print(f"  🎯 Overall: {overall_score}/100")
    print(f"  🔒 Privacy: {privacy_score}/100 (⚠️  Limited data for iOS)")
    print(f"  👁️  Transparency: {transparency_score}/100")
    print(f"  ⚡ Resources: {resource_score}/100")
    print(f"  🎨 Design: {design_score}/100")
    
    # Save to database
    print(f"\n💾 Saving to database...")
    db = SessionLocal()
    
    try:
        bundle_id = metadata['bundle_id']
        
        # Check if app exists
        app = db.query(App).filter(App.package_name == bundle_id).first()
        
        if not app:
            app = App(
                package_name=bundle_id,
                app_name=metadata['app_name'],
                developer=metadata['developer'],
                category=metadata['category'],
                platform='ios',
                icon_url=metadata['icon_url'],
                privacy_policy_url=metadata.get('app_store_url'),  # Use App Store URL
                description=metadata['description']
            )
            db.add(app)
            db.commit()
            db.refresh(app)
            print(f"  ✓ App saved (ID: {app.id})")
        else:
            print(f"  ✓ App already exists (ID: {app.id})")
        
        # Save analysis
        analysis = AnalysisResult(
            app_id=app.id,
            app_version=metadata['version'],
            analyzed_at=datetime.utcnow(),
            overall_score=overall_score,
            privacy_score=privacy_score,
            transparency_score=transparency_score,
            resource_score=resource_score,
            design_score=design_score,
            
            # iOS limitations or real tracker data
            trackers=trackers,
            permissions=[{
                'note': 'iOS does not expose permission data via API',
                'limitation': 'Check app page in App Store for privacy labels'
            }],
            policy_analysis=policy_analysis,
            review_summary={
                'avg_rating': metadata['rating'],
                'total_ratings': metadata['rating_count'],
                'note': 'Full review analysis not performed'
            },
            scoring_version='v1.0.0-ios-simple'
        )
        db.add(analysis)
        db.commit()
        
        print(f"  ✓ Analysis saved (ID: {analysis.id})")
        print(f"\n✅ Complete!\n")
        print(f"{'='*70}\n")
        
        return {
            'app_id': app.id,
            'bundle_id': bundle_id,
            'scores': {
                'overall': overall_score,
                'privacy': privacy_score,
                'transparency': transparency_score,
                'resource': resource_score,
                'design': design_score
            }
        }
        
    except Exception as e:
        print(f"\n❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return None
    finally:
        db.close()

def get_apple_privacy_data(app_id):
    url = f"https://apps.apple.com/us/app/id{app_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    detected_trackers = []
    result = []
    # 1. Find all privacy cards (Data Used to Track You, Data Linked to You, etc.)
    privacy_section = soup.find('section', {"id": "privacyTypes"})
    articles = privacy_section.find_all("article") if privacy_section else []
    for article in articles:
        # Extract title
        title_tag = article.find("h2")
        title = title_tag.get_text(strip=True) if title_tag else "Unknown"
        
        # Extract description
        desc_tag = article.find("p")
        desc = desc_tag.get_text(strip=True) if desc_tag else "Unknown"
        
        # Extract categories
        categories = []
        category_list = article.find("ul")
        if category_list:
            for li in category_list.find_all("li"):
                categories.append(li.get_text(strip=True))
        
        result.append({
            "title": title,
            "description": desc,
            "categories": categories
        })

    return result

if __name__ == '__main__':
    # --- Commented out main analysis code for testing trackers only ---
    # Analyze popular iOS apps
    apps = [
        'Instagram',
        'Signal',
        'WhatsApp',
        'TikTok',
        'Notion'
    ]
    
    print("🍎 Simple iOS App Analyzer")
    print("Fast analysis using only App Store data\n")
    
    results = []
    for i, app_name in enumerate(apps, 1):
        print(f"[{i}/{len(apps)}] {app_name}")
        result = analyze_ios_simple(app_name)
        results.append(result)
        
        if i < len(apps):
            import time
            time.sleep(2)
    
    # Summary
    print(f"{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}\n")
    
    successful = sum(1 for r in results if r)
    print(f"✓ Successfully analyzed: {successful}/{len(apps)}")
    
    if successful > 0:
        print("\nScores:")
        for app_name, result in zip(apps, results):
            if result:
                print(f"  • {app_name:15} - {result['scores']['overall']}/100")
    
    print(f"\n{'='*70}\n")

    # --- Test get_apple_privacy_data for 5 apps by App Store ID ---
    # app_ids = {
    #     'Instagram': '389801252',
    #     'Signal': '874139669',
    #     'WhatsApp': '310633997',
    #     'TikTok': '835599320',
    #     'Notion': '1232780281',
    # }
    # print("\n🍏 Testing get_apple_privacy_data for 5 apps:\n")
    # for app_name, app_id in app_ids.items():
    #     print(f"App: {app_name} (ID: {app_id})")
    #     trackers = get_apple_privacy_data(app_id)
    #     print(f"  Detected trackers: {trackers if trackers else 'None'}\n")
