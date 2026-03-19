
import sys
sys.path.insert(0, 'src')  # Add src to path

from models.database import SessionLocal
from models.app import App, AnalysisResult
from datetime import datetime

def test_database():
    print("\n" + "="*60)
    print("Testing Database Operations")
    print("="*60 + "\n")
    
    db = SessionLocal()
    
    try:
        # 1. Create a test app
        print("1. Creating test app...")
        app = App(
            package_name='com.example.testapp2',
            app_name='My Test App 2',
            developer='Test Developer',
            category='Testing',
            platform='android',
            privacy_policy_url='https://example.com/policy'
        )
        db.add(app)
        db.commit()
        db.refresh(app)
        print(f"   ✓ Created app with ID: {app.id}")
        print(f"   ✓ App: {app}\n")
        
        # 2. Create an analysis for this app
        print("2. Creating analysis...")
        analysis = AnalysisResult(
            app_id=app.id,
            app_version='1.0.0',
            overall_score=75,
            privacy_score=80,
            transparency_score=70,
            resource_score=75,
            design_score=75,
            trackers=[
                {"name": "Google Analytics", "category": "Analytics"}
            ],
            permissions=["INTERNET", "ACCESS_NETWORK_STATE"],
            policy_analysis={
                "sells_data": False,
                "can_delete_account": True,
                "clarity_score": 7
            },
            review_summary={
                "total_analyzed": 100,
                "avg_rating": 4.2
            }
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        print(f"   ✓ Created analysis with ID: {analysis.id}")
        print(f"   ✓ Analysis: {analysis}\n")
        
        # 3. Query it back
        print("3. Querying data...")
        result = db.query(App).filter(App.package_name == 'com.example.testapp2').first()
        if result is not None:
            print(f"   ✓ Found app: {result.app_name}")
            print(f"   ✓ Developer: {result.developer}")
            print(f"   ✓ Category: {result.category}")
            print(f"   ✓ Created at: {result.created_at}\n")
            # 4. Get analysis through relationship
            print("4. Getting analysis through relationship...")
            if hasattr(result, 'analyses') and result.analyses:
                analysis_result = result.analyses[0]
                print(f"   ✓ Overall score: {analysis_result.overall_score}")
                print(f"   ✓ Privacy score: {analysis_result.privacy_score}")
                print(f"   ✓ Trackers: {analysis_result.trackers}")
                print(f"   ✓ Policy analysis: {analysis_result.policy_analysis}\n")
            else:
                print("   ⚠ No analyses found for this app.\n")
        else:
            print("   ⚠ No app found with the specified package name.\n")
        
        # 5. Count all apps
        print("5. Counting all apps...")
        total_apps = db.query(App).count()
        total_analyses = db.query(AnalysisResult).count()
        print(f"   ✓ Total apps in database: {total_apps}")
        print(f"   ✓ Total analyses in database: {total_analyses}\n")
        
        print("="*60)
        print("✅ All tests passed!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    test_database()