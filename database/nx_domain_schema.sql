-- NX Domain Database Schema - Production Architecture (nx_domain.db)
-- Complete schema for all 33 fields (17 IT + 16 NX) with external MySQL integration design

-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- Imported IT data table (from IT Domain CSV) - All 17 IT fields
CREATE TABLE imported_it_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- Core project info
    project_name VARCHAR(100) NOT NULL,
    task_index VARCHAR(50),
    -- Project specifications  
    spip_ip VARCHAR(100),
    ip VARCHAR(100),
    ip_postfix VARCHAR(50),
    ip_subtype VARCHAR(50),
    alternative_name VARCHAR(100),
    -- Personnel assignments
    dv_engineer VARCHAR(100),
    digital_designer VARCHAR(100),
    analog_designer VARCHAR(100),
    business_unit VARCHAR(10),
    -- Documentation
    spip_url VARCHAR(500),
    wiki_url VARCHAR(500),
    spec_version VARCHAR(50),
    spec_path VARCHAR(500),
    -- IP management
    inherit_from_ip VARCHAR(100),
    reuse_ip VARCHAR(100),
    -- Metadata
    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Validation constraints
    CHECK (business_unit IS NULL OR business_unit = '' OR business_unit IN ('CN', 'PC')),
    CHECK (ip_subtype IS NULL OR ip_subtype = '' OR ip_subtype IN ('default', 'gen2x1')),
    CHECK (reuse_ip IS NULL OR reuse_ip = '' OR reuse_ip IN ('Y', 'N'))
);

-- NX Domain specific data table (auto-collected from regression systems)
-- This table will be populated by external MySQL database in production
CREATE TABLE nx_regression_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name VARCHAR(100) NOT NULL,
    
    -- Coverage Metrics (auto-collected from DV tools)
    line_coverage DECIMAL(5,2),
    fsm_coverage DECIMAL(5,2), 
    interface_toggle_coverage DECIMAL(5,2),
    toggle_coverage DECIMAL(5,2),
    coverage_report_path VARCHAR(500),
    
    -- Version Control Fields (auto-collected)
    sanity_svn VARCHAR(500),
    sanity_svn_ver VARCHAR(100),
    release_svn VARCHAR(500),
    release_svn_ver VARCHAR(100),
    git_path VARCHAR(500),
    git_version VARCHAR(100),
    
    -- Checklist Fields (auto-collected)
    golden_checklist VARCHAR(500),
    golden_checklist_version VARCHAR(100),
    
    -- Temporal Fields (auto-collected)
    to_date DATE,
    rtl_last_update TIMESTAMP,
    to_report_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Data collection metadata
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(100) DEFAULT 'regression_system',
    
    -- Foreign key to imported IT data
    FOREIGN KEY (project_name) REFERENCES imported_it_data(project_name),
    
    -- NX Domain validation constraints
    CHECK (line_coverage IS NULL OR (line_coverage >= 0 AND line_coverage <= 100)),
    CHECK (fsm_coverage IS NULL OR (fsm_coverage >= 0 AND fsm_coverage <= 100)),
    CHECK (interface_toggle_coverage IS NULL OR (interface_toggle_coverage >= 0 AND interface_toggle_coverage <= 100)),
    CHECK (toggle_coverage IS NULL OR (toggle_coverage >= 0 AND toggle_coverage <= 100)),
    CHECK (coverage_report_path IS NULL OR coverage_report_path = '' OR 
           coverage_report_path LIKE '%.html' OR coverage_report_path LIKE '/project/%'),
    CHECK (sanity_svn IS NULL OR sanity_svn = '' OR sanity_svn LIKE 'http%'),
    CHECK (release_svn IS NULL OR release_svn = '' OR release_svn LIKE 'http%'),
    CHECK (git_path IS NULL OR git_path = '' OR 
           git_path LIKE 'ssh://git.%' OR git_path LIKE 'https://git%'),
    CHECK (git_version IS NULL OR git_version = '' OR 
           LENGTH(git_version) = 40 OR LENGTH(git_version) <= 10)
);

-- Index for performance
CREATE INDEX idx_imported_project ON imported_it_data(project_name);
CREATE INDEX idx_imported_task_index ON imported_it_data(task_index);

-- Performance indexes
CREATE INDEX idx_nx_project ON nx_regression_data(project_name);
CREATE INDEX idx_nx_coverage ON nx_regression_data(line_coverage, fsm_coverage, toggle_coverage);
CREATE INDEX idx_nx_updated ON nx_regression_data(last_updated);

-- Simple view for displaying imported IT data
CREATE VIEW imported_it_view AS
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
    import_date
FROM imported_it_data
ORDER BY task_index;

-- Complete TO Summary view (all 33 fields) - Production ready
CREATE VIEW to_summary_view AS
SELECT 
    -- IT Domain fields (17)
    it.task_index,
    it.project_name,
    it.spip_ip,
    it.ip,
    it.ip_postfix,
    it.ip_subtype,
    it.alternative_name,
    it.dv_engineer,
    it.digital_designer,
    it.analog_designer,
    it.business_unit,
    it.spip_url,
    it.wiki_url,
    it.spec_version,
    it.spec_path,
    it.inherit_from_ip,
    it.reuse_ip,
    
    -- NX Domain fields (16)
    nx.line_coverage,
    nx.fsm_coverage,
    nx.interface_toggle_coverage,
    nx.toggle_coverage,
    nx.coverage_report_path,
    nx.sanity_svn,
    nx.sanity_svn_ver,
    nx.release_svn,
    nx.release_svn_ver,
    nx.git_path,
    nx.git_version,
    nx.golden_checklist,
    nx.golden_checklist_version,
    nx.to_date,
    nx.rtl_last_update,
    nx.to_report_creation,
    
    -- Metadata
    it.import_date,
    nx.last_updated as nx_last_updated,
    nx.data_source
FROM imported_it_data it
LEFT JOIN nx_regression_data nx ON it.project_name = nx.project_name
ORDER BY it.task_index;

-- Coverage quality analysis view
CREATE VIEW coverage_analysis_view AS
SELECT 
    project_name,
    task_index,
    line_coverage,
    fsm_coverage,
    interface_toggle_coverage,
    toggle_coverage,
    -- Calculate average coverage
    ROUND((COALESCE(line_coverage, 0) + COALESCE(fsm_coverage, 0) + 
           COALESCE(interface_toggle_coverage, 0) + COALESCE(toggle_coverage, 0)) / 4.0, 2) as avg_coverage,
    -- Coverage quality assessment
    CASE 
        WHEN COALESCE(line_coverage, 0) >= 90 AND COALESCE(fsm_coverage, 0) >= 90 AND 
             COALESCE(toggle_coverage, 0) >= 90 THEN 'Excellent'
        WHEN COALESCE(line_coverage, 0) >= 70 AND COALESCE(fsm_coverage, 0) >= 70 AND 
             COALESCE(toggle_coverage, 0) >= 70 THEN 'Good'
        WHEN COALESCE(line_coverage, 0) >= 50 AND COALESCE(fsm_coverage, 0) >= 50 AND 
             COALESCE(toggle_coverage, 0) >= 50 THEN 'Fair'
        WHEN line_coverage IS NULL AND fsm_coverage IS NULL AND toggle_coverage IS NULL THEN 'No Data'
        ELSE 'Poor'
    END as coverage_quality,
    coverage_report_path,
    last_updated
FROM nx_regression_data
ORDER BY avg_coverage DESC;

-- Sample data for testing (complete IT fields)
INSERT INTO imported_it_data (
    project_name, task_index, spip_ip, ip, ip_postfix, ip_subtype, alternative_name,
    dv_engineer, digital_designer, analog_designer, business_unit,
    spip_url, wiki_url, spec_version, spec_path, inherit_from_ip, reuse_ip
) VALUES 
('RLE1339', 'TASK001', 'AFE_IP', 'AFE', 'v2', 'default', 'RealTek1339',
 'LI', 'Zhang', 'Chen', 'CN',
 'https://jira.rd.realtek.com/browse/SPIP-1234', 'https://wiki.rd.realtek.com/display/RLE1339/',
 'v1.2', '/specs/RLE1339_spec_v1.2.pdf', 'RLE1300', 'N'),
('RLE1340', 'TASK002', 'DSP_IP', 'DSP', 'support 4/4', 'gen2x1', 'RealTek1340',
 'Wang', 'Liu', 'Wu', 'PC',
 'https://jira.rd.realtek.com/browse/SPIP-1235', 'https://wiki.rd.realtek.com/display/RLE1340/',
 'v2.0', '/specs/RLE1340_spec_v2.0.pdf', 'RLE1320', 'Y');

-- Sample NX regression data (demonstrates full 33-field TO Summary)
INSERT INTO nx_regression_data (
    project_name, line_coverage, fsm_coverage, interface_toggle_coverage, toggle_coverage,
    coverage_report_path, sanity_svn, sanity_svn_ver, release_svn, release_svn_ver,
    git_path, git_version, golden_checklist, golden_checklist_version,
    to_date, rtl_last_update
) VALUES 
('RLE1339', 95.5, 87.2, 92.1, 89.8,
 '/project/RLE1339/coverage/RLE1339_coverage.html',
 'http://svn.rd.realtek.com/RLE1339/sanity', 'r12456',
 'http://svn.rd.realtek.com/RLE1339/release', 'r12500',
 'ssh://git.rd.realtek.com/RLE1339.git', 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0',
 '/golden/RLE1339_checklist.xls', 'v1.5',
 '2025-08-15', '2025-07-12 14:30:00'),
('RLE1340', 78.3, 91.7, 85.4, 82.9,
 '/project/RLE1340/coverage/RLE1340_coverage.html',
 'http://svn.rd.realtek.com/RLE1340/sanity', 'r11890',
 'http://svn.rd.realtek.com/RLE1340/release', 'r11925',
 'ssh://git.rd.realtek.com/RLE1340.git', 'v2.1.0',
 '/golden/RLE1340_checklist.xls', 'v2.0',
 '2025-09-01', '2025-07-10 16:45:00');