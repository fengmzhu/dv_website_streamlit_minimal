"""
NX Domain - Minimal Version
Simplified data import and viewing with no charts/visualizations
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Add utils directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.database import (
    import_it_data_to_nx_minimal,
    get_nx_imported_data,
    get_nx_stats
)

# Page configuration
st.set_page_config(
    page_title="NX Domain - Minimal",
    page_icon="📈",
    layout="wide"
)

def display_import_data():
    """Display CSV import functionality."""
    st.subheader("📥 Import IT Domain Data")
    
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
                    if import_it_data_to_nx_minimal(csv_data):
                        st.success(f"✅ Successfully imported {len(csv_data)} projects to NX Domain")
                        st.rerun()
                    else:
                        st.error("❌ Failed to import data. Check that project_name column exists.")
        
        except Exception as e:
            st.error(f"❌ Error reading CSV file: {str(e)}")
            st.write("Please ensure the file is a valid CSV exported from IT Domain.")


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
    
    col1, col2 = st.columns(2)
    
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


def display_summary():
    """Display simple summary of system status."""
    st.subheader("📋 System Summary")
    
    stats = get_nx_stats()
    imported_data = get_nx_imported_data()
    
    # Basic information
    st.write("**Current Status:**")
    st.write(f"• {stats.get('imported_projects', 0)} projects imported from IT Domain")
    
    if not imported_data.empty:
        st.write(f"• Last import: {imported_data['import_date'].max() if 'import_date' in imported_data.columns else 'Unknown'}")
        
        # Show breakdown by business unit if available
        if 'business_unit' in imported_data.columns:
            bu_counts = imported_data['business_unit'].value_counts()
            st.write("**Business Unit Breakdown:**")
            for bu, count in bu_counts.items():
                if bu:  # Skip empty business units
                    st.write(f"• {bu}: {count} projects")
        
        # Show DV engineers if available
        if 'dv_engineer' in imported_data.columns:
            dv_counts = imported_data['dv_engineer'].value_counts()
            if len(dv_counts) > 0:
                st.write(f"**DV Engineers:** {len(dv_counts)} unique engineers")
    else:
        st.info("Import data from IT Domain to see detailed statistics.")


def main():
    """Main function for NX Domain minimal interface."""
    
    # Header
    st.title("📈 NX Domain - Minimal")
    st.write("*Simple data import and viewing*")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        mode = st.radio(
            "Select Mode:",
            ["Summary", "Import IT Data", "View Data"],
            help="Choose what you want to do"
        )
    
    # Main content based on mode
    if mode == "Summary":
        display_summary()
    elif mode == "Import IT Data":
        display_import_data()
    elif mode == "View Data":
        display_view_data()
    
    # Footer
    st.markdown("---")
    st.markdown("*NX Domain - Minimal DV Management System*")


if __name__ == "__main__":
    main()