#!/usr/bin/env python3
"""
Clean Slate - Wipe All SERP Analysis Reports
This script will remove all existing SERP analysis data from all service pages.
"""

import os
import sys
from pathlib import Path
import frontmatter
import glob

def wipe_all_serp_reports():
    """Remove all SERP analysis data from all service pages"""
    
    ellie_root = Path(r"C:\Users\rhode\source\repos\EllieEdwardsMarketingLeadgenSite")
    services_dir = ellie_root / "content" / "services"
    
    print(f"🧹 Wiping all SERP analysis reports from: {services_dir}")
    
    if not services_dir.exists():
        print(f"❌ Services directory not found: {services_dir}")
        return False
    
    # Find all markdown files in services directory
    service_files = list(services_dir.glob("*.md"))
    
    print(f"📄 Found {len(service_files)} service files")
    
    cleaned_count = 0
    
    for service_file in service_files:
        try:
            print(f"\n🔍 Processing: {service_file.name}")
            
            # Read the file
            with open(service_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # Check if it has SEO data
            if 'seo' in post.metadata:
                # Check if it has SERP analysis
                if 'serpAnalysis' in post.metadata['seo']:
                    print(f"  🗑️  Removing SERP analysis data")
                    del post.metadata['seo']['serpAnalysis']
                    
                    # Also remove lastAnalysisDate if it exists
                    if 'lastAnalysisDate' in post.metadata['seo']:
                        del post.metadata['seo']['lastAnalysisDate']
                    
                    # If SEO section is now empty except for metaTitle, we can leave it
                    # Write the cleaned file
                    with open(service_file, 'w', encoding='utf-8') as f:
                        f.write(frontmatter.dumps(post))
                    
                    print(f"  ✅ Cleaned {service_file.name}")
                    cleaned_count += 1
                else:
                    print(f"  ℹ️  No SERP analysis data found")
            else:
                print(f"  ℹ️  No SEO section found")
                
        except Exception as e:
            print(f"  ❌ Error processing {service_file.name}: {e}")
    
    print(f"\n🎉 Cleaning complete!")
    print(f"📊 Summary:")
    print(f"  - Files processed: {len(service_files)}")
    print(f"  - Files cleaned: {cleaned_count}")
    print(f"  - Files unchanged: {len(service_files) - cleaned_count}")
    
    return True

def verify_clean_slate():
    """Verify that all SERP analysis data has been removed"""
    
    ellie_root = Path(r"C:\Users\rhode\source\repos\EllieEdwardsMarketingLeadgenSite")
    services_dir = ellie_root / "content" / "services"
    
    print(f"\n🔍 Verifying clean slate...")
    
    service_files = list(services_dir.glob("*.md"))
    serp_data_found = 0
    
    for service_file in service_files:
        try:
            with open(service_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            if 'seo' in post.metadata and 'serpAnalysis' in post.metadata['seo']:
                print(f"  ⚠️  SERP analysis still found in: {service_file.name}")
                serp_data_found += 1
                
        except Exception as e:
            print(f"  ❌ Error checking {service_file.name}: {e}")
    
    if serp_data_found == 0:
        print(f"  ✅ Clean slate verified - no SERP analysis data found")
        return True
    else:
        print(f"  ❌ Clean slate failed - {serp_data_found} files still have SERP data")
        return False

if __name__ == "__main__":
    print("🧹 Starting Clean Slate Operation")
    print("=" * 50)
    
    # Step 1: Wipe all reports
    if wipe_all_serp_reports():
        
        # Step 2: Verify clean slate
        if verify_clean_slate():
            print("\n🎉 SUCCESS! All SERP analysis reports have been wiped.")
            print("✨ You now have a clean slate to start fresh.")
        else:
            print("\n⚠️  Warning: Some SERP data may still exist.")
    else:
        print("\n❌ Failed to wipe SERP analysis reports.")
    
    print("\n📋 Next steps:")
    print("1. Enhanced multi-report data structure will be implemented")
    print("2. TinaCMS schema will be updated for historical reports")
    print("3. Streamlit app will be enhanced for report history")
