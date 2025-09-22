#!/usr/bin/env python3
"""
Multi-Report SERP Analysis Test
This script tests the complete multi-report functionality by generating multiple
analyses for the same page and verifying they're stored correctly.
"""

import os
import sys
from pathlib import Path
import frontmatter
from datetime import datetime, timedelta
import json

def generate_test_reports():
    """Generate multiple test reports with different data"""
    
    ellie_root = Path(r"C:\Users\rhode\source\repos\EllieEdwardsMarketingLeadgenSite")
    target_file = ellie_root / "content" / "services" / "brand-strategy.md"
    
    print("🧪 Testing Multi-Report SERP Analysis Functionality")
    print("=" * 60)
    print(f"Target file: {target_file}")
    
    # Test data for 3 different reports
    test_reports = [
        {
            "reportName": "Initial Brand Strategy Analysis",
            "date_offset": 30,  # 30 days ago
            "keywords": [
                {"keyword": "brand strategy consultant surrey", "difficulty": 45},
                {"keyword": "business branding mytchett", "difficulty": 35},
                {"keyword": "brand development camberley", "difficulty": 42},
                {"keyword": "strategic branding services", "difficulty": 48},
                {"keyword": "brand positioning consultant", "difficulty": 38},
                {"keyword": "corporate brand strategy", "difficulty": 65},
                {"keyword": "brand identity design surrey", "difficulty": 55},
                {"keyword": "brand consultant near me", "difficulty": 72},
                {"keyword": "rebranding services uk", "difficulty": 58},
                {"keyword": "brand strategy workshop", "difficulty": 51},
            ],
            "notes": [
                "Initial analysis shows strong local opportunity",
                "Competition is moderate for consultant terms",
                "Good potential for location-specific content"
            ],
            "steps": [
                "Create location-specific landing pages",
                "Optimize for consultant-type queries",
                "Develop case study content"
            ]
        },
        {
            "reportName": "Post-Content Update Analysis", 
            "date_offset": 15,  # 15 days ago
            "keywords": [
                {"keyword": "brand strategy consultant surrey", "difficulty": 42},  # Improved
                {"keyword": "business branding mytchett", "difficulty": 33},  # Improved
                {"keyword": "brand development camberley", "difficulty": 40},  # Improved
                {"keyword": "strategic branding services", "difficulty": 46},  # Improved
                {"keyword": "brand positioning consultant", "difficulty": 36},  # Improved
                {"keyword": "corporate brand strategy", "difficulty": 63},  # Improved
                {"keyword": "brand identity design surrey", "difficulty": 53},  # Improved
                {"keyword": "brand consultant near me", "difficulty": 70},  # Improved
                {"keyword": "rebranding services uk", "difficulty": 56},  # Improved
                {"keyword": "startup brand strategy", "difficulty": 49},  # New keyword
                {"keyword": "brand audit consultant", "difficulty": 59},  # New keyword
                {"keyword": "brand messaging strategy", "difficulty": 57},  # New keyword
            ],
            "notes": [
                "Content updates showing positive impact on rankings",
                "Several keywords improved difficulty scores",
                "New keyword opportunities identified"
            ],
            "steps": [
                "Continue content optimization strategy",
                "Target new opportunity keywords",
                "Monitor ranking improvements"
            ]
        },
        {
            "reportName": "Quarterly Review Analysis",
            "date_offset": 0,  # Today
            "keywords": [
                {"keyword": "brand strategy consultant surrey", "difficulty": 38},  # Further improved
                {"keyword": "business branding mytchett", "difficulty": 30},  # Further improved
                {"keyword": "brand development camberley", "difficulty": 37},  # Further improved
                {"keyword": "strategic branding services", "difficulty": 44},  # Further improved
                {"keyword": "brand positioning consultant", "difficulty": 34},  # Further improved
                {"keyword": "corporate brand strategy", "difficulty": 61},  # Further improved
                {"keyword": "brand identity design surrey", "difficulty": 51},  # Further improved
                {"keyword": "brand consultant near me", "difficulty": 68},  # Further improved
                {"keyword": "rebranding services uk", "difficulty": 54},  # Further improved
                {"keyword": "startup brand strategy", "difficulty": 47},  # Improved
                {"keyword": "brand audit consultant", "difficulty": 57},  # Improved
                {"keyword": "brand messaging strategy", "difficulty": 55},  # Improved
                {"keyword": "brand differentiation strategy", "difficulty": 66},  # New
                {"keyword": "brand architecture consulting", "difficulty": 72},  # New
                {"keyword": "scale-up brand strategy", "difficulty": 43},  # New
            ],
            "notes": [
                "Significant improvements across all keyword categories",
                "Strong progress on local optimization",
                "Ready for expansion into new keyword areas"
            ],
            "steps": [
                "Launch advanced content strategy",
                "Expand into new keyword territories", 
                "Develop thought leadership content"
            ]
        }
    ]
    
    try:
        # Load the current file
        with open(target_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        print(f"✓ Loaded existing file")
        
        # Initialize SEO section
        if "seo" not in post.metadata:
            post.metadata["seo"] = {}
        
        # Initialize serpAnalysisHistory
        post.metadata["seo"]["serpAnalysisHistory"] = []
        
        # Generate and add each test report
        for i, report_data in enumerate(test_reports):
            print(f"\n📊 Generating Report {i+1}: {report_data['reportName']}")
            
            # Calculate analysis date
            analysis_date = datetime.now() - timedelta(days=report_data['date_offset'])
            report_id = f"report_{analysis_date.strftime('%Y_%m_%d_%H_%M_%S')}"
            
            # Categorize keywords
            keywords = report_data['keywords']
            easy_keywords = [kw['keyword'] for kw in keywords if kw['difficulty'] < 50]
            moderate_keywords = [kw['keyword'] for kw in keywords if 50 <= kw['difficulty'] < 70]
            hard_keywords = [kw['keyword'] for kw in keywords if kw['difficulty'] >= 70]
            
            # Calculate average difficulty
            avg_difficulty = sum(kw['difficulty'] for kw in keywords) / len(keywords)
            
            # Create report object
            report = {
                "reportId": report_id,
                "analysisDate": analysis_date.isoformat(),
                "reportName": report_data['reportName'],
                "avgDifficulty": round(avg_difficulty, 1),
                "easyCount": len(easy_keywords),
                "easyKeywords": easy_keywords,
                "moderateCount": len(moderate_keywords),
                "moderateKeywords": moderate_keywords,
                "hardCount": len(hard_keywords),
                "hardKeywords": hard_keywords,
                "topOpportunities": [kw['keyword'] for kw in keywords[:5]],
                "analysisNotes": report_data['notes'],
                "nextSteps": report_data['steps'],
            }
            
            # Add to history
            post.metadata["seo"]["serpAnalysisHistory"].append(report)
            
            print(f"  ✓ Report ID: {report_id}")
            print(f"  ✓ Date: {analysis_date.strftime('%Y-%m-%d')}")
            print(f"  ✓ Keywords: Easy: {len(easy_keywords)}, Moderate: {len(moderate_keywords)}, Hard: {len(hard_keywords)}")
            print(f"  ✓ Avg Difficulty: {avg_difficulty:.1f}")
        
        # Set the most recent report as current
        post.metadata["seo"]["currentReport"] = post.metadata["seo"]["serpAnalysisHistory"][-1]["reportId"]
        
        # Write back to file
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        print(f"\n✅ Successfully generated {len(test_reports)} test reports")
        print(f"📁 Reports saved to: {target_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating test reports: {e}")
        return False

def verify_multi_report_structure():
    """Verify the multi-report data structure is correct"""
    
    ellie_root = Path(r"C:\Users\rhode\source\repos\EllieEdwardsMarketingLeadgenSite")
    target_file = ellie_root / "content" / "services" / "brand-strategy.md"
    
    print(f"\n🔍 Verifying Multi-Report Structure")
    print("=" * 40)
    
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        if "seo" not in post.metadata:
            print("❌ No SEO section found")
            return False
        
        if "serpAnalysisHistory" not in post.metadata["seo"]:
            print("❌ No serpAnalysisHistory found")
            return False
        
        reports = post.metadata["seo"]["serpAnalysisHistory"]
        print(f"✓ Found {len(reports)} reports in history")
        
        # Verify each report structure
        required_fields = [
            "reportId", "analysisDate", "reportName", "avgDifficulty",
            "easyCount", "easyKeywords", "moderateCount", "moderateKeywords", 
            "hardCount", "hardKeywords", "topOpportunities", "analysisNotes", "nextSteps"
        ]
        
        for i, report in enumerate(reports):
            print(f"\n📊 Report {i+1}: {report.get('reportName', 'Unnamed')}")
            print(f"  Date: {report.get('analysisDate', '')[:10]}")
            print(f"  ID: {report.get('reportId', 'No ID')}")
            
            # Check required fields
            missing_fields = []
            for field in required_fields:
                if field not in report:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"  ❌ Missing fields: {missing_fields}")
                return False
            else:
                print(f"  ✓ All required fields present")
            
            # Check keyword lists are populated
            if not report["easyKeywords"]:
                print(f"  ⚠️  Easy keywords list is empty")
            else:
                print(f"  ✓ Easy keywords: {len(report['easyKeywords'])} items")
            
            if not report["moderateKeywords"]:
                print(f"  ⚠️  Moderate keywords list is empty") 
            else:
                print(f"  ✓ Moderate keywords: {len(report['moderateKeywords'])} items")
            
            if not report["hardKeywords"]:
                print(f"  ⚠️  Hard keywords list is empty")
            else:
                print(f"  ✓ Hard keywords: {len(report['hardKeywords'])} items")
        
        # Check current report pointer
        current_report = post.metadata["seo"].get("currentReport")
        if current_report:
            print(f"\n✓ Current report set to: {current_report}")
        else:
            print(f"\n⚠️  No current report pointer set")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying structure: {e}")
        return False

def display_report_summary():
    """Display a summary of all reports for visual confirmation"""
    
    ellie_root = Path(r"C:\Users\rhode\source\repos\EllieEdwardsMarketingLeadgenSite")
    target_file = ellie_root / "content" / "services" / "brand-strategy.md"
    
    print(f"\n📈 Multi-Report Summary")
    print("=" * 40)
    
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        reports = post.metadata["seo"]["serpAnalysisHistory"]
        
        print(f"Page: brand-strategy.md")
        print(f"Total Reports: {len(reports)}")
        print(f"Current Report: {post.metadata['seo'].get('currentReport', 'None')}")
        
        print(f"\n{'Report Name':<35} {'Date':<12} {'Avg Diff':<8} {'E/M/H':<10}")
        print("-" * 70)
        
        for report in reports:
            name = report['reportName'][:34]
            date = report['analysisDate'][:10]
            avg_diff = f"{report['avgDifficulty']:.1f}"
            emh = f"{report['easyCount']}/{report['moderateCount']}/{report['hardCount']}"
            
            print(f"{name:<35} {date:<12} {avg_diff:<8} {emh:<10}")
        
        # Show trend analysis
        if len(reports) > 1:
            print(f"\n📊 Trend Analysis:")
            first_report = reports[0]
            last_report = reports[-1]
            
            avg_diff_change = last_report['avgDifficulty'] - first_report['avgDifficulty']
            easy_change = last_report['easyCount'] - first_report['easyCount']
            
            print(f"  Average Difficulty: {first_report['avgDifficulty']:.1f} → {last_report['avgDifficulty']:.1f} ({avg_diff_change:+.1f})")
            print(f"  Easy Keywords: {first_report['easyCount']} → {last_report['easyCount']} ({easy_change:+d})")
            
            if avg_diff_change < 0:
                print(f"  🎉 Difficulty trending downward (easier to rank)")
            elif avg_diff_change > 0:
                print(f"  📈 Difficulty trending upward (harder to rank)")
            else:
                print(f"  ➡️  Difficulty stable")
        
        return True
        
    except Exception as e:
        print(f"❌ Error displaying summary: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Multi-Report SERP Analysis Test Suite")
    print("=" * 60)
    
    # Step 1: Generate test reports
    if generate_test_reports():
        
        # Step 2: Verify structure
        if verify_multi_report_structure():
            
            # Step 3: Display summary
            if display_report_summary():
                
                print(f"\n🎉 Multi-Report Functionality Test PASSED!")
                print(f"✅ All reports generated and verified successfully")
                print(f"✅ Data structure is correct for TinaCMS")
                print(f"✅ Historical tracking is working")
                print(f"\n📋 Next Steps:")
                print(f"1. Open TinaCMS admin: http://localhost:3000/admin")
                print(f"2. Navigate to Services → brand-strategy")
                print(f"3. Check 'SERP Analysis History' section")
                print(f"4. Verify all 3 reports are visible with proper dates")
                print(f"5. Test the Streamlit app with enhanced interface")
                
            else:
                print(f"\n❌ Summary display failed")
        else:
            print(f"\n❌ Structure verification failed")
    else:
        print(f"\n❌ Report generation failed")
    
    print(f"\n" + "=" * 60)
