-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Apps table
CREATE TABLE apps (
    id SERIAL PRIMARY KEY,
    package_name VARCHAR(255) UNIQUE NOT NULL,
    app_name VARCHAR(255) NOT NULL,
    developer VARCHAR(255),
    category VARCHAR(100),
    platform VARCHAR(20) CHECK (platform IN ('android', 'ios', 'both')),
    icon_url TEXT,
    privacy_policy_url TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis results table
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    app_id INTEGER REFERENCES apps(id) ON DELETE CASCADE,
    app_version VARCHAR(50),
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    overall_score INTEGER CHECK (overall_score BETWEEN 0 AND 100),
    privacy_score INTEGER CHECK (privacy_score BETWEEN 0 AND 100),
    transparency_score INTEGER CHECK (transparency_score BETWEEN 0 AND 100),
    resource_score INTEGER CHECK (resource_score BETWEEN 0 AND 100),
    design_score INTEGER CHECK (design_score BETWEEN 0 AND 100),
    
    trackers JSONB,
    permissions JSONB,
    policy_analysis JSONB,
    review_summary JSONB,
    
    scoring_version VARCHAR(20) DEFAULT 'v1.0.0',
    analysis_duration_seconds INTEGER,
    
    CONSTRAINT unique_app_analysis UNIQUE(app_id, analyzed_at)
);

-- Indexes for performance
CREATE INDEX idx_apps_package_name ON apps(package_name);
CREATE INDEX idx_apps_category ON apps(category);
CREATE INDEX idx_analysis_app_id ON analysis_results(app_id);
CREATE INDEX idx_analysis_date ON analysis_results(analyzed_at DESC);
CREATE INDEX idx_analysis_overall_score ON analysis_results(overall_score);

-- Full-text search
ALTER TABLE apps ADD COLUMN search_vector tsvector;
CREATE INDEX idx_apps_search ON apps USING GIN(search_vector);

-- Trigger to update search_vector
CREATE OR REPLACE FUNCTION update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', 
        COALESCE(NEW.app_name, '') || ' ' || COALESCE(NEW.developer, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER apps_search_update 
    BEFORE INSERT OR UPDATE ON apps
    FOR EACH ROW EXECUTE FUNCTION update_search_vector();

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER apps_updated_at 
    BEFORE UPDATE ON apps
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
