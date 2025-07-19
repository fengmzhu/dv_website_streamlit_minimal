import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
from pathlib import Path

class JSONManager:
    """Manages JSON file operations including save, load, update, and backup"""
    
    def __init__(self):
        self.json_dir = "data/json"
        self.backup_dir = "data/backups"
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure required directories exist"""
        os.makedirs(self.json_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def save_to_json(self, data: Any, filename: str, metadata: Optional[Dict] = None) -> str:
        """Save data to JSON file with optional metadata"""
        # Ensure filename has .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        file_path = os.path.join(self.json_dir, filename)
        
        # Prepare the JSON structure
        json_data = {
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0",
                "record_count": len(data) if isinstance(data, (list, pd.DataFrame)) else 1
            },
            "data": data
        }
        
        # Add custom metadata if provided
        if metadata:
            json_data["metadata"].update(metadata)
        
        # Convert DataFrame to dict if necessary
        if isinstance(data, pd.DataFrame):
            json_data["data"] = data.to_dict(orient='records')
            json_data["metadata"]["record_count"] = len(data)
        
        # Write to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)
            return file_path
        except Exception as e:
            raise Exception(f"Error saving JSON file: {str(e)}")
    
    def load_from_json(self, filename: str) -> Dict[str, Any]:
        """Load data from JSON file"""
        if not filename.endswith('.json'):
            filename += '.json'
        
        file_path = os.path.join(self.json_dir, filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"JSON file not found: {filename}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Error loading JSON file: {str(e)}")
    
    def update_json_data(self, filename: str, new_data: Any, 
                        merge_strategy: str = "update") -> str:
        """Update JSON data with different merge strategies
        
        Args:
            filename: JSON file to update
            new_data: New data to merge
            merge_strategy: 'update', 'append', or 'replace'
        """
        if not filename.endswith('.json'):
            filename += '.json'
        
        file_path = os.path.join(self.json_dir, filename)
        
        # Create backup before updating
        if os.path.exists(file_path):
            self.create_backup(filename)
        
        if merge_strategy == "replace" or not os.path.exists(file_path):
            # Complete replacement or new file
            return self.save_to_json(new_data, filename)
        
        # Load existing data
        existing_data = self.load_from_json(filename)
        existing_records = existing_data.get("data", [])
        
        # Convert new_data to list of records if it's a DataFrame
        if isinstance(new_data, pd.DataFrame):
            new_records = new_data.to_dict(orient='records')
        elif isinstance(new_data, dict) and "data" in new_data:
            new_records = new_data["data"]
        else:
            new_records = new_data if isinstance(new_data, list) else [new_data]
        
        if merge_strategy == "append":
            # Append new records
            merged_data = existing_records + new_records
        elif merge_strategy == "update":
            # Update existing records and add new ones
            # This assumes there's an 'id' or 'index' field for matching
            merged_data = self._merge_records(existing_records, new_records)
        else:
            raise ValueError(f"Invalid merge strategy: {merge_strategy}")
        
        # Update metadata
        metadata = {
            "updated": datetime.now().isoformat(),
            "merge_strategy": merge_strategy,
            "previous_count": len(existing_records),
            "new_records": len(new_records)
        }
        
        return self.save_to_json(merged_data, filename, metadata)
    
    def _merge_records(self, existing: List[Dict], new: List[Dict]) -> List[Dict]:
        """Merge records based on common identifier"""
        # Try to find a common identifier
        id_fields = ['id', 'ID', 'index', 'Index', 'task_id', 'project_id']
        id_field = None
        
        # Find which ID field exists in the data
        if existing and len(existing) > 0:
            for field in id_fields:
                if field in existing[0]:
                    id_field = field
                    break
        
        if not id_field:
            # No ID field found, just append
            return existing + new
        
        # Create a map of existing records
        existing_map = {record.get(id_field): record for record in existing}
        
        # Update existing and add new
        for record in new:
            record_id = record.get(id_field)
            if record_id:
                existing_map[record_id] = record
            else:
                # No ID, append to end
                existing.append(record)
        
        return list(existing_map.values())
    
    def create_backup(self, filename: str) -> str:
        """Create a backup of the JSON file"""
        if not filename.endswith('.json'):
            filename += '.json'
        
        source_path = os.path.join(self.json_dir, filename)
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {filename}")
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{os.path.splitext(filename)[0]}_{timestamp}.json"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            shutil.copy2(source_path, backup_path)
            return backup_path
        except Exception as e:
            raise Exception(f"Error creating backup: {str(e)}")
    
    def list_json_files(self) -> List[Dict[str, Any]]:
        """List all JSON files with metadata"""
        files = []
        
        for filename in os.listdir(self.json_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.json_dir, filename)
                
                # Get file info
                stat = os.stat(file_path)
                
                # Try to load metadata
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        metadata = data.get("metadata", {})
                except:
                    metadata = {}
                
                files.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "record_count": metadata.get("record_count", "Unknown"),
                    "version": metadata.get("version", "Unknown"),
                    "created": metadata.get("created", "Unknown")
                })
        
        return sorted(files, key=lambda x: x["modified"], reverse=True)
    
    def restore_from_backup(self, backup_filename: str, target_filename: str) -> str:
        """Restore a JSON file from backup"""
        backup_path = os.path.join(self.backup_dir, backup_filename)
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_filename}")
        
        if not target_filename.endswith('.json'):
            target_filename += '.json'
        
        target_path = os.path.join(self.json_dir, target_filename)
        
        try:
            shutil.copy2(backup_path, target_path)
            return target_path
        except Exception as e:
            raise Exception(f"Error restoring from backup: {str(e)}")
    
    def delete_json_file(self, filename: str, create_backup: bool = True) -> bool:
        """Delete a JSON file with optional backup"""
        if not filename.endswith('.json'):
            filename += '.json'
        
        file_path = os.path.join(self.json_dir, filename)
        
        if not os.path.exists(file_path):
            return False
        
        if create_backup:
            self.create_backup(filename)
        
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            raise Exception(f"Error deleting file: {str(e)}")
    
    def export_to_excel(self, json_filename: str, excel_filename: str) -> str:
        """Export JSON data to Excel file"""
        data = self.load_from_json(json_filename)
        records = data.get("data", [])
        
        if not records:
            raise ValueError("No data to export")
        
        # Convert to DataFrame
        df = pd.DataFrame(records)
        
        # Ensure exports directory exists
        os.makedirs("exports", exist_ok=True)
        excel_path = os.path.join("exports", excel_filename)
        
        # Write to Excel
        df.to_excel(excel_path, index=False)
        
        return excel_path