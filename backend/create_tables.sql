-- Create tables for PBL course system in textloom_core schema
SET search_path TO textloom_core, public;

-- Base model fields that will be in all tables
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    -- Course basic info
    title VARCHAR(200) NOT NULL,
    subtitle VARCHAR(500),
    description TEXT,
    summary TEXT,

    -- Category info
    subject VARCHAR(50) NOT NULL,
    subjects VARCHAR(50)[],
    education_level VARCHAR(20) NOT NULL,
    grade_levels INTEGER[],

    -- Course attributes
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    difficulty_level VARCHAR(20) DEFAULT 'intermediate',
    duration_weeks INTEGER NOT NULL,
    duration_hours INTEGER NOT NULL,
    class_size_min INTEGER DEFAULT 15,
    class_size_max INTEGER DEFAULT 35,

    -- Course goals
    learning_objectives JSONB,
    core_competencies JSONB,
    assessment_criteria JSONB,

    -- Project info
    project_context TEXT,
    driving_question TEXT,
    final_products JSONB,
    authentic_assessment JSONB,

    -- Course structure
    phases JSONB,
    milestones JSONB,
    scaffolding_supports JSONB,

    -- Resource configuration
    required_resources JSONB,
    recommended_resources JSONB,
    technology_requirements JSONB,

    -- Teacher guidance
    teacher_preparation JSONB,
    teaching_strategies JSONB,
    differentiation_strategies JSONB,

    -- Quality metrics
    quality_score REAL DEFAULT 0.0,
    completion_rate REAL DEFAULT 0.0,
    satisfaction_score REAL DEFAULT 0.0,

    -- Publishing info
    is_public BOOLEAN DEFAULT FALSE,
    is_template BOOLEAN DEFAULT FALSE,
    template_category VARCHAR(100),

    -- Version control
    version_number VARCHAR(20) DEFAULT '1.0.0',
    parent_course_id UUID REFERENCES courses(id),

    -- Statistics
    view_count INTEGER DEFAULT 0,
    use_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0
);

-- Lessons table
CREATE TABLE IF NOT EXISTS lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    objectives JSONB,

    -- Order and timing
    sequence_number INTEGER NOT NULL,
    duration_minutes INTEGER NOT NULL,
    phase VARCHAR(50),

    -- Content structure
    activities JSONB,
    materials JSONB,
    homework JSONB,

    -- Teaching design
    teaching_methods JSONB,
    student_grouping VARCHAR(50),
    teacher_notes TEXT
);

-- Assessments table
CREATE TABLE IF NOT EXISTS assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,

    title VARCHAR(200) NOT NULL,
    description TEXT,
    type VARCHAR(20) NOT NULL,

    -- Assessment configuration
    criteria JSONB,
    rubric JSONB,
    weight REAL DEFAULT 1.0,

    -- Time arrangement
    due_date_offset INTEGER,
    estimated_time INTEGER
);

-- Resources table
CREATE TABLE IF NOT EXISTS resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,

    title VARCHAR(200) NOT NULL,
    description TEXT,
    type VARCHAR(20) NOT NULL,

    -- Resource info
    url VARCHAR(500),
    file_path VARCHAR(500),
    file_size INTEGER,
    mime_type VARCHAR(100),

    -- Usage configuration
    is_required BOOLEAN DEFAULT FALSE,
    access_level VARCHAR(20) DEFAULT 'public'
);

-- Tags table
CREATE TABLE IF NOT EXISTS tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7),
    use_count INTEGER DEFAULT 0
);

-- Course-Tag association table
CREATE TABLE IF NOT EXISTS course_tags (
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (course_id, tag_id)
);

-- Users table (simplified for now)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,

    -- Personal info
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    display_name VARCHAR(100),

    -- Role and permissions
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    status VARCHAR(20) NOT NULL DEFAULT 'inactive'
);

-- Course collaborators table
CREATE TABLE IF NOT EXISTS course_collaborators (
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'collaborator',
    permissions JSONB DEFAULT '{}',
    PRIMARY KEY (course_id, user_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_courses_subject ON courses(subject);
CREATE INDEX IF NOT EXISTS idx_courses_education_level ON courses(education_level);
CREATE INDEX IF NOT EXISTS idx_courses_status ON courses(status);
CREATE INDEX IF NOT EXISTS idx_lessons_course_id ON lessons(course_id);
CREATE INDEX IF NOT EXISTS idx_lessons_sequence ON lessons(course_id, sequence_number);
CREATE INDEX IF NOT EXISTS idx_assessments_course_id ON assessments(course_id);
CREATE INDEX IF NOT EXISTS idx_resources_course_id ON resources(course_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

COMMENT ON SCHEMA textloom_core IS 'PBL Course Design System Schema';