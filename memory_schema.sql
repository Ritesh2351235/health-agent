-- Memory table for Health Agent
-- Stores user memory, analysis results, and generated plans
-- 
-- PREREQUISITES: This schema requires the existing health data tables to be present:
-- - profiles (with id TEXT PRIMARY KEY)
-- - biomarkers, scores, archetypes tables (optional but recommended)
--
-- This table references the profiles table via foreign key constraint

CREATE TABLE IF NOT EXISTS memory (
    id SERIAL PRIMARY KEY,
    profile_id TEXT NOT NULL UNIQUE REFERENCES profiles(id),
    
    -- Memory and context
    user_preferences JSONB DEFAULT '{}',
    health_goals JSONB DEFAULT '{}',
    dietary_restrictions JSONB DEFAULT '{}',
    lifestyle_context JSONB DEFAULT '{}',
    medical_conditions JSONB DEFAULT '{}',
    
    -- Analysis results
    last_analysis_date TIMESTAMPTZ,
    last_analysis_result TEXT,
    analysis_insights JSONB DEFAULT '{}',
    
    -- Generated plans (keep updating)
    last_nutrition_plan JSONB,
    last_routine_plan JSONB,
    nutrition_plan_date TIMESTAMPTZ,
    routine_plan_date TIMESTAMPTZ,
    
    -- Progress tracking
    health_trends JSONB DEFAULT '{}',
    improvement_areas JSONB DEFAULT '{}',
    success_patterns JSONB DEFAULT '{}',
    
    -- Memory metadata
    total_analyses INTEGER DEFAULT 0,
    memory_version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_memory_profile_id ON memory(profile_id);
CREATE INDEX IF NOT EXISTS idx_memory_updated_at ON memory(updated_at);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_memory_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update timestamp
CREATE TRIGGER memory_update_timestamp
    BEFORE UPDATE ON memory
    FOR EACH ROW
    EXECUTE FUNCTION update_memory_timestamp();

-- Sample insert for testing (profile_id must exist in profiles table first)
-- INSERT INTO memory (profile_id, user_preferences, health_goals) 
-- VALUES ('existing_profile_id', '{"preferred_meal_time": "evening", "exercise_preference": "morning"}', '{"target": "weight_loss", "timeline": "3_months"}'); 