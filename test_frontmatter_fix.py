#!/usr/bin/env python3
"""
Fixed test script to verify the TinaCMS saving issue
"""

import os
import sys
import frontmatter
from datetime import datetime

def test_frontmatter_writing_fix():
    """Test the corrected frontmatter writing"""
    print("=== Testing Fixed Frontmatter Writing ===")
    
    services_file = r"C:\Users\rhode\source\repos\EllieEdwardsMarketingLeadgenSite\content\services.md"
    
    if not os.path.exists(services_file):
        print(f"ERROR: File does not exist: {services_file}")
        return False
    
    try:
        # Read the file
        with open(services_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        print("✅ Successfully read frontmatter")
        
        # Ensure SEO section exists
        if 'seo' not in post.metadata:
            post.metadata['seo'] = {}
        
        # Add test SERP analysis data
        test_analysis = {
            'avgDifficulty': 65.5,
            'easyCount': 3,
            'moderateCount': 7,
            'hardCount': 2,
            'topOpportunities': [
                'brand strategy consultant',
                'small business branding',
                'brand development services'
            ],
            'analysisNotes': [
                'Good opportunity for local targeting',
                'Moderate competition in main keywords'
            ],
            'nextSteps': [
                'Focus on long-tail variations',
                'Create location-specific content'
            ]
        }
        
        # Update the metadata
        post.metadata['seo']['serpAnalysis'] = test_analysis
        post.metadata['seo']['lastAnalysisDate'] = datetime.now().isoformat()
        
        print("✅ Added test data to metadata")
        
        # Write the file using the correct method
        with open(services_file, 'w', encoding='utf-8') as f:
            # Use frontmatter.dump() instead of f.write(frontmatter.dumps())
            frontmatter.dump(post, f)
        
        print("✅ Successfully wrote file using frontmatter.dump()")
        
        # Verify by reading back
        with open(services_file, 'r', encoding='utf-8') as f:
            verify_post = frontmatter.load(f)
        
        if 'seo' in verify_post.metadata and 'serpAnalysis' in verify_post.metadata['seo']:
            print("✅ Verification successful - data was written and can be read back")
            print(f"Saved avgDifficulty: {verify_post.metadata['seo']['serpAnalysis']['avgDifficulty']}")
            print(f"Saved lastAnalysisDate: {verify_post.metadata['seo']['lastAnalysisDate']}")
            return True
        else:
            print("❌ Verification failed - data was not saved correctly")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_streamlit_app_code():
    """Test the actual code used in the Streamlit app"""
    print("\n=== Testing Streamlit App Code Pattern ===")
    
    try:
        # Simulate the exact code from app.py
        services_file = r"C:\Users\rhode\source\repos\EllieEdwardsMarketingLeadgenSite\content\services.md"
        
        # Load current page (same as app.py line 537-538)
        with open(services_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        # Ensure SEO section exists (same as app.py line 541-542)
        if "seo" not in post.metadata:
            post.metadata["seo"] = {}
        
        # Simulate analysis results
        avg = 62.3
        easy = 4
        moderate = 8  
        hard = 3
        opps = [{"keyword": "brand strategy"}, {"keyword": "business branding"}]
        bullets = ["Strong local opportunity", "Moderate competition"]
        steps = ["Create location pages", "Optimize for local terms"]
        
        # Save analysis results (same as app.py lines 550-560)
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
        
        # Write back to file (same as app.py lines 563-564)
        # THIS IS THE PROBLEMATIC LINE IN APP.PY
        with open(services_file, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))  # <-- This line causes the error!
        
        print("❌ This should fail with the same error from app.py")
        return False
        
    except Exception as e:
        print(f"✅ Confirmed error in app.py code: {e}")
        return True

def main():
    """Run all tests"""
    print("🔧 TinaCMS Frontmatter Fix Test")
    print("=" * 50)
    
    # Test 1: Proper frontmatter writing
    success1 = test_frontmatter_writing_fix()
    
    # Test 2: Reproduce the app.py error
    success2 = test_streamlit_app_code()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✅ Found the issue and confirmed the fix works!")
        print("The problem is in app.py line 564:")
        print("  WRONG: f.write(frontmatter.dumps(post))")
        print("  RIGHT: frontmatter.dump(post, f)")
    else:
        print("❌ Tests failed")

if __name__ == "__main__":
    main()
