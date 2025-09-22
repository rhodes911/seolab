#!/usr/bin/env python3
"""
Corrected test script with proper frontmatter handling
"""

import os
import frontmatter
from datetime import datetime

def test_frontmatter_methods():
    """Test different frontmatter writing methods"""
    print("=== Testing Frontmatter Writing Methods ===")
    
    services_file = r"C:\Users\rhode\source\repos\EllieEdwardsMarketingLeadgenSite\content\services.md"
    
    if not os.path.exists(services_file):
        print(f"ERROR: File does not exist: {services_file}")
        return False
    
    try:
        # Create backup first
        import shutil
        backup_file = services_file + ".backup"
        shutil.copy2(services_file, backup_file)
        print(f"✅ Created backup: {backup_file}")
        
        # Read the file
        with open(services_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
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
        
        # Method 1: Use frontmatter.dumps() with manual write
        try:
            content = frontmatter.dumps(post)
            with open(services_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Method 1 (frontmatter.dumps) succeeded!")
            method1_success = True
        except Exception as e:
            print(f"❌ Method 1 failed: {e}")
            method1_success = False
        
        if method1_success:
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
        else:
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test"""
    print("🔧 Frontmatter Writing Fix Test")
    print("=" * 40)
    
    success = test_frontmatter_methods()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Found working solution!")
        print("The fix is to use frontmatter.dumps() correctly")
    else:
        print("❌ Still investigating...")

if __name__ == "__main__":
    main()
