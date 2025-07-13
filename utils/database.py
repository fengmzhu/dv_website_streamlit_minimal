"""
Minimal database utilities for simplified DV Management System.
Focuses on core functionality: input → export → import → view
"""

import sqlite3
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database paths
IT_DB_PATH = Path(__file__).parent.parent / "database" / "it_domain.db"
NX_DB_PATH = Path(__file__).parent.parent / "database" / "nx_domain.db"


class MinimalDatabaseManager:
    """Simplified database manager for core workflow only."""
    
    def __init__(self):
        self.it_db_path = IT_DB_PATH
        self.nx_db_path = NX_DB_PATH
        self._ensure_databases_exist()
    
    def _ensure_databases_exist(self):
        """Create databases if they don't exist."""
        if not self.it_db_path.exists():
            self._create_it_database()
        if not self.nx_db_path.exists():
            self._create_nx_database()
    
    def _create_it_database(self):
        """Create IT domain database from schema."""
        schema_path = self.it_db_path.parent / "it_domain_schema.sql"
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            conn = sqlite3.connect(self.it_db_path)
            conn.executescript(schema_sql)
            conn.close()
            logger.info(f"Created IT domain database: {self.it_db_path}")
    
    def _create_nx_database(self):
        """Create NX domain database from schema."""
        schema_path = self.nx_db_path.parent / "nx_domain_schema.sql"
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            conn = sqlite3.connect(self.nx_db_path)
            conn.executescript(schema_sql)
            conn.close()
            logger.info(f"Created NX domain database: {self.nx_db_path}")
    
    @st.cache_resource
    def get_it_connection(_self):
        """Get cached connection to IT domain database."""
        return sqlite3.connect(_self.it_db_path, check_same_thread=False)
    
    @st.cache_resource
    def get_nx_connection(_self):
        """Get cached connection to NX domain database."""
        return sqlite3.connect(_self.nx_db_path, check_same_thread=False)


# Global database manager instance
db_manager = MinimalDatabaseManager()


def execute_it_query(query: str, params: Optional[tuple] = None) -> sqlite3.Cursor:
    """Execute query on IT domain database."""
    try:
        conn = db_manager.get_it_connection()
        if params:
            cursor = conn.execute(query, params)
        else:
            cursor = conn.execute(query)
        conn.commit()
        return cursor
    except Exception as e:
        logger.error(f"IT domain query failed: {query}, Error: {e}")
        raise


def execute_nx_query(query: str, params: Optional[tuple] = None) -> sqlite3.Cursor:
    """Execute query on NX domain database."""
    try:
        conn = db_manager.get_nx_connection()
        if params:
            cursor = conn.execute(query, params)
        else:
            cursor = conn.execute(query)
        conn.commit()
        return cursor
    except Exception as e:
        logger.error(f"NX domain query failed: {query}, Error: {e}")
        raise


def fetch_it_dataframe(query: str, params: Optional[tuple] = None) -> pd.DataFrame:
    """Fetch data from IT domain as pandas DataFrame."""
    try:
        conn = db_manager.get_it_connection()
        if params:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        logger.error(f"IT domain dataframe fetch failed: {query}, Error: {e}")
        return pd.DataFrame()


def fetch_nx_dataframe(query: str, params: Optional[tuple] = None) -> pd.DataFrame:
    """Fetch data from NX domain as pandas DataFrame."""
    try:
        conn = db_manager.get_nx_connection()
        if params:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        logger.error(f"NX domain dataframe fetch failed: {query}, Error: {e}")
        return pd.DataFrame()


# IT Domain Functions (Complete)
def add_it_project_complete(project_data: Dict[str, Any]) -> bool:
    """
    Add new project to IT domain with all 17 fields.
    
    Args:
        project_data: Dictionary with all IT Domain fields
    
    Returns:
        bool: Success status
    """
    try:
        # Validate required fields
        if not project_data.get('project_name'):
            raise ValueError("Project name is required")
        
        # Build insert query with all 17 fields
        query = """
        INSERT INTO it_domain_projects (
            project_name, spip_ip, ip, ip_postfix, ip_subtype, alternative_name,
            dv_engineer, digital_designer, analog_designer, business_unit,
            spip_url, wiki_url, spec_version, spec_path, inherit_from_ip, reuse_ip
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            project_data.get('project_name'),
            project_data.get('spip_ip', ''),
            project_data.get('ip', ''),
            project_data.get('ip_postfix', ''),
            project_data.get('ip_subtype', 'default'),
            project_data.get('alternative_name', ''),
            project_data.get('dv_engineer', ''),
            project_data.get('digital_designer', ''),
            project_data.get('analog_designer', ''),
            project_data.get('business_unit', ''),
            project_data.get('spip_url', ''),
            project_data.get('wiki_url', ''),
            project_data.get('spec_version', ''),
            project_data.get('spec_path', ''),
            project_data.get('inherit_from_ip', ''),
            project_data.get('reuse_ip', '')
        )
        
        execute_it_query(query, params)
        logger.info(f"Added IT project: {project_data['project_name']}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to add IT project: {e}")
        return False

# Backward compatibility function
def add_it_project_minimal(project_data: Dict[str, Any]) -> bool:
    """Backward compatibility wrapper for minimal field support."""
    return add_it_project_complete(project_data)


def get_it_projects_complete() -> pd.DataFrame:
    """Get all IT domain projects with all 17 fields."""
    query = """
    SELECT 
        id, task_index, project_name, spip_ip, ip, ip_postfix, ip_subtype, alternative_name,
        dv_engineer, digital_designer, analog_designer, business_unit,
        spip_url, wiki_url, spec_version, spec_path, inherit_from_ip, reuse_ip,
        created_at, updated_at
    FROM it_domain_projects
    ORDER BY task_index
    """
    return fetch_it_dataframe(query)

# Backward compatibility function
def get_it_projects_minimal() -> pd.DataFrame:
    """Backward compatibility wrapper for minimal field display."""
    df = get_it_projects_complete()
    if df.empty:
        return df
    # Return subset of columns for minimal view
    minimal_cols = ['id', 'task_index', 'project_name', 'dv_engineer', 'business_unit', 'ip', 'spip_url', 'created_at']
    available_cols = [col for col in minimal_cols if col in df.columns]
    return df[available_cols]


def get_it_export_data_minimal() -> pd.DataFrame:
    """Get IT domain export data using the minimal export view."""
    query = "SELECT * FROM export_view"
    return fetch_it_dataframe(query)


def delete_it_project(project_id: int) -> bool:
    """Delete IT domain project by ID."""
    try:
        query = "DELETE FROM it_domain_projects WHERE id = ?"
        execute_it_query(query, (project_id,))
        logger.info(f"Deleted IT project ID: {project_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete IT project: {e}")
        return False


# NX Domain Functions (Simplified)
def import_it_data_to_nx_complete(csv_data: pd.DataFrame) -> bool:
    """
    Import complete IT domain CSV data to NX domain (all 17 fields).
    
    Args:
        csv_data: DataFrame with complete IT domain project data
    
    Returns:
        bool: Success status
    """
    try:
        conn = db_manager.get_nx_connection()
        
        # Clear existing data
        conn.execute("DELETE FROM imported_it_data")
        
        # All 17 IT domain columns
        required_cols = [
            'task_index', 'project_name', 'spip_ip', 'ip', 'ip_postfix', 'ip_subtype', 'alternative_name',
            'dv_engineer', 'digital_designer', 'analog_designer', 'business_unit',
            'spip_url', 'wiki_url', 'spec_version', 'spec_path', 'inherit_from_ip', 'reuse_ip'
        ]
        available_cols = [col for col in required_cols if col in csv_data.columns]
        
        if 'project_name' not in available_cols:
            raise ValueError("project_name column is required")
        
        # Select only available columns
        import_data = csv_data[available_cols].copy()
        
        # Clean data - replace NaN with empty strings
        import_data = import_data.fillna('')
        
        # Insert new data
        import_data.to_sql('imported_it_data', conn, if_exists='append', index=False)
        conn.commit()
        
        logger.info(f"Imported {len(import_data)} IT projects to NX domain with {len(available_cols)} fields")
        return True
        
    except Exception as e:
        logger.error(f"Failed to import IT data to NX: {e}")
        return False

# Backward compatibility function
def import_it_data_to_nx_minimal(csv_data: pd.DataFrame) -> bool:
    """Backward compatibility wrapper for IT data import."""
    return import_it_data_to_nx_complete(csv_data)


def get_nx_imported_data() -> pd.DataFrame:
    """Get all imported IT data from NX domain."""
    query = "SELECT * FROM imported_it_view"
    return fetch_nx_dataframe(query)


def get_nx_to_summary() -> pd.DataFrame:
    """Get complete TO Summary with all 33 fields (IT + NX)."""
    query = "SELECT * FROM to_summary_view"
    return fetch_nx_dataframe(query)


def get_nx_coverage_analysis() -> pd.DataFrame:
    """Get coverage analysis with quality assessment."""
    query = "SELECT * FROM coverage_analysis_view"
    return fetch_nx_dataframe(query)


def get_nx_stats() -> Dict[str, Any]:
    """Get comprehensive statistics for NX domain."""
    try:
        stats = {}
        
        # Basic counts
        imported_count = fetch_nx_dataframe("SELECT COUNT(*) as count FROM imported_it_data").iloc[0]['count']
        stats['imported_projects'] = imported_count
        
        # NX regression data count
        nx_count = fetch_nx_dataframe("SELECT COUNT(*) as count FROM nx_regression_data").iloc[0]['count']
        stats['nx_projects_with_data'] = nx_count
        
        # Coverage quality breakdown
        coverage_df = get_nx_coverage_analysis()
        if not coverage_df.empty:
            quality_counts = coverage_df['coverage_quality'].value_counts().to_dict()
            stats.update({f'coverage_{k.lower().replace(" ", "_")}': v for k, v in quality_counts.items()})
        
        # Average coverage
        avg_coverage = fetch_nx_dataframe("""
            SELECT AVG(COALESCE(line_coverage, 0)) as avg_line,
                   AVG(COALESCE(fsm_coverage, 0)) as avg_fsm,
                   AVG(COALESCE(toggle_coverage, 0)) as avg_toggle
            FROM nx_regression_data
        """)
        if not avg_coverage.empty:
            stats['avg_line_coverage'] = round(avg_coverage.iloc[0]['avg_line'], 1)
            stats['avg_fsm_coverage'] = round(avg_coverage.iloc[0]['avg_fsm'], 1)
            stats['avg_toggle_coverage'] = round(avg_coverage.iloc[0]['avg_toggle'], 1)
        
        return stats
    except Exception as e:
        logger.error(f"Failed to get NX stats: {e}")
        return {'imported_projects': 0, 'nx_projects_with_data': 0}


# Validation Functions (Complete)
def validate_project_data_complete(data: Dict[str, Any]) -> list:
    """Validate complete project data for all 17 IT Domain fields."""
    errors = []
    
    # Required field validation
    if not data.get('project_name', '').strip():
        errors.append("Project name is required")
    
    # Enum field validations
    business_unit = data.get('business_unit', '')
    if business_unit and business_unit not in ['CN', 'PC', '']:
        errors.append("Business unit must be 'CN', 'PC', or empty")
    
    ip_subtype = data.get('ip_subtype', '')
    if ip_subtype and ip_subtype not in ['default', 'gen2x1']:
        errors.append("IP subtype must be 'default' or 'gen2x1'")
    
    reuse_ip = data.get('reuse_ip', '')
    if reuse_ip and reuse_ip not in ['Y', 'N', '']:
        errors.append("Reuse IP must be 'Y', 'N', or empty")
    
    # URL validations
    spip_url = data.get('spip_url', '')
    if spip_url and not spip_url.startswith('http'):
        errors.append("SPIP URL must start with 'http' or be empty")
    
    wiki_url = data.get('wiki_url', '')
    if wiki_url and not wiki_url.startswith('http'):
        errors.append("Wiki URL must start with 'http' or be empty")
    
    return errors

# Backward compatibility function
def validate_project_data_minimal(data: Dict[str, Any]) -> list:
    """Backward compatibility wrapper for validation."""
    return validate_project_data_complete(data)