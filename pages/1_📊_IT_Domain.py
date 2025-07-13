"""
IT Domain - Minimal Version
Simplified project management with only essential features
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Add utils directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.database import (
    add_it_project_minimal,
    get_it_projects_minimal,
    get_it_export_data_minimal,
    delete_it_project,
    validate_project_data_minimal
)

# Page configuration
st.set_page_config(
    page_title="IT Domain - Minimal",
    page_icon="📊",
    layout="wide"
)

def display_project_table():
    """Display all projects in a simple table."""
    st.subheader("📋 Current Projects")
    
    # Get projects data
    projects_df = get_it_projects_minimal()
    
    if projects_df.empty:
        st.info("No projects found. Add a project to get started.")
        return
    
    # Show basic stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Projects", len(projects_df))
    with col2:
        cn_count = len(projects_df[projects_df['business_unit'] == 'CN'])
        st.metric("CN Projects", cn_count)
    with col3:
        pc_count = len(projects_df[projects_df['business_unit'] == 'PC'])
        st.metric("PC Projects", pc_count)
    
    # Display table
    st.dataframe(projects_df, use_container_width=True)
    
    # Delete functionality
    if not projects_df.empty:
        st.subheader("🗑️ Delete Project")
        project_options = {f"{row['project_name']} ({row['task_index']})": row['id'] 
                          for _, row in projects_df.iterrows()}
        
        selected_project = st.selectbox("Select project to delete:", [""] + list(project_options.keys()))
        
        if selected_project and st.button("Delete Selected Project", type="secondary"):
            if delete_it_project(project_options[selected_project]):
                st.success(f"Deleted project: {selected_project}")
                st.rerun()
            else:
                st.error("Failed to delete project")


def display_add_project():
    """Display simplified form to add new project."""
    st.subheader("➕ Add New Project")
    st.write("Enter the 5 essential project fields:")
    
    with st.form("add_project_form"):
        # Essential fields only
        project_name = st.text_input(
            "Project Name *", 
            help="Required. Must be unique."
        )
        
        dv_engineer = st.text_input(
            "DV Engineer",
            help="Design verification engineer"
        )
        
        business_unit = st.selectbox(
            "Business Unit",
            ["", "CN", "PC"],
            help="Business unit designation"
        )
        
        ip = st.text_input(
            "IP",
            help="IP name/identifier"
        )
        
        spip_url = st.text_input(
            "SPIP URL",
            help="Link to SPIP project page"
        )
        
        submitted = st.form_submit_button("Add Project")
        
        if submitted:
            # Prepare project data
            project_data = {
                'project_name': project_name.strip(),
                'dv_engineer': dv_engineer.strip(),
                'business_unit': business_unit,
                'ip': ip.strip(),
                'spip_url': spip_url.strip()
            }
            
            # Validate data
            errors = validate_project_data_minimal(project_data)
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Add project
                if add_it_project_minimal(project_data):
                    st.success(f"Successfully added project: {project_name}")
                    st.rerun()
                else:
                    st.error("Failed to add project. Project name might already exist.")


def display_export():
    """Display export functionality."""
    st.subheader("📤 Export Data")
    
    export_data = get_it_export_data_minimal()
    
    if export_data.empty:
        st.warning("No data to export")
        return
    
    # Show export preview
    st.write(f"Found {len(export_data)} projects to export")
    with st.expander("Preview Export Data"):
        st.dataframe(export_data)
    
    # Export buttons
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = export_data.to_csv(index=False)
        st.download_button(
            label="📊 Download CSV",
            data=csv_data,
            file_name=f"it_domain_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Excel export if openpyxl is available
        try:
            import openpyxl
            from io import BytesIO
            excel_buffer = BytesIO()
            export_data.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_buffer = excel_buffer.getvalue()
            st.download_button(
                label="📈 Download Excel",
                data=excel_buffer,
                file_name=f"it_domain_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except ImportError:
            st.info("Excel export not available (openpyxl not installed)")


def main():
    """Main function for IT Domain minimal interface."""
    
    # Header
    st.title("📊 IT Domain - Minimal")
    st.write("*Simple project management and data export*")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        mode = st.radio(
            "Select Mode:",
            ["View Projects", "Add Project", "Export Data"],
            help="Choose what you want to do"
        )
    
    # Main content based on mode
    if mode == "View Projects":
        display_project_table()
    elif mode == "Add Project":
        display_add_project()
    elif mode == "Export Data":
        display_export()
    
    # Footer
    st.markdown("---")
    st.markdown("*IT Domain - Minimal DV Management System*")


if __name__ == "__main__":
    main()