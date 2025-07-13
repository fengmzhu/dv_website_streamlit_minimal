# DV Management System - Minimal

Ultra-lightweight implementation with only essential dependencies and core functionality.

## Quick Start

```bash
# Install minimal dependencies (only 3 packages)
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

## Architecture

**Dependencies (3 packages only):**
- `streamlit` - Core web framework
- `pandas` - Data manipulation for CSV handling
- `openpyxl` - Excel export functionality

**Core Workflow:**
1. **IT Domain**: Add projects (5 essential fields)
2. **IT Domain**: Export data as CSV
3. **NX Domain**: Import CSV data
4. **NX Domain**: View integrated data

## Files Structure

```
dv_website_streamlit_minimal/
├── app.py                           # Main application
├── requirements.txt                 # Minimal dependencies
├── pages/
│   ├── 1_📊_IT_Domain.py           # IT Domain interface
│   └── 2_📈_NX_Domain.py           # NX Domain interface
├── utils/
│   └── database.py                 # Database utilities
└── database/
    ├── it_domain_schema.sql        # IT database schema
    └── nx_domain_schema.sql        # NX database schema
```

## Key Simplifications

- **Fields**: Reduced from 17 to 5 essential fields
- **Dependencies**: Reduced from 10+ to 3 packages
- **Features**: Core workflow only (no charts, complex UI)
- **Code**: ~70% reduction in complexity
- **Performance**: Much faster startup and execution

## Essential Fields

**IT Domain (5 fields):**
1. `project_name` (required)
2. `dv_engineer`
3. `business_unit` ('CN', 'PC', or empty)
4. `ip`
5. `spip_url`

**NX Domain:**
- Simple import of IT data
- Basic table view
- Export functionality