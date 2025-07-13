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
        """Create IT domain database from minimal schema."""
        schema_path = self.it_db_path.parent / "it_domain_schema_minimal.sql"
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            conn = sqlite3.connect(self.it_db_path)
            conn.executescript(schema_sql)
            conn.close()
            logger.info(f"Created minimal IT domain database: {self.it_db_path}")
    
    def _create_nx_database(self):
        """Create NX domain database from minimal schema."""
        schema_path = self.nx_db_path.parent / "nx_domain_schema_minimal.sql"
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            conn = sqlite3.connect(self.nx_db_path)
            conn.executescript(schema_sql)
            conn.close()
            logger.info(f"Created minimal NX domain database: {self.nx_db_path}")
    
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


# IT Domain Functions (Simplified)
def add_it_project_minimal(project_data: Dict[str, Any]) -> bool:
    """
    Add new project to IT domain with minimal 5 fields.
    
    Args:
        project_data: Dictionary with 5 essential fields
    
    Returns:
        bool: Success status
    """
    try:
        # Validate required fields
        if not project_data.get('project_name'):
            raise ValueError("Project name is required")
        
        # Build insert query with 5 fields only
        query = """
        INSERT INTO it_domain_projects (
            project_name, dv_engineer, business_unit, ip, spip_url
        ) VALUES (?, ?, ?, ?, ?)
        """
        
        params = (
            project_data.get('project_name'),
            project_data.get('dv_engineer', ''),
            project_data.get('business_unit', ''),
            project_data.get('ip', ''),
            project_data.get('spip_url', '')
        )
        
        execute_it_query(query, params)
        logger.info(f"Added IT project: {project_data['project_name']}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to add IT project: {e}")
        return False


def get_it_projects_minimal() -> pd.DataFrame:
    """Get all IT domain projects with minimal fields."""
    query = """
    SELECT 
        id, task_index, project_name, dv_engineer, 
        business_unit, ip, spip_url, created_at
    FROM it_domain_projects
    ORDER BY task_index
    """
    return fetch_it_dataframe(query)


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
def import_it_data_to_nx_minimal(csv_data: pd.DataFrame) -> bool:
    """
    Import IT domain CSV data to NX domain (minimal version).
    
    Args:
        csv_data: DataFrame with IT domain project data
    
    Returns:
        bool: Success status
    """
    try:
        conn = db_manager.get_nx_connection()
        
        # Clear existing data
        conn.execute("DELETE FROM imported_it_data")
        
        # Only keep the 6 essential columns if they exist
        required_cols = ['task_index', 'project_name', 'dv_engineer', 'business_unit', 'ip', 'spip_url']
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
        
        logger.info(f"Imported {len(import_data)} IT projects to NX domain")
        return True
        
    except Exception as e:
        logger.error(f"Failed to import IT data to NX: {e}")
        return False


def get_nx_imported_data() -> pd.DataFrame:
    """Get all imported data from NX domain."""
    query = "SELECT * FROM simple_view"
    return fetch_nx_dataframe(query)


def get_nx_stats() -> Dict[str, int]:
    """Get basic statistics for NX domain."""
    try:
        imported_count = fetch_nx_dataframe("SELECT COUNT(*) as count FROM imported_it_data").iloc[0]['count']
        return {'imported_projects': imported_count}
    except Exception as e:
        logger.error(f"Failed to get NX stats: {e}")
        return {'imported_projects': 0}


# Validation Functions (Simplified)
def validate_project_data_minimal(data: Dict[str, Any]) -> list:
    """Validate minimal project data."""
    errors = []
    
    # Only validate required project name
    if not data.get('project_name', '').strip():
        errors.append("Project name is required")
    
    # Optional business unit validation
    business_unit = data.get('business_unit', '')
    if business_unit and business_unit not in ['CN', 'PC', '']:
        errors.append("Business unit must be 'CN', 'PC', or empty")
    
    return errors