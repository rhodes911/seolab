#!/usr/bin/env python3
"""
Test Streamlit Save Functionality
Debug and test the actual save button in the SERP analysis tool
"""

import os
import sys
from pathlib import Path
import frontmatter
from datetime import datetime

def test_streamlit_save_logic():
    """Test the exact save logic from Streamlit"""
    
    print("🧪 Testing Streamlit Save Logic")
    print("=" * 50)
    
    # Simulate what Streamlit should have available
    ellie_root = Path(r"C:\Users\rhode\source\repos\EllieEdwardsMarketingLeadgenSite")
    target_file = ellie_root / "content" / "services" / "brand-strategy.md"
    
    # Mock data that Streamlit would have from analysis
    report_name = "Test SERP Analysis"
    avg = 45.2
    easy = 5
    easy_keywords = ["easy seo keyword", "local seo tips", "seo basics"]
    moderate = 3
    moderate_keywords = ["seo strategy", "content marketing", "link building"]
    hard = 2
    hard_keywords = ["enterprise seo", "technical seo audit"]
    opps = [
        {"keyword": "opportunity 1", "difficulty": 30},
        {"keyword": "opportunity 2", "difficulty": 35}
    ]
    bullets = ["Analysis note 1", "Analysis note 2"]
    steps = ["Next step 1", "Next step 2"]
    selected_winners = ["winning keyword 1", "winning keyword 2"]
    
    print(f"📁 Target file: {target_file}")
    print(f"📊 Mock analysis data prepared")
    
    try:
        # === EXACT STREAMLIT SAVE LOGIC ===
        print(f"\n🔄 Starting save process...")
        
        # Load current page
        print(f"📖 Loading file...")
        with open(target_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        print(f"✅ File loaded successfully")
        
        # Ensure SEO section exists
        if "seo" not in post.metadata:
            post.metadata["seo"] = {}
            print(f"✅ Created SEO section")
        else:
            print(f"✅ SEO section exists")
        
        # Initialize serpAnalysisHistory if it doesn't exist
        if "serpAnalysisHistory" not in post.metadata["seo"]:
            post.metadata["seo"]["serpAnalysisHistory"] = []
            print(f"✅ Initialized serpAnalysisHistory")
        else:
            existing_count = len(post.metadata["seo"]["serpAnalysisHistory"])
            print(f"✅ serpAnalysisHistory exists with {existing_count} reports")
        
        # Generate unique report ID
        report_id = f"report_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        analysis_date = datetime.now().isoformat()
        print(f"🆔 Generated report ID: {report_id}")
        
        # Create new report object
        new_report = {
            "reportId": report_id,
            "analysisDate": analysis_date,
            "reportName": report_name,
            "avgDifficulty": avg,
            "easyCount": easy,
            "easyKeywords": easy_keywords,
            "moderateCount": moderate,
            "moderateKeywords": moderate_keywords,
            "hardCount": hard,
            "hardKeywords": hard_keywords,
            "topOpportunities": [r["keyword"] for r in opps[:10]],
            "analysisNotes": bullets,
            "nextSteps": steps,
        }
        print(f"📝 Created report object")
        
        # Add the new report to history
        pre_count = len(post.metadata["seo"]["serpAnalysisHistory"])
        post.metadata["seo"]["serpAnalysisHistory"].append(new_report)
        post_count = len(post.metadata["seo"]["serpAnalysisHistory"])
        print(f"📈 Added to history: {pre_count} -> {post_count} reports")
        
        # Set as current active report
        post.metadata["seo"]["currentReport"] = report_id
        print(f"🎯 Set as current report")
        
        # Update winning keywords (maintain backward compatibility)
        if selected_winners:
            existing_winners = post.metadata["seo"].get("winningKeywords", [])
            combined_winners = list(set(existing_winners + selected_winners))
            post.metadata["seo"]["winningKeywords"] = combined_winners
            print(f"🏆 Updated winning keywords: {len(combined_winners)} total")
        
        # Write back to file
        print(f"💾 Writing to file...")
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        print(f"✅ File written successfully")
        
        # === SUCCESS MESSAGES (what Streamlit should show) ===
        success_msg = f"✅ Saved '{report_name}' to Service: Brand Strategy"
        if selected_winners:
            success_msg += f" with {len(selected_winners)} winning keywords"
        
        print(f"\n🎉 SUCCESS MESSAGE: {success_msg}")
        print(f"📊 Total reports for this page: {len(post.metadata['seo']['serpAnalysisHistory'])}")
        
        # Show report summary
        report_summary = {
            "reportId": report_id,
            "reportName": report_name,
            "analysisDate": analysis_date[:10],
            "keywordBreakdown": f"Easy: {easy}, Moderate: {moderate}, Hard: {hard}"
        }
        print(f"📋 Report Summary: {report_summary}")
        
        return True, report_id
        
    except Exception as e:
        print(f"❌ SAVE FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def verify_save_worked(report_id):
    """Verify the save actually worked by re-reading the file"""
    
    print(f"\n🔍 Verifying Save Result")
    print("=" * 50)
    
    ellie_root = Path(r"C:\Users\rhode\source\repos\EllieEdwardsMarketingLeadgenSite")
    target_file = ellie_root / "content" / "services" / "brand-strategy.md"
    
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        if "seo" in post.metadata and "serpAnalysisHistory" in post.metadata["seo"]:
            reports = post.metadata["seo"]["serpAnalysisHistory"]
            print(f"✅ Found {len(reports)} reports in serpAnalysisHistory")
            
            # Look for our specific report
            found_our_report = False
            for i, report in enumerate(reports):
                report_found_id = report.get('reportId', '')
                if report_found_id == report_id:
                    found_our_report = True
                    print(f"🎯 Found our test report at position {i+1}:")
                    print(f"    Name: {report.get('reportName', 'No name')}")
                    print(f"    Date: {report.get('analysisDate', 'No date')[:19]}")
                    print(f"    Keywords: E:{report.get('easyCount', 0)} M:{report.get('moderateCount', 0)} H:{report.get('hardCount', 0)}")
                    break
            
            if found_our_report:
                print(f"✅ VERIFICATION PASSED - Report saved correctly!")
                return True
            else:
                print(f"❌ VERIFICATION FAILED - Our report not found in saved data")
                print(f"📋 Available report IDs:")
                for report in reports:
                    print(f"    - {report.get('reportId', 'No ID')}")
                return False
        else:
            print(f"❌ VERIFICATION FAILED - No serpAnalysisHistory found")
            return False
            
    except Exception as e:
        print(f"❌ VERIFICATION ERROR: {e}")
        return False

def test_file_permissions():
    """Test if we can actually write to the target file"""
    
    print(f"\n🔒 Testing File Permissions")
    print("=" * 50)
    
    ellie_root = Path(r"C:\Users\rhode\source\repos\EllieEdwardsMarketingLeadgenSite")
    target_file = ellie_root / "content" / "services" / "brand-strategy.md"
    
    try:
        # Check if file exists
        if not target_file.exists():
            print(f"❌ File does not exist: {target_file}")
            return False
        
        print(f"✅ File exists: {target_file}")
        
        # Check if file is readable
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ File is readable ({len(content)} characters)")
        
        # Check if file is writable by creating a backup
        backup_content = content
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(backup_content)
        print(f"✅ File is writable")
        
        return True
        
    except Exception as e:
        print(f"❌ File permission error: {e}")
        return False

if __name__ == "__main__":
    print("🚨 Streamlit Save Functionality Test")
    print("=" * 60)
    
    # Step 1: Test file permissions
    if not test_file_permissions():
        print(f"\n❌ Cannot proceed - file permission issues")
        sys.exit(1)
    
    # Step 2: Test the save logic
    success, report_id = test_streamlit_save_logic()
    
    if success and report_id:
        # Step 3: Verify it worked
        if verify_save_worked(report_id):
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"✅ The Streamlit save button logic is working correctly")
            print(f"🔧 If users aren't seeing saves, check:")
            print(f"   1. Are they clicking 'Save Analysis & Keywords to TinaCMS'?")
            print(f"   2. Is the analysis checkbox enabled?")
            print(f"   3. Are there any JavaScript console errors in Streamlit?")
            print(f"   4. Is TinaCMS refreshed after saving?")
        else:
            print(f"\n❌ Save logic ran but verification failed")
    else:
        print(f"\n❌ Save logic failed to execute")
