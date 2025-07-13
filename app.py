"""
DV Management System - Minimal Version
Ultra-lightweight application focused on core workflow: input → export → import → view
"""

import streamlit as st
import sys
from pathlib import Path

# Add utils directory to path
sys.path.append(str(Path(__file__).parent))

from utils.database import db_manager, get_nx_stats

# Page configuration
st.set_page_config(
    page_title="DV Management - Minimal",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application landing page - minimal version."""
    
    # Header
    st.title("🔧 DV Management System - Minimal")
    st.write("*Lightweight project management and data integration*")
    
    # Simple description
    st.markdown("""
    **Simple workflow:**
    1. **IT Domain**: Add projects with essential data
    2. **IT Domain**: Export project data as CSV
    3. **NX Domain**: Import CSV data
    4. **NX Domain**: View and manage integrated data
    """)
    
    # Quick navigation
    st.subheader("🧭 Quick Access")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📊 IT Domain**
        - Add projects (5 essential fields)
        - View projects in table
        - Export data as CSV/Excel
        """)
        if st.button("📊 Go to IT Domain", use_container_width=True):
            st.switch_page("pages/1_📊_IT_Domain.py")
    
    with col2:
        st.markdown("""
        **📈 NX Domain**
        - Import CSV from IT Domain
        - View integrated data
        - Export processed data
        """)
        if st.button("📈 Go to NX Domain", use_container_width=True):
            st.switch_page("pages/2_📈_NX_Domain.py")
    
    # System status
    st.subheader("🔍 System Status")
    
    try:
        # Test database connections
        it_conn = db_manager.get_it_connection()
        nx_conn = db_manager.get_nx_connection()
        
        # Get basic stats
        it_count = it_conn.execute("SELECT COUNT(*) FROM it_domain_projects").fetchone()[0]
        nx_stats = get_nx_stats()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("IT Projects", it_count)
        
        with col2:
            st.metric("Imported Projects", nx_stats.get('imported_projects', 0))
        
        st.success("✅ Database connections working")
        
    except Exception as e:
        st.error(f"❌ Database connection error: {str(e)}")
        st.info("💡 Databases will be created automatically when you access the domain pages.")
    
    # Technical information
    with st.expander("🔧 Technical Information"):
        st.markdown("""
        ### Minimal Architecture
        - **Dependencies**: Only Streamlit, Pandas, and SQLite
        - **IT Domain**: 5 essential fields (project_name, dv_engineer, business_unit, ip, spip_url)
        - **NX Domain**: Simple import and view functionality
        - **Database**: Lightweight SQLite files
        
        ### Workflow
        1. Add projects in IT Domain with basic information
        2. Export projects as CSV from IT Domain
        3. Import CSV file into NX Domain
        4. View and export integrated data from NX Domain
        
        ### Benefits
        - **Ultra-lightweight**: ~70% less code than full version
        - **Fast**: No complex visualizations or heavy dependencies
        - **Simple**: Focused on core workflow only
        - **Reliable**: Minimal dependencies reduce potential issues
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        DV Management System - Minimal Version | Ultra-Lightweight Implementation
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()