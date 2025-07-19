"""
NX Domain - Enhanced Version
Complete data import, coverage analysis, and TO Summary generation
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Add utils directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.database import (
    import_it_data_to_nx_complete,
    import_it_data_to_nx_minimal,
    get_nx_imported_data,
    get_nx_to_summary,
    get_nx_coverage_analysis,
    get_nx_stats
)
from utils.excel_handler import ExcelHandler
from utils.json_manager import JSONManager
from utils.data_converter import DataConverter

# Page configuration
st.set_page_config(
    page_title="NX Domain - Minimal",
    page_icon="📈",
    layout="wide"
)

def display_import_data():
    """Display CSV and Excel import functionality."""
    st.subheader("📥 Import IT Domain Data")
    
    # File type selection
    file_type = st.radio(
        "Select file type:",
        ["CSV File", "Excel File", "JSON File"],
        horizontal=True,
        help="Choose the type of file to import"
    )
    
    # Initialize handlers
    excel_handler = ExcelHandler()
    json_manager = JSONManager()
    data_converter = DataConverter()
    
    if file_type == "CSV File":
        st.write("Upload CSV file exported from IT Domain:")
        
        uploaded_file = st.file_uploader(
            "Choose CSV file from IT Domain export",
            type=['csv'],
            help="Select the CSV file exported from IT Domain"
        )
        
        if uploaded_file is not None:
            try:
                # Read CSV data
                csv_data = pd.read_csv(uploaded_file)
                
                st.success(f"✅ CSV file loaded successfully ({len(csv_data)} rows)")
                
                # Show preview
                with st.expander("Preview CSV Data"):
                    st.dataframe(csv_data)
                
                # Show column information
                st.write("**Available columns:**")
                cols_info = []
                for col in csv_data.columns:
                    non_empty = csv_data[col].notna().sum()
                    cols_info.append(f"• {col} ({non_empty} non-empty values)")
                st.write("\n".join(cols_info))
                
                # Import button
                if st.button("🔄 Import Data to NX Domain", type="primary"):
                    with st.spinner("Importing data..."):
                        if import_it_data_to_nx_complete(csv_data):
                            st.success(f"✅ Successfully imported {len(csv_data)} projects to NX Domain")
                            st.rerun()
                        else:
                            st.error("❌ Failed to import data. Check that project_name column exists.")
            
            except Exception as e:
                st.error(f"❌ Error reading CSV file: {str(e)}")
                st.write("Please ensure the file is a valid CSV exported from IT Domain.")
    
    elif file_type == "Excel File":
        st.write("Upload Excel file exported from IT Domain:")
        
        uploaded_file = st.file_uploader(
            "Choose Excel file from IT Domain export",
            type=['xlsx', 'xls', 'xlsm'],
            help="Select the Excel file exported from IT Domain"
        )
        
        if uploaded_file is not None:
            try:
                # Save temporary file
                temp_path = excel_handler.save_temp_file(uploaded_file, uploaded_file.name)
                
                # Validate file
                is_valid, message = excel_handler.validate_excel_file(temp_path)
                if not is_valid:
                    st.error(f"Invalid file: {message}")
                    return
                
                # Get sheet names
                sheet_names = excel_handler.get_sheet_names(temp_path)
                selected_sheet = st.selectbox("Select sheet:", sheet_names)
                
                # Read data
                excel_data = excel_handler.read_excel_data(temp_path, selected_sheet)
                
                st.success(f"✅ Excel file loaded successfully ({len(excel_data)} rows)")
                
                # Show preview
                with st.expander("Preview Excel Data"):
                    st.dataframe(excel_handler.preview_data(excel_data, 20))
                
                # Show column information
                st.write("**Available columns:**")
                cols_info = []
                for col in excel_data.columns:
                    non_empty = excel_data[col].notna().sum()
                    cols_info.append(f"• {col} ({non_empty} non-empty values)")
                st.write("\n".join(cols_info))
                
                # Import options
                st.subheader("Import Options")
                save_json_backup = st.checkbox(
                    "Save JSON backup",
                    value=True,
                    help="Save imported data as JSON backup"
                )
                
                # Import button
                if st.button("🔄 Import Data to NX Domain", type="primary"):
                    with st.spinner("Importing data..."):
                        # Save JSON backup if requested
                        if save_json_backup:
                            json_filename = f"nx_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                            data_converter.excel_to_json(excel_data, json_filename)
                            st.info(f"JSON backup saved: {json_filename}.json")
                        
                        # Import to database
                        if import_it_data_to_nx_complete(excel_data):
                            st.success(f"✅ Successfully imported {len(excel_data)} projects to NX Domain")
                            st.rerun()
                        else:
                            st.error("❌ Failed to import data. Check that project_name column exists.")
                        
                        # Clean up temp file
                        excel_handler.clean_temp_files(0)
            
            except Exception as e:
                st.error(f"❌ Error reading Excel file: {str(e)}")
                st.write("Please ensure the file is a valid Excel file exported from IT Domain.")
    
    else:  # JSON File
        st.write("Import from JSON backup files:")
        
        # List available JSON files
        json_files = json_manager.list_json_files()
        
        if json_files:
            st.write("Available JSON files:")
            
            # Create selection interface
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
                    if st.button("Import", key=f"nx_import_{file_info['filename']}"):
                        selected_file = file_info['filename']
            
            if selected_file:
                try:
                    # Load JSON data and convert to DataFrame
                    df = data_converter.json_to_dataframe(selected_file)
                    
                    # Import to database
                    if import_it_data_to_nx_complete(df):
                        st.success(f"✅ Successfully imported {len(df)} projects from {selected_file}")
                        st.rerun()
                    else:
                        st.error("❌ Failed to import JSON data.")
                
                except Exception as e:
                    st.error(f"❌ Error importing JSON file: {str(e)}")
        
        else:
            st.info("No JSON files found. Import CSV/Excel files to create JSON backups.")


def display_view_data():
    """Display imported data in simple table format."""
    st.subheader("📊 View Imported Data")
    
    # Get imported data
    imported_data = get_nx_imported_data()
    
    if imported_data.empty:
        st.info("No data imported yet. Import CSV data from IT Domain first.")
        return
    
    # Show basic stats
    stats = get_nx_stats()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Projects", stats.get('imported_projects', 0))
    
    with col2:
        if 'business_unit' in imported_data.columns:
            cn_count = len(imported_data[imported_data['business_unit'] == 'CN'])
            st.metric("CN Projects", cn_count)
    
    with col3:
        if 'business_unit' in imported_data.columns:
            pc_count = len(imported_data[imported_data['business_unit'] == 'PC'])
            st.metric("PC Projects", pc_count)
    
    # Display data table
    st.dataframe(imported_data, use_container_width=True)
    
    # Export functionality
    st.subheader("📤 Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv_data = imported_data.to_csv(index=False)
        st.download_button(
            label="📊 Download as CSV",
            data=csv_data,
            file_name=f"nx_domain_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Excel export if available
        try:
            import openpyxl
            from io import BytesIO
            excel_buffer = BytesIO()
            imported_data.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_buffer = excel_buffer.getvalue()
            st.download_button(
                label="📈 Download as Excel",
                data=excel_buffer,
                file_name=f"nx_domain_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except ImportError:
            st.info("Excel export not available (openpyxl not installed)")
    
    with col3:
        # JSON export
        import json
        data_converter = DataConverter()
        json_data = data_converter.excel_to_json(imported_data)
        json_str = json.dumps(json_data, indent=2, default=str)
        st.download_button(
            label="📋 Download as JSON",
            data=json_str,
            file_name=f"nx_domain_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


def display_to_summary():
    """Display complete TO Summary with all 33 fields."""
    st.subheader("📊 TO Summary Report (All 33 Fields)")
    
    to_summary = get_nx_to_summary()
    
    if to_summary.empty:
        st.info("No TO Summary data available. Import IT data and add NX regression data first.")
        return
    
    # Show summary statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Projects", len(to_summary))
    with col2:
        projects_with_nx = len(to_summary[to_summary['line_coverage'].notna()])
        st.metric("With NX Data", projects_with_nx)
    with col3:
        avg_coverage = to_summary['line_coverage'].mean()
        st.metric("Avg Line Coverage", f"{avg_coverage:.1f}%" if pd.notna(avg_coverage) else "N/A")
    with col4:
        complete_projects = len(to_summary[to_summary['to_date'].notna()])
        st.metric("TO Scheduled", complete_projects)
    
    # Display complete TO Summary table
    st.dataframe(to_summary, use_container_width=True, height=400)
    
    # Export TO Summary
    st.subheader("📤 Export TO Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = to_summary.to_csv(index=False)
        st.download_button(
            label="📊 Download Complete TO Summary (CSV)",
            data=csv_data,
            file_name=f"to_summary_33_fields_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        try:
            import openpyxl
            from io import BytesIO
            excel_buffer = BytesIO()
            to_summary.to_excel(excel_buffer, index=False, engine='openpyxl')
            excel_buffer = excel_buffer.getvalue()
            st.download_button(
                label="📈 Download TO Summary (Excel)",
                data=excel_buffer,
                file_name=f"to_summary_33_fields_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except ImportError:
            st.info("Excel export not available")


def display_coverage_analysis():
    """Display coverage analysis and quality assessment."""
    st.subheader("📈 Coverage Analysis & Quality Assessment")
    
    coverage_data = get_nx_coverage_analysis()
    
    if coverage_data.empty:
        st.info("No coverage data available. NX regression data needs to be collected first.")
        return
    
    # Coverage quality overview
    col1, col2, col3, col4 = st.columns(4)
    quality_counts = coverage_data['coverage_quality'].value_counts()
    
    with col1:
        excellent = quality_counts.get('Excellent', 0)
        st.metric("Excellent (≥90%)", excellent, delta_color="normal")
    with col2:
        good = quality_counts.get('Good', 0) 
        st.metric("Good (70-89%)", good, delta_color="normal")
    with col3:
        fair = quality_counts.get('Fair', 0)
        st.metric("Fair (50-69%)", fair, delta_color="inverse")
    with col4:
        poor = quality_counts.get('Poor', 0)
        st.metric("Poor (<50%)", poor, delta_color="inverse")
    
    # Coverage details table
    st.subheader("Coverage Details by Project")
    
    # Format coverage columns for better display
    display_df = coverage_data.copy()
    for col in ['line_coverage', 'fsm_coverage', 'interface_toggle_coverage', 'toggle_coverage', 'avg_coverage']:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
    
    st.dataframe(display_df, use_container_width=True, height=400)
    
    # Export coverage analysis
    csv_data = coverage_data.to_csv(index=False)
    st.download_button(
        label="📊 Download Coverage Analysis",
        data=csv_data,
        file_name=f"coverage_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )


def display_summary():
    """Display enhanced system summary with NX capabilities."""
    st.subheader("📋 Enhanced System Summary")
    
    stats = get_nx_stats()
    imported_data = get_nx_imported_data()
    
    # Enhanced statistics display
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("IT Projects", stats.get('imported_projects', 0))
    with col2:
        st.metric("NX Data Available", stats.get('nx_projects_with_data', 0))
    with col3:
        avg_line = stats.get('avg_line_coverage', 0)
        st.metric("Avg Line Coverage", f"{avg_line}%" if avg_line > 0 else "N/A")
    with col4:
        avg_fsm = stats.get('avg_fsm_coverage', 0)
        st.metric("Avg FSM Coverage", f"{avg_fsm}%" if avg_fsm > 0 else "N/A")
    
    # Quality breakdown
    if any(k.startswith('coverage_') for k in stats.keys()):
        st.subheader("Coverage Quality Breakdown")
        quality_cols = st.columns(4)
        quality_metrics = [
            ('coverage_excellent', 'Excellent', '🟢'),
            ('coverage_good', 'Good', '🟡'), 
            ('coverage_fair', 'Fair', '🟠'),
            ('coverage_poor', 'Poor', '🔴')
        ]
        
        for i, (key, label, icon) in enumerate(quality_metrics):
            with quality_cols[i]:
                count = stats.get(key, 0)
                st.metric(f"{icon} {label}", count)
    
    # Basic information
    st.subheader("System Status")
    st.write(f"• **IT Domain Projects**: {stats.get('imported_projects', 0)} imported")
    st.write(f"• **NX Domain Projects**: {stats.get('nx_projects_with_data', 0)} with regression data")
    
    if not imported_data.empty and 'import_date' in imported_data.columns:
        st.write(f"• **Last Import**: {imported_data['import_date'].max()}")
        
        # Business unit breakdown
        if 'business_unit' in imported_data.columns:
            bu_counts = imported_data['business_unit'].value_counts()
            if len(bu_counts) > 0:
                st.write("• **Business Units**: " + ", ".join([f"{bu}: {count}" for bu, count in bu_counts.items() if bu]))
    
    if stats.get('nx_projects_with_data', 0) == 0:
        st.info("💡 Import IT data and add NX regression data to see full TO Summary capabilities.")


def main():
    """Main function for enhanced NX Domain interface."""
    
    # Header
    st.title("📈 NX Domain - Enhanced")
    st.write("*Complete data import, coverage analysis, and TO Summary generation*")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        mode = st.radio(
            "Select Mode:",
            ["Summary", "Import IT Data", "View IT Data", "TO Summary (33 Fields)", "Coverage Analysis"],
            help="Choose what you want to do"
        )
        
        # Production note
        st.markdown("---")
        st.info("**Production Note**: NX regression data will be auto-collected from external MySQL database populated by regression scripts.")
    
    # Main content based on mode
    if mode == "Summary":
        display_summary()
    elif mode == "Import IT Data":
        display_import_data()
    elif mode == "View IT Data":
        display_view_data()
    elif mode == "TO Summary (33 Fields)":
        display_to_summary()
    elif mode == "Coverage Analysis":
        display_coverage_analysis()
    
    # Footer
    st.markdown("---")
    st.markdown("*NX Domain - Enhanced DV Management System*")


if __name__ == "__main__":
    main()