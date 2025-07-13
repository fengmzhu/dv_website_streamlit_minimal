-- IT Domain Database Schema - Complete Version (it_domain.db)
-- All 17 fields as per WEBSITE_REQUIREMENTS.md specifications

-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- Main projects table with all 17 IT Domain fields
CREATE TABLE it_domain_projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Auto-generated fields
    task_index VARCHAR(50) UNIQUE DEFAULT NULL,
    
    -- Core Project Information (Required)
    project_name VARCHAR(100) NOT NULL UNIQUE,
    
    -- Project Specification Fields
    spip_ip VARCHAR(100),
    ip VARCHAR(100),
    ip_postfix VARCHAR(50),
    ip_subtype VARCHAR(50) DEFAULT 'default',
    alternative_name VARCHAR(100),
    
    -- Personnel Assignment Fields
    dv_engineer VARCHAR(100),
    digital_designer VARCHAR(100),
    analog_designer VARCHAR(100),
    business_unit VARCHAR(10),
    
    -- Documentation Fields
    spip_url VARCHAR(500),
    wiki_url VARCHAR(500),
    spec_version VARCHAR(50),
    spec_path VARCHAR(500),
    
    -- IP Management Fields
    inherit_from_ip VARCHAR(100),
    reuse_ip VARCHAR(100),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Comprehensive validation constraints
    CHECK (business_unit IN ('CN', 'PC', '') OR business_unit IS NULL),
    CHECK (ip_subtype IN ('default', 'gen2x1') OR ip_subtype IS NULL),
    CHECK (reuse_ip IN ('Y', 'N', '') OR reuse_ip IS NULL),
    CHECK (spip_url = '' OR spip_url IS NULL OR spip_url LIKE 'http%'),
    CHECK (wiki_url = '' OR wiki_url IS NULL OR wiki_url LIKE 'http%')
);

-- Indexes for performance
CREATE INDEX idx_project_name ON it_domain_projects(project_name);
CREATE INDEX idx_task_index ON it_domain_projects(task_index);
CREATE INDEX idx_dv_engineer ON it_domain_projects(dv_engineer);
CREATE INDEX idx_business_unit ON it_domain_projects(business_unit);

-- Export view for all 17 IT Domain fields
CREATE VIEW export_view AS
SELECT 
    task_index,
    project_name,
    spip_ip,
    ip,
    ip_postfix,
    ip_subtype,
    alternative_name,
    dv_engineer,
    digital_designer,
    analog_designer,
    business_unit,
    spip_url,
    wiki_url,
    spec_version,
    spec_path,
    inherit_from_ip,
    reuse_ip,
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

-- Sample data for testing (complete fields)
INSERT INTO it_domain_projects (
    project_name, spip_ip, ip, ip_postfix, ip_subtype, alternative_name,
    dv_engineer, digital_designer, analog_designer, business_unit,
    spip_url, wiki_url, spec_version, spec_path, inherit_from_ip, reuse_ip
) VALUES 
('RLE1339', 'AFE_IP', 'AFE', 'v2', 'default', 'RealTek1339',
 'LI', 'Zhang', 'Chen', 'CN',
 'https://jira.rd.realtek.com/browse/SPIP-1234', 'https://wiki.rd.realtek.com/display/RLE1339/',
 'v1.2', '/specs/RLE1339_spec_v1.2.pdf', 'RLE1300', 'N'),
('RLE1340', 'DSP_IP', 'DSP', 'support 4/4', 'gen2x1', 'RealTek1340',
 'Wang', 'Liu', 'Wu', 'PC',
 'https://jira.rd.realtek.com/browse/SPIP-1235', 'https://wiki.rd.realtek.com/display/RLE1340/',
 'v2.0', '/specs/RLE1340_spec_v2.0.pdf', 'RLE1320', 'Y');