#!/usr/bin/env python3
"""
Test if Streamlit can actually save from the UI
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add the streamlit_app directory to path to import modules
streamlit_app_dir = Path(__file__).parent / "streamlit_app"
sys.path.insert(0, str(streamlit_app_dir))

def main():
    st.title("🧪 Streamlit Save Test")
    
    st.write("This is a minimal test to check if Streamlit can save reports.")
    
    # Simulate the exact save process
    if st.button("Test Save Process"):
        try:
            import frontmatter
            from datetime import datetime
            
            # Target file
            ellie_root = Path(r"C:\Users\rhode\source\repos\EllieEdwardsMarketingLeadgenSite")
            target_file = ellie_root / "content" / "services" / "brand-strategy.md"
            
            st.info(f"📁 Target file: {target_file}")
            
            # Load file
            with open(target_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            st.success("✅ File loaded successfully")
            
            # Check SEO section
            if "seo" not in post.metadata:
                post.metadata["seo"] = {}
            
            if "serpAnalysisHistory" not in post.metadata["seo"]:
                post.metadata["seo"]["serpAnalysisHistory"] = []
            
            pre_count = len(post.metadata["seo"]["serpAnalysisHistory"])
            st.info(f"📊 Current reports: {pre_count}")
            
            # Create test report
            report_id = f"streamlit_test_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
            
            new_report = {
                "reportId": report_id,
                "analysisDate": datetime.now().isoformat(),
                "reportName": "Streamlit UI Test Report",
                "avgDifficulty": 42.0,
                "easyCount": 4,
                "easyKeywords": ["streamlit test 1", "streamlit test 2", "streamlit test 3", "streamlit test 4"],
                "moderateCount": 2,
                "moderateKeywords": ["moderate test 1", "moderate test 2"],
                "hardCount": 1,
                "hardKeywords": ["hard test 1"],
                "topOpportunities": ["opportunity test 1", "opportunity test 2"],
                "analysisNotes": ["Streamlit UI test note"],
                "nextSteps": ["Streamlit UI test step"],
            }
            
            # Add to history
            post.metadata["seo"]["serpAnalysisHistory"].append(new_report)
            post.metadata["seo"]["currentReport"] = report_id
            
            # Save file
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(frontmatter.dumps(post))
            
            post_count = len(post.metadata["seo"]["serpAnalysisHistory"])
            
            st.balloons()
            st.success(f"🎉 SAVE SUCCESSFUL!")
            st.success(f"📈 Reports: {pre_count} → {post_count}")
            st.success(f"🆔 Report ID: {report_id}")
            
            # Show all reports
            st.subheader("📋 All Reports in File:")
            for i, report in enumerate(post.metadata["seo"]["serpAnalysisHistory"]):
                st.write(f"{i+1}. **{report.get('reportName', 'No name')}** ({report.get('reportId', 'No ID')[:20]}...)")
            
        except Exception as e:
            st.error(f"❌ SAVE FAILED: {e}")
            st.exception(e)

if __name__ == "__main__":
    main()
