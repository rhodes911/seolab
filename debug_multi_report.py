#!/usr/bin/env python3
"""
Debug Multi-Report Saving
Test if the Streamlit app is correctly saving to the new structure
"""

import os
import sys
from pathlib import Path
import frontmatter
from datetime import datetime

def check_current_file_structure():
    """Check the current structure of brand-strategy.md"""
    
    ellie_root = Path(r"C:\Users\rhode\source\repos\EllieEdwardsMarketingLeadgenSite")
    target_file = ellie_root / "content" / "services" / "brand-strategy.md"
    
    print("🔍 Checking Current File Structure")
    print("=" * 50)
    print(f"File: {target_file}")
    
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        print(f"✓ File loaded successfully")
        print(f"📄 Total frontmatter fields: {len(post.metadata)}")
        
        # Check SEO section
        if "seo" in post.metadata:
            seo = post.metadata["seo"]
            print(f"✓ SEO section exists with {len(seo)} fields:")
            for key in seo.keys():
                value = seo[key]
                if isinstance(value, list):
                    print(f"  - {key}: list with {len(value)} items")
                elif isinstance(value, dict):
                    print(f"  - {key}: dict with {len(value)} fields")
                else:
                    print(f"  - {key}: {type(value).__name__} = {str(value)[:50]}...")
            
            # Check specifically for serpAnalysisHistory
            if "serpAnalysisHistory" in seo:
                history = seo["serpAnalysisHistory"]
                print(f"✅ serpAnalysisHistory found with {len(history)} reports")
                for i, report in enumerate(history):
                    print(f"  Report {i+1}: {report.get('reportName', 'Unnamed')} ({report.get('analysisDate', '')[:10]})")
            else:
                print(f"❌ serpAnalysisHistory NOT found in SEO section")
                print(f"Available SEO fields: {list(seo.keys())}")
        else:
            print(f"❌ No SEO section found")
            print(f"Available frontmatter fields: {list(post.metadata.keys())}")
        
        return post
        
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return None

def simulate_streamlit_save():
    """Simulate what the Streamlit app should do when saving"""
    
    ellie_root = Path(r"C:\Users\rhode\source\repos\EllieEdwardsMarketingLeadgenSite")
    target_file = ellie_root / "content" / "services" / "brand-strategy.md"
    
    print(f"\n🧪 Simulating Streamlit Save Process")
    print("=" * 50)
    
    try:
        # Load current page (same as Streamlit)
        with open(target_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        print(f"✓ Loaded file")
        
        # Ensure SEO section exists (same as Streamlit)
        if "seo" not in post.metadata:
            post.metadata["seo"] = {}
            print(f"✓ Created SEO section")
        else:
            print(f"✓ SEO section already exists")
        
        # Initialize serpAnalysisHistory if it doesn't exist (same as Streamlit)
        if "serpAnalysisHistory" not in post.metadata["seo"]:
            post.metadata["seo"]["serpAnalysisHistory"] = []
            print(f"✓ Initialized serpAnalysisHistory")
        else:
            print(f"✓ serpAnalysisHistory already exists with {len(post.metadata['seo']['serpAnalysisHistory'])} reports")
        
        # Generate test report (same as Streamlit)
        report_id = f"debug_report_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        analysis_date = datetime.now().isoformat()
        
        new_report = {
            "reportId": report_id,
            "analysisDate": analysis_date,
            "reportName": "Debug Test Report",
            "avgDifficulty": 55.5,
            "easyCount": 3,
            "easyKeywords": ["test easy keyword 1", "test easy keyword 2", "test easy keyword 3"],
            "moderateCount": 2,
            "moderateKeywords": ["test moderate keyword 1", "test moderate keyword 2"],
            "hardCount": 1,
            "hardKeywords": ["test hard keyword 1"],
            "topOpportunities": ["opportunity 1", "opportunity 2"],
            "analysisNotes": ["Test analysis note"],
            "nextSteps": ["Test next step"],
        }
        
        print(f"✓ Created test report: {report_id}")
        
        # Add the new report to history (same as Streamlit)
        post.metadata["seo"]["serpAnalysisHistory"].append(new_report)
        print(f"✓ Added report to history")
        
        # Set as current active report (same as Streamlit)
        post.metadata["seo"]["currentReport"] = report_id
        print(f"✓ Set as current report")
        
        # Write back to file (same as Streamlit)
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        print(f"✅ Successfully saved debug report")
        print(f"📊 Total reports now: {len(post.metadata['seo']['serpAnalysisHistory'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during simulated save: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_save_result():
    """Verify the save worked by re-reading the file"""
    
    ellie_root = Path(r"C:\Users\rhode\source\repos\EllieEdwardsMarketingLeadgenSite")
    target_file = ellie_root / "content" / "services" / "brand-strategy.md"
    
    print(f"\n✅ Verifying Save Result")
    print("=" * 50)
    
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        if "seo" in post.metadata and "serpAnalysisHistory" in post.metadata["seo"]:
            reports = post.metadata["seo"]["serpAnalysisHistory"]
            print(f"✅ SUCCESS! Found {len(reports)} reports in serpAnalysisHistory")
            
            for i, report in enumerate(reports):
                print(f"  Report {i+1}:")
                print(f"    Name: {report.get('reportName', 'No name')}")
                print(f"    Date: {report.get('analysisDate', 'No date')[:19]}")
                print(f"    ID: {report.get('reportId', 'No ID')}")
                print(f"    Keywords: E:{report.get('easyCount', 0)} M:{report.get('moderateCount', 0)} H:{report.get('hardCount', 0)}")
            
            current = post.metadata["seo"].get("currentReport", "None")
            print(f"✅ Current report: {current}")
            
            return True
        else:
            print(f"❌ FAILED! No serpAnalysisHistory found after save")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying save: {e}")
        return False

if __name__ == "__main__":
    print("🚨 Multi-Report Debug & Fix")
    print("=" * 60)
    
    # Step 1: Check current structure
    current_post = check_current_file_structure()
    
    if current_post:
        # Step 2: Simulate save process
        if simulate_streamlit_save():
            # Step 3: Verify result
            if verify_save_result():
                print(f"\n🎉 Debug test PASSED! Multi-report saving is working.")
                print(f"📋 If Streamlit still isn't working:")
                print(f"1. Make sure you click 'Save Analysis & Keywords to TinaCMS'")
                print(f"2. Check that 'Save analysis results' is enabled")
                print(f"3. Ensure you have analysis results to save")
                print(f"4. Refresh TinaCMS admin and check SERP Analysis History")
            else:
                print(f"\n❌ Save verification failed")
        else:
            print(f"\n❌ Simulated save failed")
    else:
        print(f"\n❌ Could not load current file")
