#!/usr/bin/env python3
"""
Test script to diagnose TinaCMS frontmatter saving issues
"""

import os
import sys
import frontmatter
from datetime import datetime
from pathlib import Path

# Add the streamlit_app directory to path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'streamlit_app'))

def test_file_paths():
    """Test if we can find the TinaCMS content files"""
    print("=== Testing File Paths ===")
    
    # Test the path to the TinaCMS site
    tinacms_path = r"C:\Users\rhode\source\repos\EllieEdwardsMarketingLeadgenSite"
    content_path = os.path.join(tinacms_path, "content")
    
    print(f"TinaCMS site path: {tinacms_path}")
    print(f"TinaCMS site exists: {os.path.exists(tinacms_path)}")
    print(f"Content directory: {content_path}")
    print(f"Content directory exists: {os.path.exists(content_path)}")
    
    # Test specific files
    services_file = os.path.join(content_path, "services.md")
    print(f"Services file: {services_file}")
    print(f"Services file exists: {os.path.exists(services_file)}")
    
    # List content directory
    if os.path.exists(content_path):
        print(f"Content directory contents: {os.listdir(content_path)}")
    
    return content_path, services_file

def test_frontmatter_reading(file_path):
    """Test reading frontmatter from a file"""
    print(f"\n=== Testing Frontmatter Reading: {file_path} ===")
    
    if not os.path.exists(file_path):
        print(f"ERROR: File does not exist: {file_path}")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        print(f"Successfully read frontmatter")
        print(f"Content length: {len(post.content)}")
        print(f"Metadata keys: {list(post.metadata.keys())}")
        
        # Check for SEO section
        if 'seo' in post.metadata:
            seo = post.metadata['seo']
            print(f"SEO section exists with keys: {list(seo.keys())}")
            
            # Check for our SERP analysis fields
            if 'serpAnalysis' in seo:
                print(f"serpAnalysis already exists: {seo['serpAnalysis']}")
            else:
                print("serpAnalysis field not found in seo section")
                
            if 'lastAnalysisDate' in seo:
                print(f"lastAnalysisDate already exists: {seo['lastAnalysisDate']}")
            else:
                print("lastAnalysisDate field not found in seo section")
        else:
            print("No seo section found in frontmatter")
            
        return post
    
    except Exception as e:
        print(f"ERROR reading frontmatter: {e}")
        return None

def test_frontmatter_writing(file_path, post):
    """Test writing frontmatter to a file"""
    print(f"\n=== Testing Frontmatter Writing: {file_path} ===")
    
    if post is None:
        print("ERROR: No post object to write")
        return False
    
    try:
        # Create backup
        backup_path = file_path + ".backup"
        if os.path.exists(file_path):
            import shutil
            shutil.copy2(file_path, backup_path)
            print(f"Created backup: {backup_path}")
        
        # Add test SERP analysis data
        if 'seo' not in post.metadata:
            post.metadata['seo'] = {}
        
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
        
        post.metadata['seo']['serpAnalysis'] = test_analysis
        post.metadata['seo']['lastAnalysisDate'] = datetime.now().isoformat()
        
        # Write the file
        with open(file_path, 'w', encoding='utf-8') as f:
            frontmatter.dump(post, f)
        
        print("Successfully wrote frontmatter with test data")
        
        # Verify by reading back
        with open(file_path, 'r', encoding='utf-8') as f:
            verify_post = frontmatter.load(f)
        
        if 'seo' in verify_post.metadata and 'serpAnalysis' in verify_post.metadata['seo']:
            print("✅ Verification successful - data was written and can be read back")
            print(f"Saved serpAnalysis: {verify_post.metadata['seo']['serpAnalysis']}")
            return True
        else:
            print("❌ Verification failed - data was not saved correctly")
            return False
            
    except Exception as e:
        print(f"ERROR writing frontmatter: {e}")
        return False

def test_streamlit_integration():
    """Test the actual saving function from the Streamlit app"""
    print(f"\n=== Testing Streamlit Integration ===")
    
    try:
        # Import the content loader
        from content_loader import load_page_content, get_available_pages
        
        # Test loading pages
        pages = get_available_pages()
        print(f"Available pages: {len(pages)}")
        for page in pages[:5]:  # Show first 5
            print(f"  - {page}")
        
        # Test loading a specific page
        if "services/brand-strategy" in [p.split('/')[-1] for p in pages]:
            page_url = "services/brand-strategy"
            content = load_page_content(page_url)
            if content:
                print(f"✅ Successfully loaded content for {page_url}")
                print(f"Keywords found: {content.get('keywords', [])}")
            else:
                print(f"❌ Failed to load content for {page_url}")
        
        return True
        
    except Exception as e:
        print(f"ERROR testing Streamlit integration: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🔍 TinaCMS SERP Analysis Saving Diagnostic Tool")
    print("=" * 60)
    
    # Test 1: File paths
    content_path, services_file = test_file_paths()
    
    # Test 2: Frontmatter reading
    post = test_frontmatter_reading(services_file)
    
    # Test 3: Frontmatter writing
    if post:
        success = test_frontmatter_writing(services_file, post)
        if success:
            print("\n✅ Frontmatter reading/writing works correctly")
        else:
            print("\n❌ Frontmatter writing failed")
    
    # Test 4: Streamlit integration
    test_streamlit_integration()
    
    print("\n" + "=" * 60)
    print("🏁 Diagnostic complete!")

if __name__ == "__main__":
    main()
