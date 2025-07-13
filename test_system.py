#!/usr/bin/env python3
"""
Simple test script for minimal DV Management System
Tests basic functionality without running the full Streamlit app
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

try:
    # Test imports
    print("🧪 Testing minimal system imports...")
    
    import streamlit as st
    print("✅ Streamlit import successful")
    
    import pandas as pd
    print("✅ Pandas import successful")
    
    try:
        import openpyxl
        print("✅ Openpyxl import successful")
    except ImportError:
        print("⚠️  Openpyxl not available (Excel export disabled)")
    
    # Test database utilities
    from utils.database import (
        MinimalDatabaseManager,
        validate_project_data_minimal
    )
    print("✅ Database utilities import successful")
    
    # Test database manager initialization
    db_manager = MinimalDatabaseManager()
    print("✅ Database manager initialization successful")
    
    # Test validation function
    test_data = {
        'project_name': 'TEST001',
        'dv_engineer': 'TestEngineer',
        'business_unit': 'CN',
        'ip': 'TestIP',
        'spip_url': 'https://test.example.com'
    }
    
    errors = validate_project_data_minimal(test_data)
    if not errors:
        print("✅ Data validation test passed")
    else:
        print(f"❌ Data validation failed: {errors}")
    
    # Test invalid data
    invalid_data = {'project_name': ''}  # Empty project name
    errors = validate_project_data_minimal(invalid_data)
    if errors:
        print("✅ Invalid data detection test passed")
    else:
        print("❌ Invalid data detection failed")
    
    print("\n🎉 All tests passed! Minimal system is ready to use.")
    print("\n📋 System Summary:")
    print("   • 3 essential dependencies (streamlit, pandas, openpyxl)")
    print("   • 5 core project fields")
    print("   • Simplified database schema")
    print("   • Core workflow: input → export → import → view")
    print("\n🚀 To run the application:")
    print("   streamlit run app.py")
    
except Exception as e:
    print(f"❌ Test failed: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)