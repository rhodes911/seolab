import json
import streamlit as st
import os, re
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
import uuid
from io import BytesIO
# Import FPDF
try:
    from fpdf2 import FPDF
except ImportError:
    try:
        from fpdf import FPDF
    except ImportError:
        # Create a fallback FPDF class if neither module is installed
        class FPDF:
            def __init__(self):
                pass
            def add_page(self):
                pass
            def set_font(self, *args, **kwargs):
                pass
            def cell(self, *args, **kwargs):
                pass
            def multi_cell(self, *args, **kwargs):
                pass
            def ln(self, *args, **kwargs):
                pass
            def output(self, *args, **kwargs):
                return b""

import base64

import state

# Function to create a PDF case study report
def generate_case_study_pdf(slug: str, case_study_id: str, lesson_title: str) -> BytesIO:
    """
    Generate a PDF report for a case study
    
    Args:
        slug: Lesson slug
        case_study_id: Case study ID
        lesson_title: Title of the lesson
    
    Returns:
        BytesIO object containing the PDF
    """
    # Get case study data
    case_studies = state.get_case_studies(slug)
    if case_study_id not in case_studies:
        raise ValueError(f"Case study {case_study_id} not found")
    
    case_study = case_studies[case_study_id]
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Add title
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 20, "SEO Lab Case Study", ln=True, align="C")
    
    # Add project info
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 15, case_study.get("project_name", "Untitled Project"), ln=True)
    
    # Add metadata
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 10, f"Created: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.cell(0, 10, f"Context: {case_study.get('context', 'General')}", ln=True)
    pdf.cell(0, 10, f"Lesson: {lesson_title}", ln=True)
    pdf.ln(5)
    
    # Add sections
    for section, content in case_study.items():
        # Skip metadata fields
        if section in ["context", "project_name", "created_at"]:
            continue
            
        # Format section title
        section_title = section.replace("_", " ").title()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 15, section_title, ln=True)
        
        # Format content
        pdf.set_font("Helvetica", "", 12)
        
        # Handle different content types
        if isinstance(content, str):
            pdf.multi_cell(0, 10, content)
        elif isinstance(content, list):
            for item in content:
                pdf.cell(0, 10, f"• {item}", ln=True)
        elif isinstance(content, dict):
            for key, value in content.items():
                k = key.replace("_", " ").title()
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 10, k, ln=True)
                pdf.set_font("Helvetica", "", 12)
                
                if isinstance(value, str):
                    pdf.multi_cell(0, 10, value)
                elif isinstance(value, list):
                    for item in value:
                        pdf.cell(0, 10, f"• {item}", ln=True)
                        
        pdf.ln(5)
    
    # Generate PDF to memory
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    
    return pdf_output

def case_study_builder(slug: str, context: str = ""):
    """
    Interactive case study builder
    
    Args:
        slug: Page slug
        context: Context from preset (General, Local, E-commerce)
    """
    st.markdown("## 📊 Case Study Builder")
    st.markdown("Create a structured SEO case study to apply concepts from this lesson.")
    
    # Get or create case study ID
    if "current_case_study" not in st.session_state:
        st.session_state.current_case_study = str(uuid.uuid4())
    
    case_study_id = st.session_state.current_case_study
    
    # Get existing data or initialize
    case_studies = state.get_case_studies(slug)
    case_study = case_studies.get(case_study_id, {})
    
    # Set context from preset if available
    if context and "context" not in case_study:
        case_study["context"] = context
    
    # Project information
    st.subheader("Project Information")
    project_name = st.text_input(
        "Project Name", 
        value=case_study.get("project_name", ""),
        key=f"cs_{case_study_id}_name"
    )
    
    if project_name:
        case_study["project_name"] = project_name
    
    # Context selection if not set by preset
    if not context:
        context_options = ["General", "Local Business", "E-commerce"]
        selected_context = st.selectbox(
            "SEO Context", 
            options=context_options,
            index=context_options.index(case_study.get("context", "General")) if "context" in case_study else 0,
            key=f"cs_{case_study_id}_context"
        )
        case_study["context"] = selected_context
    
    # Website details
    st.subheader("Website Details")
    website_url = st.text_input(
        "Website URL", 
        value=case_study.get("website_url", ""),
        key=f"cs_{case_study_id}_url"
    )
    if website_url:
        case_study["website_url"] = website_url
    
    website_description = st.text_area(
        "Website Description", 
        value=case_study.get("website_description", ""),
        key=f"cs_{case_study_id}_description"
    )
    if website_description:
        case_study["website_description"] = website_description
    
    # SEO Objectives
    st.subheader("SEO Objectives")
    primary_goals = st.text_area(
        "Primary Goals", 
        value=case_study.get("primary_goals", ""),
        key=f"cs_{case_study_id}_goals",
        help="What are you trying to achieve with SEO? (e.g., increase organic traffic, improve rankings for specific keywords)"
    )
    if primary_goals:
        case_study["primary_goals"] = primary_goals
    
    # Target keywords
    target_keywords = st.text_area(
        "Target Keywords", 
        value=case_study.get("target_keywords", ""),
        key=f"cs_{case_study_id}_keywords",
        help="List your primary and secondary target keywords"
    )
    if target_keywords:
        case_study["target_keywords"] = target_keywords
    
    # Current status
    st.subheader("Current Status")
    current_rankings = st.text_area(
        "Current Rankings", 
        value=case_study.get("current_rankings", ""),
        key=f"cs_{case_study_id}_rankings",
        help="Current position in search results for target keywords"
    )
    if current_rankings:
        case_study["current_rankings"] = current_rankings
    
    identified_issues = st.text_area(
        "Identified Issues", 
        value=case_study.get("identified_issues", ""),
        key=f"cs_{case_study_id}_issues",
        help="Technical issues, content gaps, etc."
    )
    if identified_issues:
        case_study["identified_issues"] = identified_issues
    
    # Strategy
    st.subheader("SEO Strategy")
    strategy = st.text_area(
        "Strategy Overview", 
        value=case_study.get("strategy", ""),
        key=f"cs_{case_study_id}_strategy",
        help="Overall approach to achieve objectives"
    )
    if strategy:
        case_study["strategy"] = strategy
    
    # Implementation plan
    st.subheader("Implementation Plan")
    implementation = st.text_area(
        "Implementation Steps", 
        value=case_study.get("implementation", ""),
        key=f"cs_{case_study_id}_implementation",
        help="Specific actions to be taken"
    )
    if implementation:
        case_study["implementation"] = implementation
    
    # Save button
    if st.button("Save Case Study", key=f"cs_{case_study_id}_save"):
        # Add timestamp
        case_study["created_at"] = datetime.now().isoformat()
        
        # Save to state
        state.save_case_study(slug, case_study_id, case_study)
        st.success("Case study saved!")
    
    # Display summary
    st.subheader("Case Study Summary")
    with st.expander("View Summary", expanded=True):
        if project_name:
            st.markdown(f"### {project_name}")
            st.markdown(f"**Context:** {case_study.get('context', 'General')}")
            
            if website_url:
                st.markdown(f"**Website:** {website_url}")
            
            if primary_goals:
                st.markdown("#### Objectives")
                st.markdown(primary_goals)
            
            if target_keywords:
                st.markdown("#### Target Keywords")
                st.markdown(target_keywords)
            
            if identified_issues:
                st.markdown("#### Issues Identified")
                st.markdown(identified_issues)
            
            if strategy:
                st.markdown("#### Strategy")
                st.markdown(strategy)
            
            if implementation:
                st.markdown("#### Implementation Plan")
                st.markdown(implementation)
            
            # Export options
            col1, col2 = st.columns(2)
            
            with col1:
                # JSON export
                case_study_json = json.dumps(case_study, indent=2)
                st.download_button(
                    "Download as JSON",
                    case_study_json,
                    file_name=f"seo_case_study_{slug}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    key=f"cs_{case_study_id}_download_json"
                )
            
            with col2:
                # PDF export
                try:
                    lesson_title = st.session_state.get("page_title", "SEO Lesson")
                    pdf_buffer = generate_case_study_pdf(slug, case_study_id, lesson_title)
                    st.download_button(
                        "Download as PDF",
                        pdf_buffer,
                        file_name=f"seo_case_study_{slug}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        key=f"cs_{case_study_id}_download_pdf"
                    )
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
        else:
            st.info("Complete the form to see your case study summary")
