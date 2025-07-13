# DV Website Domain Specifications & Field Requirements

## Overview
The DV Website is a dual-domain system for Design Verification (DV) project management in semiconductor/engineering companies. The system consists of two interconnected domains that together provide a complete 33-field TO (Tape Out) Summary Report.

## Domain Architecture

### IT Domain - Project Management & Personnel
- **Purpose**: Capture project information, personnel assignments, and design specifications
- **Field Count**: 17 fields total
- **Entry Type**: Manual data entry through web forms
- **Primary Function**: Project tracking and resource management

### NX Domain - DV Regression & Coverage
- **Purpose**: Track DV test results, coverage metrics, and version control
- **Field Count**: 16 additional fields (33 total in TO Summary)
- **Entry Type**: All fields auto-collected from regression results and tools
- **Primary Function**: Technical verification metrics and tape-out readiness

## IT Domain Field Specifications (17 Fields)

### 1. Index (Auto-generated)
- **Field Name**: `task_index`
- **Type**: VARCHAR(50)
- **Format**: TASK001, TASK002, etc.
- **Constraints**: Unique, auto-generated via database trigger
- **Purpose**: Sequential task identifier

### 2. Project (Required)
- **Field Name**: `project_name`
- **Type**: VARCHAR(100)
- **Constraints**: NOT NULL, UNIQUE
- **Purpose**: Primary project identifier linking both domains
- **Notes**: Main key for cross-domain data integration

### 3. SPIP_IP
- **Field Name**: `spip_ip`
- **Type**: VARCHAR(100)
- **Purpose**: IP classification from project management system
- **Source**: Originally from allproject.xlsx

### 4. IP
- **Field Name**: `ip`
- **Type**: VARCHAR(100)
- **Purpose**: IP component name/identifier (e.g., AFE, DSP, PCIe)
- **Notes**: Core technical component being verified

### 5. IP Postfix
- **Field Name**: `ip_postfix`
- **Type**: VARCHAR(50)
- **Purpose**: IP variant identifier (e.g., "v2", "support 4/4")
- **Notes**: Version or configuration details

### 6. IP Subtype
- **Field Name**: `ip_subtype`
- **Type**: VARCHAR(50)
- **Constraints**: Must be 'default' or 'gen2x1'
- **Default**: 'default'
- **Purpose**: IP subtype classification

### 7. Alternative Name
- **Field Name**: `alternative_name`
- **Type**: VARCHAR(100)
- **Purpose**: Alternative project designation
- **Notes**: Secondary identifier if needed

### 8. DV (Design Verification Engineer)
- **Field Name**: `dv_engineer`
- **Type**: VARCHAR(100)
- **Purpose**: Assigned DV engineer name/ID
- **Notes**: Primary responsible engineer

### 9. DD (Digital Designer)
- **Field Name**: `digital_designer`
- **Type**: VARCHAR(100)
- **Purpose**: Digital design engineer name
- **Notes**: Digital circuit designer

### 10. BU (Business Unit)
- **Field Name**: `business_unit`
- **Type**: VARCHAR(10)
- **Constraints**: Must be 'CN', 'PC', or empty
- **Purpose**: Business unit classification
- **Values**:
  - CN: China team
  - PC: PC team
  - Empty: Unassigned

### 11. AD (Analog Designer)
- **Field Name**: `analog_designer`
- **Type**: VARCHAR(100)
- **Purpose**: Analog design engineer name
- **Notes**: Analog circuit designer

### 12. SPIP URL
- **Field Name**: `spip_url`
- **Type**: VARCHAR(500)
- **Constraints**: Must start with 'http' or be empty
- **Purpose**: JIRA/SPIP project tracking URL
- **Format**: https://jira.rd.company.com/browse/SPIP-XXXX

### 13. Wiki URL
- **Field Name**: `wiki_url`
- **Type**: VARCHAR(500)
- **Constraints**: Must start with 'http' or be empty
- **Purpose**: Project wiki documentation URL
- **Format**: https://wiki.company.com/display/PROJECT/

### 14. Spec Version
- **Field Name**: `spec_version`
- **Type**: VARCHAR(50)
- **Purpose**: Specification document version
- **Format**: v1.0, v2.1, etc.

### 15. Spec Path
- **Field Name**: `spec_path`
- **Type**: VARCHAR(500)
- **Purpose**: Path to specification document
- **Format**: /specs/project_name_v1.0.pdf

### 16. Inherit from IP
- **Field Name**: `inherit_from_ip`
- **Type**: VARCHAR(100)
- **Purpose**: Parent IP project reference
- **Notes**: Links to previous project if IP is inherited

### 17. Re-use IP
- **Field Name**: `reuse_ip`
- **Type**: VARCHAR(100)
- **Constraints**: Must be 'Y', 'N', or empty
- **Purpose**: IP reuse indicator
- **Values**:
  - Y: IP is reused from another project
  - N: New IP development
  - Empty: Status undefined

## NX Domain Field Specifications (16 Additional Fields)

### Coverage Metrics (Auto-generated from DV Tools)

#### 18. Line Coverage
- **Field Name**: `line_coverage`
- **Type**: DECIMAL(5,2)
- **Constraints**: 0-100% or NULL
- **Purpose**: Code line execution coverage percentage
- **Source**: DV regression tools

#### 19. FSM Coverage
- **Field Name**: `fsm_coverage`
- **Type**: DECIMAL(5,2)
- **Constraints**: 0-100% or NULL
- **Purpose**: Finite State Machine coverage percentage
- **Source**: DV regression tools

#### 20. Interface Toggle Coverage
- **Field Name**: `interface_toggle_coverage`
- **Type**: DECIMAL(5,2)
- **Constraints**: 0-100% or NULL
- **Purpose**: Interface signal toggle coverage percentage
- **Source**: DV regression tools

#### 21. Toggle Coverage
- **Field Name**: `toggle_coverage`
- **Type**: DECIMAL(5,2)
- **Constraints**: 0-100% or NULL
- **Purpose**: General signal toggle coverage percentage
- **Source**: DV regression tools

#### 22. Coverage Report Path
- **Field Name**: `coverage_report_path`
- **Type**: VARCHAR(500)
- **Constraints**: Must end with .html or start with /project/
- **Purpose**: Path to detailed HTML coverage report
- **Format**: /project/coverage/PROJECT_coverage.html

### Version Control Fields

#### 23. Sanity SVN
- **Field Name**: `sanity_svn`
- **Type**: VARCHAR(500)
- **Constraints**: Must start with 'http' or be empty
- **Purpose**: SVN repository path for sanity test environment
- **Source**: Auto-collected from regression environment

#### 24. Sanity SVN Version
- **Field Name**: `sanity_svn_ver`
- **Type**: VARCHAR(100)
- **Purpose**: SVN revision number for sanity environment
- **Source**: Auto-generated from SVN

#### 25. Release SVN
- **Field Name**: `release_svn`
- **Type**: VARCHAR(500)
- **Constraints**: Must start with 'http' or be empty
- **Purpose**: SVN repository path for release environment
- **Source**: Auto-collected from regression environment

#### 26. Release SVN Version
- **Field Name**: `release_svn_ver`
- **Type**: VARCHAR(100)
- **Purpose**: SVN revision number for release environment
- **Source**: Auto-generated from SVN

#### 27. Git Path
- **Field Name**: `git_path`
- **Type**: VARCHAR(500)
- **Constraints**: Must start with 'ssh://git.' or 'https://git' or be empty
- **Purpose**: Git repository URL
- **Format**: ssh://git.company.com/PROJECT.git
- **Source**: Auto-collected from regression environment

#### 28. Git Version
- **Field Name**: `git_version`
- **Type**: VARCHAR(100)
- **Constraints**: 40-character hex hash or ≤10-character tag
- **Purpose**: Git commit hash or tag
- **Source**: Auto-generated from Git

### Checklist and Reporting Fields

#### 29. Golden Checklist
- **Field Name**: `golden_checklist`
- **Type**: VARCHAR(500)
- **Purpose**: Path to golden checklist file
- **Source**: Auto-collected from regression results
- **Format**: /golden/PROJECT_checklist.xls

#### 30. Golden Checklist Version
- **Field Name**: `golden_checklist_version`
- **Type**: VARCHAR(100)
- **Purpose**: Checklist version identifier
- **Source**: Auto-collected from regression results

### Temporal Fields

#### 31. TO Date
- **Field Name**: `to_date`
- **Type**: DATE
- **Purpose**: Target tape-out date
- **Source**: Auto-collected from DV schedule system

#### 32. RTL Last Update
- **Field Name**: `rtl_last_update`
- **Type**: TIMESTAMP
- **Purpose**: Last RTL code modification timestamp
- **Source**: Auto-generated from repository

#### 33. TO Report Creation
- **Field Name**: `to_report_creation`
- **Type**: TIMESTAMP
- **Purpose**: Timestamp when TO report was generated
- **Source**: Auto-generated during report creation

## Domain Constraints and Business Rules

### IT Domain Constraints
1. **Required Fields**: Only `project_name` is mandatory for initial entry
2. **Unique Constraint**: `project_name` must be unique across the system
3. **Auto-generation**: `task_index` is automatically assigned
4. **URL Validation**: SPIP and Wiki URLs must start with 'http' if provided
5. **Enum Constraints**:
   - `ip_subtype`: 'default' or 'gen2x1'
   - `business_unit`: 'CN', 'PC', or empty
   - `reuse_ip`: 'Y', 'N', or empty

### NX Domain Constraints
1. **Coverage Validation**: All coverage percentages must be 0-100 or NULL
2. **Project Linking**: Uses `project_name` to join with IT Domain data
3. **Version Control**: SVN paths must start with 'http', Git paths with 'ssh://git.' or 'https://git'
4. **Git Hash**: Must be 40-character hex string or ≤10-character tag
5. **Report Path**: Must end with .html or start with /project/

### Coverage Quality Thresholds
- **Excellent**: ≥ 90%
- **Good**: 70-89%
- **Fair**: 50-69%
- **Poor**: < 50%
- **No Data**: NULL values

## Data Flow and Integration

### Workflow
1. **IT Domain Entry**: Engineers manually enter project data (17 fields)
2. **IT Domain Export**: Export all project data as CSV
3. **NX Domain Import**: Import IT Domain CSV data
4. **NX Domain Enhancement**: Add coverage metrics and version control data
5. **TO Summary Generation**: Combine all 33 fields for final report

### Integration Points
- **Primary Key**: `project_name` links data between domains
- **Data Direction**: IT Domain → NX Domain (one-way flow)
- **Export Format**: CSV with all 17 IT fields preserved
- **Import Validation**: NX Domain validates IT data during import

## Field Entry Summary

### Manual Entry Fields (16 total)
**IT Domain (16)**:
- All IT Domain fields except `task_index` (auto-generated)

**NX Domain (0)**:
- All NX Domain fields are auto-collected from regression results

### Auto-generated Fields (17 total)
**IT Domain (1)**:
- `task_index`

**NX Domain (16)**:
- All 16 NX Domain fields are auto-collected from regression results and tools

## Implementation Notes

1. **Data Integrity**: Maintain referential integrity using `project_name` as the linking key
2. **Null Handling**: Most fields allow NULL/empty values except `project_name`
3. **Validation Timing**: Apply constraints at both application and database levels
4. **Export Completeness**: Always export all 17 IT fields, even if empty
5. **Import Flexibility**: NX Domain should handle missing IT projects gracefully