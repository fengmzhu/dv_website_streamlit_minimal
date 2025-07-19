import pandas as pd
import os
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import openpyxl

class ExcelHandler:
    """Handles Excel file operations including reading, validation, and conversion"""
    
    SUPPORTED_EXTENSIONS = ['.xlsx', '.xls', '.xlsm', '.xlsb']
    
    def __init__(self):
        self.temp_dir = "data/temp"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def validate_excel_file(self, file_path: str) -> Tuple[bool, str]:
        """Validate if the file is a valid Excel file"""
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.SUPPORTED_EXTENSIONS:
            return False, f"Unsupported file type. Supported types: {', '.join(self.SUPPORTED_EXTENSIONS)}"
        
        try:
            # Try to open the file to validate it's a valid Excel
            pd.read_excel(file_path, nrows=0)
            return True, "Valid Excel file"
        except Exception as e:
            return False, f"Invalid Excel file: {str(e)}"
    
    def read_excel_data(self, file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """Read Excel file and return as DataFrame"""
        try:
            # Read Excel file
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Convert data types
            df = self._convert_data_types(df)
            
            return df
        except Exception as e:
            raise Exception(f"Error reading Excel file: {str(e)}")
    
    def _convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert DataFrame data types appropriately"""
        for col in df.columns:
            # Try to convert to numeric if possible
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass
            
            # Convert datetime columns
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    pass
        
        return df
    
    def validate_columns(self, df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, List[str]]:
        """Validate if DataFrame has all required columns"""
        missing_columns = []
        df_columns_lower = [col.lower() for col in df.columns]
        
        for req_col in required_columns:
            if req_col.lower() not in df_columns_lower:
                missing_columns.append(req_col)
        
        if missing_columns:
            return False, missing_columns
        return True, []
    
    def validate_data_quality(self, df: pd.DataFrame, validation_rules: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate data quality based on provided rules"""
        errors = []
        
        for column, rules in validation_rules.items():
            if column not in df.columns:
                continue
            
            # Check for nulls if not allowed
            if rules.get('not_null', False):
                null_count = df[column].isnull().sum()
                if null_count > 0:
                    errors.append(f"Column '{column}' has {null_count} null values")
            
            # Check data type
            if 'dtype' in rules:
                expected_type = rules['dtype']
                if expected_type == 'numeric':
                    non_numeric = df[column].apply(lambda x: not isinstance(x, (int, float)) and pd.notna(x)).sum()
                    if non_numeric > 0:
                        errors.append(f"Column '{column}' has {non_numeric} non-numeric values")
            
            # Check allowed values
            if 'allowed_values' in rules:
                invalid_values = df[~df[column].isin(rules['allowed_values'])][column].unique()
                if len(invalid_values) > 0:
                    errors.append(f"Column '{column}' has invalid values: {invalid_values[:5]}")
            
            # Check value range
            if 'min_value' in rules:
                below_min = df[df[column] < rules['min_value']].shape[0]
                if below_min > 0:
                    errors.append(f"Column '{column}' has {below_min} values below minimum ({rules['min_value']})")
            
            if 'max_value' in rules:
                above_max = df[df[column] > rules['max_value']].shape[0]
                if above_max > 0:
                    errors.append(f"Column '{column}' has {above_max} values above maximum ({rules['max_value']})")
        
        return len(errors) == 0, errors
    
    def preview_data(self, df: pd.DataFrame, rows: int = 10) -> pd.DataFrame:
        """Return a preview of the DataFrame"""
        return df.head(rows)
    
    def get_sheet_names(self, file_path: str) -> List[str]:
        """Get all sheet names from Excel file"""
        try:
            excel_file = pd.ExcelFile(file_path)
            return excel_file.sheet_names
        except Exception as e:
            raise Exception(f"Error reading sheet names: {str(e)}")
    
    def save_temp_file(self, uploaded_file, filename: str) -> str:
        """Save uploaded file to temp directory"""
        temp_path = os.path.join(self.temp_dir, filename)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return temp_path
    
    def clean_temp_files(self, older_than_hours: int = 24):
        """Clean old temp files"""
        current_time = datetime.now()
        for filename in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if (current_time - file_time).total_seconds() > older_than_hours * 3600:
                    os.remove(file_path)
    
    def split_comma_separated_values(self, df: pd.DataFrame, column: str, 
                                   distribute_column: Optional[str] = None) -> pd.DataFrame:
        """Split comma-separated values in a column into multiple rows"""
        if column not in df.columns:
            return df
        
        # Create a copy to avoid modifying original
        result_df = df.copy()
        
        # Split the column and expand
        split_rows = []
        for idx, row in result_df.iterrows():
            if pd.notna(row[column]) and ',' in str(row[column]):
                values = [v.strip() for v in str(row[column]).split(',')]
                
                # If distribute_column is specified, divide its value
                if distribute_column and distribute_column in result_df.columns:
                    distributed_value = row[distribute_column] / len(values) if len(values) > 0 else row[distribute_column]
                else:
                    distributed_value = None
                
                for value in values:
                    new_row = row.copy()
                    new_row[column] = value
                    if distributed_value is not None:
                        new_row[distribute_column] = distributed_value
                    split_rows.append(new_row)
            else:
                split_rows.append(row)
        
        return pd.DataFrame(split_rows).reset_index(drop=True)