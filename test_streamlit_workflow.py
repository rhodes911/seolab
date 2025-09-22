#!/usr/bin/env python3
"""
Test the exact Streamlit app workflow
"""

import os
import sys

# Add streamlit_app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'streamlit_app'))

def test_exact_streamlit_workflow():
    """Test the exact workflow from Streamlit app"""
    print("=== Testing Exact Streamlit Workflow ===")
    
    # Replicate the exact path logic from app.py lines 18-19
    ellie_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "EllieEdwardsMarketingLeadgenSite"))
    print(f"Ellie root path: {ellie_root}")
    print(f"Ellie root exists: {os.path.exists(ellie_root)}")
    
    # Test the services page path
    services_path = os.path.join(ellie_root, "content", "services.md")
    print(f"Services path: {services_path}")
    print(f"Services path exists: {os.path.exists(services_path)}")
    
    # Test the services subdirectory structure
    services_dir = os.path.join(ellie_root, "content", "services")
    print(f"Services directory: {services_dir}")
    print(f"Services directory exists: {os.path.exists(services_dir)}")
    
    if os.path.exists(services_dir):
        print(f"Services directory contents: {os.listdir(services_dir)}")
        
        # Test brand-strategy specifically
        brand_strategy_path = os.path.join(services_dir, "brand-strategy.md")
        print(f"Brand strategy path: {brand_strategy_path}")
        print(f"Brand strategy exists: {os.path.exists(brand_strategy_path)}")
        
        if os.path.exists(brand_strategy_path):
            return test_save_to_file(brand_strategy_path)
    
    return False

def test_save_to_file(file_path):
    """Test saving SERP analysis to the specific file"""
    print(f"\n=== Testing Save to {file_path} ===")
    
    try:
        import frontmatter
        from datetime import datetime
        
        # Create backup
        import shutil
        backup_path = file_path + ".test_backup"
        shutil.copy2(file_path, backup_path)
        print(f"✅ Created backup: {backup_path}")
        
        # Load current page (exact same as app.py)
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        print(f"✅ Loaded frontmatter, keys: {list(post.metadata.keys())}")
        
        # Ensure SEO section exists (exact same as app.py)
        if "seo" not in post.metadata:
            post.metadata["seo"] = {}
        
        # Test data
        avg = 58.7
        easy = 5
        moderate = 8
        hard = 2
        opps = [{"keyword": "brand strategy services"}, {"keyword": "business branding consultant"}]
        bullets = ["Strong local opportunity in Surrey area", "Moderate competition for main terms"]
        steps = ["Create location-specific landing pages", "Optimize for consultant-type queries"]
        
        # Save analysis results (exact same as app.py)
        post.metadata["seo"]["lastAnalysisDate"] = datetime.now().isoformat()
        post.metadata["seo"]["serpAnalysis"] = {
            "avgDifficulty": avg,
            "easyCount": easy,
            "moderateCount": moderate,
            "hardCount": hard,
            "topOpportunities": [r["keyword"] for r in opps[:10]],
            "analysisNotes": bullets,
            "nextSteps": steps,
        }
        
        print("✅ Updated metadata with analysis results")
        
        # Write back to file (exact same as app.py lines 563-564)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        print("✅ Successfully wrote file using frontmatter.dumps()")
        
        # Verify
        with open(file_path, 'r', encoding='utf-8') as f:
            verify_post = frontmatter.load(f)
        
        if 'seo' in verify_post.metadata and 'serpAnalysis' in verify_post.metadata['seo']:
            print("✅ Verification successful!")
            analysis = verify_post.metadata['seo']['serpAnalysis']
            print(f"   avgDifficulty: {analysis['avgDifficulty']}")
            print(f"   topOpportunities: {analysis['topOpportunities']}")
            print(f"   lastAnalysisDate: {verify_post.metadata['seo']['lastAnalysisDate']}")
            return True
        else:
            print("❌ Verification failed")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test"""
    print("🧪 Testing Exact Streamlit App Workflow")
    print("=" * 50)
    
    success = test_exact_streamlit_workflow()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Streamlit app workflow works correctly!")
        print("The issue might be elsewhere in the app flow.")
    else:
        print("❌ Found issues in the workflow")

if __name__ == "__main__":
    main()
