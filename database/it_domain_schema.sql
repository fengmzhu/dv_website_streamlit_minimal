-- IT Domain Database Schema - Minimal Version (it_domain.db)
-- Simplified to 5 essential fields for lightweight implementation

-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- Main projects table with 5 essential fields
CREATE TABLE it_domain_projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Auto-generated fields
    task_index VARCHAR(50) UNIQUE DEFAULT NULL,
    
    -- Essential project information (5 fields only)
    project_name VARCHAR(100) NOT NULL UNIQUE,
    dv_engineer VARCHAR(100),
    business_unit VARCHAR(10),
    ip VARCHAR(100),
    spip_url VARCHAR(500),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Minimal validation constraints 
    CHECK (business_unit IN ('CN', 'PC', '') OR business_unit IS NULL)
);

-- Indexes for performance
CREATE INDEX idx_project_name ON it_domain_projects(project_name);
CREATE INDEX idx_task_index ON it_domain_projects(task_index);
CREATE INDEX idx_dv_engineer ON it_domain_projects(dv_engineer);
CREATE INDEX idx_business_unit ON it_domain_projects(business_unit);

-- Export view for minimal fields
CREATE VIEW export_view AS
SELECT 
    task_index,
    project_name,
    dv_engineer,
    business_unit,
    ip,
    spip_url,
    created_at,
    updated_at
FROM it_domain_projects
ORDER BY task_index;

-- Trigger for auto-generating task_index
CREATE TRIGGER generate_task_index 
AFTER INSERT ON it_domain_projects
FOR EACH ROW
WHEN NEW.task_index IS NULL OR NEW.task_index = ''
BEGIN
    UPDATE it_domain_projects 
    SET task_index = 'TASK' || printf('%03d', 
        COALESCE(
            (SELECT MAX(CAST(SUBSTR(task_index, 5) AS INTEGER)) 
             FROM it_domain_projects 
             WHERE task_index GLOB 'TASK[0-9][0-9][0-9]' AND id != NEW.id), 
            0) + 1
    )
    WHERE id = NEW.id;
END;

-- Trigger for updating timestamp
CREATE TRIGGER update_timestamp_it_projects
AFTER UPDATE ON it_domain_projects
FOR EACH ROW
BEGIN
    UPDATE it_domain_projects 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- Sample data for testing (minimal fields)
INSERT INTO it_domain_projects (
    project_name, dv_engineer, business_unit, ip, spip_url
) VALUES 
('RLE1339', 'LI', 'CN', 'AFE', 'https://jira.rd.realtek.com/browse/SPIP-1234'),
('RLE1340', 'Wang', 'PC', 'DSP', 'https://jira.rd.realtek.com/browse/SPIP-1235');