import pandas as pd
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import sqlite3
import os

class DataConverter:
    """Converts data between different formats: Excel, JSON, Database, and DataFrame"""
    
    def __init__(self):
        self.database_dir = "database"
        self.json_dir = "data/json"
    
    def excel_to_json(self, excel_data: Union[pd.DataFrame, str], 
                     output_filename: Optional[str] = None,
                     metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Excel data to JSON format
        
        Args:
            excel_data: DataFrame or path to Excel file
            output_filename: Optional filename to save JSON
            metadata: Additional metadata to include
        
        Returns:
            JSON data structure
        """
        # Load data if it's a file path
        if isinstance(excel_data, str):
            df = pd.read_excel(excel_data)
        else:
            df = excel_data.copy()
        
        # Clean and prepare data
        df = self._clean_dataframe(df)
        
        # Convert DataFrame to records
        records = df.to_dict(orient='records')
        
        # Prepare JSON structure
        json_data = {
            "metadata": {
                "source": "excel",
                "created": datetime.now().isoformat(),
                "version": "1.0",
                "record_count": len(records),
                "columns": list(df.columns)
            },
            "data": records
        }
        
        # Add custom metadata
        if metadata:
            json_data["metadata"].update(metadata)
        
        # Save to file if filename provided
        if output_filename:
            from .json_manager import JSONManager
            json_manager = JSONManager()
            json_manager.save_to_json(records, output_filename, json_data["metadata"])
        
        return json_data
    
    def json_to_dataframe(self, json_data: Union[Dict, str]) -> pd.DataFrame:
        """Convert JSON data to pandas DataFrame
        
        Args:
            json_data: Dictionary or path to JSON file
        
        Returns:
            pandas DataFrame
        """
        # Load data if it's a file path
        if isinstance(json_data, str):
            from .json_manager import JSONManager
            json_manager = JSONManager()
            json_data = json_manager.load_from_json(json_data)
        
        # Extract records
        if isinstance(json_data, dict) and "data" in json_data:
            records = json_data["data"]
        elif isinstance(json_data, list):
            records = json_data
        else:
            records = [json_data]
        
        # Convert to DataFrame
        df = pd.DataFrame(records)
        
        # Apply data type conversions
        df = self._apply_dtypes(df, json_data.get("metadata", {}))
        
        return df
    
    def database_to_json(self, db_path: str, table_name: str, 
                        output_filename: Optional[str] = None,
                        query: Optional[str] = None) -> Dict[str, Any]:
        """Convert database table to JSON format
        
        Args:
            db_path: Path to database file
            table_name: Name of the table to export
            output_filename: Optional filename to save JSON
            query: Optional custom SQL query
        
        Returns:
            JSON data structure
        """
        # Connect to database
        conn = sqlite3.connect(db_path)
        
        try:
            # Execute query or select all from table
            if query:
                df = pd.read_sql_query(query, conn)
            else:
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            
            # Get table schema
            schema_query = f"PRAGMA table_info({table_name})"
            schema_df = pd.read_sql_query(schema_query, conn)
            
            # Prepare metadata
            metadata = {
                "source": "database",
                "database": os.path.basename(db_path),
                "table": table_name,
                "schema": schema_df.to_dict(orient='records')
            }
            
            # Convert to JSON
            return self.excel_to_json(df, output_filename, metadata)
        
        finally:
            conn.close()
    
    def json_to_database(self, json_data: Union[Dict, str], db_path: str, 
                        table_name: str, if_exists: str = 'replace') -> int:
        """Convert JSON data to database table
        
        Args:
            json_data: Dictionary or path to JSON file
            db_path: Path to database file
            table_name: Name of the table to create/update
            if_exists: 'replace', 'append', or 'fail'
        
        Returns:
            Number of records inserted
        """
        # Convert JSON to DataFrame
        df = self.json_to_dataframe(json_data)
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        
        try:
            # Write to database
            df.to_sql(table_name, conn, if_exists=if_exists, index=False)
            
            # Get row count
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            return row_count
        
        finally:
            conn.close()
    
    def sync_database_with_json(self, db_path: str, table_name: str, 
                               json_filename: str, direction: str = "both") -> Dict[str, int]:
        """Synchronize database table with JSON file
        
        Args:
            db_path: Path to database file
            table_name: Database table name
            json_filename: JSON filename
            direction: 'to_json', 'to_db', or 'both'
        
        Returns:
            Dictionary with sync statistics
        """
        stats = {"json_records": 0, "db_records": 0, "synced": 0}
        
        if direction in ["to_json", "both"]:
            # Export database to JSON
            json_data = self.database_to_json(db_path, table_name, json_filename)
            stats["json_records"] = json_data["metadata"]["record_count"]
        
        if direction in ["to_db", "both"]:
            # Import JSON to database
            from .json_manager import JSONManager
            json_manager = JSONManager()
            
            if direction == "to_db":
                # Only import if we didn't just export
                json_data = json_manager.load_from_json(json_filename)
            
            stats["db_records"] = self.json_to_database(json_data, db_path, table_name)
        
        stats["synced"] = max(stats["json_records"], stats["db_records"])
        return stats
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean DataFrame for JSON serialization"""
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Convert datetime columns to ISO format strings
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].apply(lambda x: x.isoformat() if pd.notna(x) else None)
        
        # Replace NaN with None for better JSON representation
        df = df.where(pd.notna(df), None)
        
        # Ensure column names are strings
        df.columns = df.columns.astype(str)
        
        return df
    
    def _apply_dtypes(self, df: pd.DataFrame, metadata: Dict) -> pd.DataFrame:
        """Apply data types based on metadata"""
        # Try to infer datetime columns
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    pass
        
        # Apply schema if available
        if 'schema' in metadata:
            for col_info in metadata['schema']:
                col_name = col_info.get('name')
                col_type = col_info.get('type', '').lower()
                
                if col_name in df.columns:
                    if 'int' in col_type:
                        df[col_name] = pd.to_numeric(df[col_name], errors='coerce').astype('Int64')
                    elif 'real' in col_type or 'float' in col_type:
                        df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
                    elif 'date' in col_type or 'time' in col_type:
                        df[col_name] = pd.to_datetime(df[col_name], errors='coerce')
        
        return df
    
    def convert_between_formats(self, source_path: str, target_path: str,
                               source_format: str, target_format: str,
                               **kwargs) -> bool:
        """Generic converter between different formats
        
        Args:
            source_path: Path to source file
            target_path: Path to target file
            source_format: 'excel', 'json', 'csv', 'database'
            target_format: 'excel', 'json', 'csv', 'database'
            **kwargs: Additional arguments for specific conversions
        
        Returns:
            Success status
        """
        # Load source data
        if source_format == 'excel':
            df = pd.read_excel(source_path)
        elif source_format == 'csv':
            df = pd.read_csv(source_path)
        elif source_format == 'json':
            df = self.json_to_dataframe(source_path)
        elif source_format == 'database':
            db_path = kwargs.get('db_path')
            table_name = kwargs.get('table_name')
            conn = sqlite3.connect(db_path)
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            conn.close()
        else:
            raise ValueError(f"Unsupported source format: {source_format}")
        
        # Save to target format
        if target_format == 'excel':
            df.to_excel(target_path, index=False)
        elif target_format == 'csv':
            df.to_csv(target_path, index=False)
        elif target_format == 'json':
            self.excel_to_json(df, target_path)
        elif target_format == 'database':
            db_path = kwargs.get('db_path')
            table_name = kwargs.get('table_name')
            self.json_to_database(df, db_path, table_name)
        else:
            raise ValueError(f"Unsupported target format: {target_format}")
        
        return True