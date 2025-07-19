"""
IT Domain - Minimal Version
Simplified project management with only essential features
"""

import streamlit as st
import pandas as pd
import sys
import json
from pathlib import Path
from datetime import datetime

# Add utils directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.database import (
    add_it_project_complete,
    add_it_project_minimal,
    get_it_projects_complete,
    get_it_projects_minimal,
    get_it_export_data_minimal,
    delete_it_project,
    validate_project_data_complete,
    validate_project_data_minimal
)
from utils.excel_handler import ExcelHandler
from utils.json_manager import JSONManager
from utils.data_converter import DataConverter

# Page configuration
st.set_page_config(
    page_title="IT Domain - Minimal",
    page_icon="📊",
    layout="wide"
)

def display_project_table():
    """Display all projects with option to view complete or minimal fields."""
    st.subheader("📋 Current Projects")
    
    # View mode selection
    view_mode = st.radio(
        "View Mode:",
        ["Minimal View (8 fields)", "Complete View (All 17 fields)"],
        horizontal=True
    )
    
    # Get projects data based on view mode
    if "Complete" in view_mode:
        projects_df = get_it_projects_complete()
    else:
        projects_df = get_it_projects_minimal()
    
    if projects_df.empty:
        st.info("No projects found. Add a project to get started.")
        return
    
    # Show basic stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Projects", len(projects_df))
    with col2:
        cn_count = len(projects_df[projects_df['business_unit'] == 'CN']) if 'business_unit' in projects_df.columns else 0
        st.metric("CN Projects", cn_count)
    with col3:
        pc_count = len(projects_df[projects_df['business_unit'] == 'PC']) if 'business_unit' in projects_df.columns else 0
        st.metric("PC Projects", pc_count)
    with col4:
        reuse_count = len(projects_df[projects_df.get('reuse_ip', '') == 'Y']) if 'reuse_ip' in projects_df.columns else 0
        st.metric("Reused IPs", reuse_count)
    
    # Display table
    st.dataframe(projects_df, use_container_width=True, height=400)
    
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
    """Display comprehensive form to add new project with all 17 IT Domain fields."""
    st.subheader("➕ Add New Project")
    st.write("Enter project information - all 17 IT Domain fields:")
    
    with st.form("add_project_form"):
        # Core Project Information
        st.markdown("### 📋 Core Project Information")
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input(
                "Project Name *", 
                help="Required. Must be unique identifier for the project."
            )
        with col2:
            alternative_name = st.text_input(
                "Alternative Name",
                help="Alternative project designation if needed"
            )
        
        # Project Specification Fields  
        st.markdown("### 🔧 Project Specifications")
        col1, col2, col3 = st.columns(3)
        with col1:
            spip_ip = st.text_input(
                "SPIP IP",
                help="IP classification from project management system"
            )
        with col2:
            ip = st.text_input(
                "IP",
                help="IP component name (e.g., AFE, DSP, PCIe)"
            )
        with col3:
            ip_postfix = st.text_input(
                "IP Postfix",
                help="IP variant identifier (e.g., 'v2', 'support 4/4')"
            )
        
        ip_subtype = st.selectbox(
            "IP Subtype",
            ["default", "gen2x1"],
            help="IP subtype classification"
        )
        
        # Personnel Assignment Fields
        st.markdown("### 👥 Personnel Assignments")
        col1, col2, col3 = st.columns(3)
        with col1:
            dv_engineer = st.text_input(
                "DV Engineer",
                help="Design verification engineer"
            )
        with col2:
            digital_designer = st.text_input(
                "Digital Designer",
                help="Digital design engineer"
            )
        with col3:
            analog_designer = st.text_input(
                "Analog Designer", 
                help="Analog design engineer"
            )
        
        business_unit = st.selectbox(
            "Business Unit",
            ["", "CN", "PC"],
            help="Business unit designation (CN: China team, PC: PC team)"
        )
        
        # Documentation Fields
        st.markdown("### 📚 Documentation & Links")
        col1, col2 = st.columns(2)
        with col1:
            spip_url = st.text_input(
                "SPIP URL",
                help="JIRA/SPIP project tracking URL (must start with http)"
            )
        with col2:
            wiki_url = st.text_input(
                "Wiki URL",
                help="Project wiki documentation URL (must start with http)"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            spec_version = st.text_input(
                "Spec Version",
                help="Specification document version (e.g., v1.0, v2.1)"
            )
        with col2:
            spec_path = st.text_input(
                "Spec Path",
                help="Path to specification document"
            )
        
        # IP Management Fields
        st.markdown("### 🔄 IP Management")
        col1, col2 = st.columns(2)
        with col1:
            inherit_from_ip = st.text_input(
                "Inherit from IP",
                help="Parent IP project reference if IP is inherited"
            )
        with col2:
            reuse_ip = st.selectbox(
                "Reuse IP",
                ["", "Y", "N"],
                help="IP reuse indicator (Y: reused, N: new development)"
            )
        
        submitted = st.form_submit_button("Add Project", type="primary")
        
        if submitted:
            # Prepare project data with all 17 fields
            project_data = {
                'project_name': project_name.strip(),
                'spip_ip': spip_ip.strip(),
                'ip': ip.strip(),
                'ip_postfix': ip_postfix.strip(),
                'ip_subtype': ip_subtype,
                'alternative_name': alternative_name.strip(),
                'dv_engineer': dv_engineer.strip(),
                'digital_designer': digital_designer.strip(),
                'analog_designer': analog_designer.strip(),
                'business_unit': business_unit,
                'spip_url': spip_url.strip(),
                'wiki_url': wiki_url.strip(),
                'spec_version': spec_version.strip(),
                'spec_path': spec_path.strip(),
                'inherit_from_ip': inherit_from_ip.strip(),
                'reuse_ip': reuse_ip
            }
            
            # Validate data
            errors = validate_project_data_complete(project_data)
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Add project
                if add_it_project_complete(project_data):
                    st.success(f"Successfully added project: {project_name}")
                    st.rerun()
                else:
                    st.error("Failed to add project. Project name might already exist.")


def display_import():
    """Display import functionality for Excel and JSON files."""
    st.subheader("📥 Import Data")
    
    # Import type selection
    import_type = st.radio(
        "Select import type:",
        ["Excel File", "JSON File"],
        horizontal=True
    )
    
    # Initialize handlers
    excel_handler = ExcelHandler()
    json_manager = JSONManager()
    data_converter = DataConverter()
    
    if import_type == "Excel File":
        uploaded_file = st.file_uploader(
            "Choose an Excel file",
            type=['xlsx', 'xls', 'xlsm'],
            help="Upload an Excel file containing project data"
        )
        
        if uploaded_file is not None:
            # Save temporary file
            temp_path = excel_handler.save_temp_file(uploaded_file, uploaded_file.name)
            
            # Validate file
            is_valid, message = excel_handler.validate_excel_file(temp_path)
            if not is_valid:
                st.error(f"Invalid file: {message}")
                return
            
            # Get sheet names
            try:
                sheet_names = excel_handler.get_sheet_names(temp_path)
                selected_sheet = st.selectbox("Select sheet:", sheet_names)
                
                # Read data
                df = excel_handler.read_excel_data(temp_path, selected_sheet)
                
                # Show preview
                st.write(f"Found {len(df)} records in the file")
                with st.expander("Preview Data"):
                    st.dataframe(excel_handler.preview_data(df, 20))
                
                # Column mapping
                st.subheader("Column Mapping")
                st.write("Map Excel columns to IT Domain fields:")
                
                # Required fields for IT Domain
                it_fields = [
                    'project_name', 'spip_ip', 'ip', 'ip_postfix', 'ip_subtype',
                    'alternative_name', 'dv_engineer', 'digital_designer', 
                    'analog_designer', 'business_unit', 'spip_url', 'wiki_url',
                    'spec_version', 'spec_path', 'inherit_from_ip', 'reuse_ip'
                ]
                
                # Create mapping interface
                column_mapping = {}
                excel_columns = [''] + list(df.columns)
                
                col1, col2 = st.columns(2)
                for i, field in enumerate(it_fields):
                    with col1 if i % 2 == 0 else col2:
                        mapped_col = st.selectbox(
                            f"{field}{'*' if field == 'project_name' else ''}:",
                            excel_columns,
                            key=f"map_{field}"
                        )
                        if mapped_col:
                            column_mapping[field] = mapped_col
                
                # Import options
                st.subheader("Import Options")
                merge_strategy = st.selectbox(
                    "Merge Strategy:",
                    ["Add New Only", "Update Existing", "Replace All"],
                    help="How to handle existing records"
                )
                
                split_dv_engineers = st.checkbox(
                    "Split comma-separated DV engineers",
                    help="Create separate records for each DV engineer if comma-separated"
                )
                
                save_to_json = st.checkbox(
                    "Also save as JSON backup",
                    value=True,
                    help="Save imported data as JSON file for backup"
                )
                
                # Import button
                if st.button("Import Data", type="primary"):
                    try:
                        # Map columns
                        mapped_df = pd.DataFrame()
                        for field, excel_col in column_mapping.items():
                            if excel_col:
                                mapped_df[field] = df[excel_col]
                            else:
                                mapped_df[field] = ''
                        
                        # Split DV engineers if requested
                        if split_dv_engineers and 'dv_engineer' in column_mapping:
                            mapped_df = excel_handler.split_comma_separated_values(
                                mapped_df, 'dv_engineer'
                            )
                        
                        # Validate required fields
                        if 'project_name' not in column_mapping or not column_mapping['project_name']:
                            st.error("Project name mapping is required!")
                            return
                        
                        # Save to JSON if requested
                        if save_to_json:
                            json_filename = f"it_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                            data_converter.excel_to_json(mapped_df, json_filename)
                            st.info(f"Data saved to JSON: {json_filename}.json")
                        
                        # Import to database
                        success_count = 0
                        error_count = 0
                        errors = []
                        
                        for _, row in mapped_df.iterrows():
                            project_data = row.to_dict()
                            # Clean empty strings
                            project_data = {k: v if v != '' else None for k, v in project_data.items()}
                            
                            # Validate
                            validation_errors = validate_project_data_complete(project_data)
                            if validation_errors:
                                error_count += 1
                                errors.extend(validation_errors)
                                continue
                            
                            # Add to database
                            if merge_strategy == "Replace All" and success_count == 0:
                                # Clear existing data (implement this in database.py if needed)
                                pass
                            
                            if add_it_project_complete(project_data):
                                success_count += 1
                            else:
                                error_count += 1
                                errors.append(f"Failed to add project: {project_data.get('project_name', 'Unknown')}")
                        
                        # Show results
                        st.success(f"Import completed! Successfully imported {success_count} projects.")
                        if error_count > 0:
                            st.warning(f"{error_count} projects failed to import.")
                            with st.expander("View Errors"):
                                for error in errors[:20]:  # Show first 20 errors
                                    st.error(error)
                        
                        # Clean up temp file
                        excel_handler.clean_temp_files(0)
                        
                    except Exception as e:
                        st.error(f"Import failed: {str(e)}")
            
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    else:  # JSON File
        # List available JSON files
        json_files = json_manager.list_json_files()
        
        if json_files:
            st.write("Available JSON files:")
            
            # Create selection table
            selected_file = None
            for file_info in json_files:
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                with col1:
                    st.write(file_info['filename'])
                with col2:
                    st.write(f"Records: {file_info['record_count']}")
                with col3:
                    st.write(f"Modified: {file_info['modified'][:10]}")
                with col4:
                    if st.button("Import", key=f"import_{file_info['filename']}"):
                        selected_file = file_info['filename']
            
            if selected_file:
                try:
                    # Load JSON data
                    df = data_converter.json_to_dataframe(selected_file)
                    
                    # Import to database
                    success_count = 0
                    for _, row in df.iterrows():
                        project_data = row.to_dict()
                        if add_it_project_complete(project_data):
                            success_count += 1
                    
                    st.success(f"Successfully imported {success_count} projects from {selected_file}")
                    
                except Exception as e:
                    st.error(f"Import failed: {str(e)}")
        
        else:
            st.info("No JSON files found. Import an Excel file first to create JSON backups.")


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
    
    # Export options
    st.subheader("Export Options")
    save_json_backup = st.checkbox("Save JSON backup", value=True, 
                                  help="Save a JSON backup in addition to downloading")
    
    # Export buttons
    col1, col2, col3 = st.columns(3)
    
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
    
    with col3:
        # JSON export
        data_converter = DataConverter()
        json_data = data_converter.excel_to_json(export_data)
        json_str = json.dumps(json_data, indent=2, default=str)
        st.download_button(
            label="📋 Download JSON",
            data=json_str,
            file_name=f"it_domain_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    # Save JSON backup if requested
    if save_json_backup:
        json_manager = JSONManager()
        filename = f"it_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        json_manager.save_to_json(export_data, filename)
        st.success(f"JSON backup saved as: {filename}.json")


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
            ["View Projects", "Add Project", "Import Data", "Export Data"],
            help="Choose what you want to do"
        )
    
    # Main content based on mode
    if mode == "View Projects":
        display_project_table()
    elif mode == "Add Project":
        display_add_project()
    elif mode == "Import Data":
        display_import()
    elif mode == "Export Data":
        display_export()
    
    # Footer
    st.markdown("---")
    st.markdown("*IT Domain - Minimal DV Management System*")


if __name__ == "__main__":
    main()