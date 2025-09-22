#!/usr/bin/env python3
"""
Quick check of how many reports are actually in the file
"""

import frontmatter
from pathlib import Path

def check_reports():
    ellie_root = Path(r"C:\Users\rhode\source\repos\EllieEdwardsMarketingLeadgenSite")
    target_file = ellie_root / "content" / "services" / "brand-strategy.md"
    
    print("🔍 Checking Reports in brand-strategy.md")
    print("=" * 50)
    
    with open(target_file, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)
    
    if "seo" in post.metadata and "serpAnalysisHistory" in post.metadata["seo"]:
        reports = post.metadata["seo"]["serpAnalysisHistory"]
        print(f"📊 Total reports found: {len(reports)}")
        print()
        
        for i, report in enumerate(reports, 1):
            print(f"Report {i}:")
            print(f"  Name: {report.get('reportName', 'No name')}")
            print(f"  ID: {report.get('reportId', 'No ID')}")
            print(f"  Date: {report.get('analysisDate', 'No date')[:19]}")
            print(f"  Keywords: Easy:{report.get('easyCount', 0)} Moderate:{report.get('moderateCount', 0)} Hard:{report.get('hardCount', 0)}")
            print()
        
        current = post.metadata["seo"].get("currentReport", "None")
        print(f"🎯 Current active report: {current}")
        
    else:
        print("❌ No serpAnalysisHistory found")

if __name__ == "__main__":
    check_reports()
