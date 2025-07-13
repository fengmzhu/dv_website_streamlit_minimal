-- NX Domain Database Schema - Minimal Version (nx_domain.db)
-- Simplified to only imported IT data table for lightweight implementation

-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- Imported IT data table (CSV import from IT domain) - 8 fields only
CREATE TABLE imported_it_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name VARCHAR(100) NOT NULL,
    task_index VARCHAR(50),
    dv_engineer VARCHAR(100),
    business_unit VARCHAR(10),
    ip VARCHAR(100),
    spip_url VARCHAR(500),
    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Minimal validation constraints
    CHECK (business_unit IS NULL OR business_unit = '' OR business_unit IN ('CN', 'PC'))
);

-- Index for performance
CREATE INDEX idx_imported_project ON imported_it_data(project_name);
CREATE INDEX idx_imported_task_index ON imported_it_data(task_index);

-- Simple view for displaying all imported data
CREATE VIEW simple_view AS
SELECT 
    task_index,
    project_name,
    dv_engineer,
    business_unit,
    ip,
    spip_url,
    import_date
FROM imported_it_data
ORDER BY task_index;

-- Sample data for testing (minimal fields)
INSERT INTO imported_it_data (
    project_name, task_index, dv_engineer, business_unit, ip, spip_url
) VALUES 
('RLE1339', 'TASK001', 'LI', 'CN', 'AFE', 'https://jira.rd.realtek.com/browse/SPIP-1234'),
('RLE1340', 'TASK002', 'Wang', 'PC', 'DSP', 'https://jira.rd.realtek.com/browse/SPIP-1235');