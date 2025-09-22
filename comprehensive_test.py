#!/usr/bin/env python3
"""
Comprehensive test suite to verify TinaCMS SERP analysis saving works end-to-end
"""

import os
import sys
import frontmatter
from datetime import datetime

def test_1_file_paths():
    """Test 1: Verify all file paths are correct"""
    print("🧪 TEST 1: File Path Verification")
    print("=" * 50)
    
    # Test the hardcoded path from app.py
    ellie_root = r"C:\Users\rhode\source\repos\EllieEdwardsMarketingLeadgenSite"
    print(f"TinaCMS root: {ellie_root}")
    print(f"TinaCMS root exists: {os.path.exists(ellie_root)}")
    
    content_dir = os.path.join(ellie_root, "content")
    print(f"Content directory: {content_dir}")
    print(f"Content directory exists: {os.path.exists(content_dir)}")
    
    # Test services.md
    services_file = os.path.join(content_dir, "services.md")
    print(f"Services file: {services_file}")
    print(f"Services file exists: {os.path.exists(services_file)}")
    
    # Test services subdirectory and brand-strategy
    services_dir = os.path.join(content_dir, "services")
    print(f"Services directory: {services_dir}")
    print(f"Services directory exists: {os.path.exists(services_dir)}")
    
    if os.path.exists(services_dir):
        brand_strategy_file = os.path.join(services_dir, "brand-strategy.md")
        print(f"Brand strategy file: {brand_strategy_file}")
        print(f"Brand strategy file exists: {os.path.exists(brand_strategy_file)}")
        
        if os.path.exists(brand_strategy_file):
            return brand_strategy_file, services_file
    
    return None, services_file

def test_2_frontmatter_reading(file_path):
    """Test 2: Verify we can read existing frontmatter"""
    print(f"\n🧪 TEST 2: Frontmatter Reading - {os.path.basename(file_path)}")
    print("=" * 50)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        print(f"✅ Successfully loaded frontmatter")
        print(f"Metadata keys: {list(post.metadata.keys())}")
        
        if 'seo' in post.metadata:
            seo = post.metadata['seo']
            print(f"SEO section keys: {list(seo.keys())}")
            
            # Check current state of SERP fields
            if 'serpAnalysis' in seo:
                print(f"⚠️  serpAnalysis already exists: {seo['serpAnalysis']}")
            else:
                print("✅ serpAnalysis field not present (will be added)")
                
            if 'lastAnalysisDate' in seo:
                print(f"⚠️  lastAnalysisDate already exists: {seo['lastAnalysisDate']}")
            else:
                print("✅ lastAnalysisDate field not present (will be added)")
        else:
            print("⚠️  No SEO section found (will be created)")
            
        return post
        
    except Exception as e:
        print(f"❌ ERROR reading frontmatter: {e}")
        return None

def test_3_frontmatter_writing(file_path, post):
    """Test 3: Verify we can write SERP analysis data"""
    print(f"\n🧪 TEST 3: Frontmatter Writing - {os.path.basename(file_path)}")
    print("=" * 50)
    
    if post is None:
        print("❌ No post object to test with")
        return False
    
    try:
        # Create backup
        import shutil
        backup_path = file_path + ".test_backup"
        shutil.copy2(file_path, backup_path)
        print(f"✅ Created backup: {backup_path}")
        
        # Ensure SEO section exists
        if 'seo' not in post.metadata:
            post.metadata['seo'] = {}
        
        # Create test analysis data (simulating what the Streamlit app would save)
        test_analysis = {
            'avgDifficulty': 58.7,
            'easyCount': 5,
            'moderateCount': 8,
            'hardCount': 2,
            'topOpportunities': [
                'brand strategy services surrey',
                'business branding consultant camberley',
                'brand development mytchett'
            ],
            'analysisNotes': [
                'Strong local opportunity in Surrey area',
                'Moderate competition for main consultant terms',
                'Good potential for location-specific content'
            ],
            'nextSteps': [
                'Create location-specific landing pages',
                'Optimize for consultant-type queries',
                'Develop case study content for local businesses'
            ]
        }
        
        # Update metadata (exactly like app.py does)
        post.metadata['seo']['lastAnalysisDate'] = datetime.now().isoformat()
        post.metadata['seo']['serpAnalysis'] = test_analysis
        
        print("✅ Updated metadata with test analysis data")
        
        # Write file (exactly like app.py line 564)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        print("✅ Successfully wrote file using frontmatter.dumps()")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR writing frontmatter: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_4_verification(file_path):
    """Test 4: Verify the saved data can be read back correctly"""
    print(f"\n🧪 TEST 4: Data Verification - {os.path.basename(file_path)}")
    print("=" * 50)
    
    try:
        # Read the file back
        with open(file_path, 'r', encoding='utf-8') as f:
            verify_post = frontmatter.load(f)
        
        print("✅ Successfully re-read the file")
        
        # Check if our data is there
        if 'seo' not in verify_post.metadata:
            print("❌ SEO section missing after save")
            return False
        
        seo = verify_post.metadata['seo']
        
        if 'serpAnalysis' not in seo:
            print("❌ serpAnalysis missing after save")
            return False
        
        if 'lastAnalysisDate' not in seo:
            print("❌ lastAnalysisDate missing after save")
            return False
        
        analysis = seo['serpAnalysis']
        print("✅ SERP Analysis data found:")
        print(f"   avgDifficulty: {analysis.get('avgDifficulty')}")
        print(f"   easyCount: {analysis.get('easyCount')}")
        print(f"   moderateCount: {analysis.get('moderateCount')}")
        print(f"   hardCount: {analysis.get('hardCount')}")
        print(f"   topOpportunities: {len(analysis.get('topOpportunities', []))} items")
        print(f"   analysisNotes: {len(analysis.get('analysisNotes', []))} items")
        print(f"   nextSteps: {len(analysis.get('nextSteps', []))} items")
        print(f"✅ lastAnalysisDate: {seo['lastAnalysisDate']}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR verifying data: {e}")
        return False

def test_5_streamlit_app_simulation():
    """Test 5: Simulate the exact Streamlit app page discovery"""
    print(f"\n🧪 TEST 5: Streamlit App Page Discovery Simulation")
    print("=" * 50)
    
    try:
        # Use the exact same logic as app.py
        ellie_root = r"C:\Users\rhode\source\repos\EllieEdwardsMarketingLeadgenSite"
        
        page_options = []
        page_data = {}
        
        if os.path.isdir(ellie_root):
            print("✅ TinaCMS root directory found")
            
            # Main pages (like app.py lines 26-35)
            for page_file in ["home.md", "about.md", "services.md", "contact.md", "blog.md", "case-studies.md", "faq.md"]:
                page_path = os.path.join(ellie_root, "content", page_file)
                if os.path.isfile(page_path):
                    page_name = page_file.replace(".md", "").replace("-", " ").title()
                    url_path = "/" + page_file.replace(".md", "").replace("home", "")
                    page_options.append(f"{page_name} ({url_path})")
                    page_data[f"{page_name} ({url_path})"] = {
                        "file_path": page_path,
                        "url": f"https://ellieedwardsmarketing.co.uk{url_path}"
                    }
            
            print(f"✅ Found {len(page_options)} main pages")
            
            # Service pages (like app.py lines 40-52)
            services_dir = os.path.join(ellie_root, "content", "services")
            if os.path.isdir(services_dir):
                for service_file in os.listdir(services_dir):
                    if service_file.endswith(".md"):
                        service_path = os.path.join(services_dir, service_file)
                        service_name = service_file.replace(".md", "").replace("-", " ").title()
                        url_path = f"/services/{service_file.replace('.md', '')}"
                        service_option = f"Service: {service_name} ({url_path})"
                        page_options.append(service_option)
                        page_data[service_option] = {
                            "file_path": service_path,
                            "url": f"https://ellieedwardsmarketing.co.uk{url_path}"
                        }
                
                print(f"✅ Found {len([p for p in page_options if p.startswith('Service:')])} service pages")
            
            print(f"✅ Total pages discovered: {len(page_options)}")
            
            # Look for brand-strategy specifically
            brand_strategy_option = None
            for option in page_options:
                if "brand-strategy" in option.lower():
                    brand_strategy_option = option
                    break
            
            if brand_strategy_option:
                print(f"✅ Found brand-strategy page: {brand_strategy_option}")
                print(f"   File path: {page_data[brand_strategy_option]['file_path']}")
                print(f"   URL: {page_data[brand_strategy_option]['url']}")
                return True
            else:
                print("❌ brand-strategy page not found in discovery")
                print("Available pages:")
                for option in page_options:
                    print(f"   - {option}")
                return False
        else:
            print("❌ TinaCMS root directory not found")
            return False
            
    except Exception as e:
        print(f"❌ ERROR in page discovery: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all comprehensive tests"""
    print("🚀 COMPREHENSIVE TINACMS SERP ANALYSIS TESTS")
    print("=" * 60)
    print("Testing the complete end-to-end workflow...")
    
    # Test 1: File paths
    brand_strategy_file, services_file = test_1_file_paths()
    if not services_file or not os.path.exists(services_file):
        print("\n❌ CRITICAL: Basic file paths are broken. Cannot continue.")
        return
    
    # Use brand-strategy if available, otherwise services.md
    test_file = brand_strategy_file if brand_strategy_file and os.path.exists(brand_strategy_file) else services_file
    print(f"\n📁 Using test file: {test_file}")
    
    # Test 2: Reading
    post = test_2_frontmatter_reading(test_file)
    if post is None:
        print("\n❌ CRITICAL: Cannot read frontmatter. Cannot continue.")
        return
    
    # Test 3: Writing
    write_success = test_3_frontmatter_writing(test_file, post)
    if not write_success:
        print("\n❌ CRITICAL: Cannot write frontmatter. Fix required.")
        return
    
    # Test 4: Verification
    verify_success = test_4_verification(test_file)
    if not verify_success:
        print("\n❌ CRITICAL: Data verification failed. Fix required.")
        return
    
    # Test 5: App simulation
    app_success = test_5_streamlit_app_simulation()
    
    # Final results
    print("\n" + "=" * 60)
    print("🏁 FINAL TEST RESULTS:")
    print("=" * 60)
    
    if write_success and verify_success and app_success:
        print("✅ ALL TESTS PASSED!")
        print("✅ TinaCMS SERP analysis saving should work correctly")
        print("✅ The Streamlit app should be able to save analysis results")
        print("\n🎯 Next steps:")
        print("   1. Test in the actual Streamlit app")
        print("   2. Run SERP analysis on services/brand-strategy")
        print("   3. Check TinaCMS admin for the saved fields")
    else:
        print("❌ SOME TESTS FAILED!")
        print(f"   Writing: {'✅' if write_success else '❌'}")
        print(f"   Verification: {'✅' if verify_success else '❌'}")
        print(f"   App Discovery: {'✅' if app_success else '❌'}")

if __name__ == "__main__":
    main()
