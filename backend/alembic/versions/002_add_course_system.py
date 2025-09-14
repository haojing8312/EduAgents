"""Add course system tables

Revision ID: 002
Revises: 001
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Create course system tables"""
    
    # Tags table
    op.create_table(
        'tags',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(50), nullable=False, unique=True),
        sa.Column('description', sa.Text),
        sa.Column('color', sa.String(7)),
        sa.Column('use_count', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True)),
        sa.Column('updated_by', UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('metadata', JSON)
    )
    
    # Courses table
    op.create_table(
        'courses',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('subtitle', sa.String(500)),
        sa.Column('description', sa.Text),
        sa.Column('summary', sa.Text),
        sa.Column('subject', sa.String(50), nullable=False),
        sa.Column('subjects', ARRAY(sa.String)),
        sa.Column('education_level', sa.String(20), nullable=False),
        sa.Column('grade_levels', ARRAY(sa.Integer)),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('difficulty_level', sa.String(20), default='intermediate'),
        sa.Column('duration_weeks', sa.Integer, nullable=False),
        sa.Column('duration_hours', sa.Integer, nullable=False),
        sa.Column('class_size_min', sa.Integer, default=15),
        sa.Column('class_size_max', sa.Integer, default=35),
        sa.Column('learning_objectives', JSON),
        sa.Column('core_competencies', JSON),
        sa.Column('assessment_criteria', JSON),
        sa.Column('project_context', sa.Text),
        sa.Column('driving_question', sa.Text),
        sa.Column('final_products', JSON),
        sa.Column('authentic_assessment', JSON),
        sa.Column('phases', JSON),
        sa.Column('milestones', JSON),
        sa.Column('scaffolding_supports', JSON),
        sa.Column('required_resources', JSON),
        sa.Column('recommended_resources', JSON),
        sa.Column('technology_requirements', JSON),
        sa.Column('teacher_preparation', JSON),
        sa.Column('teaching_strategies', JSON),
        sa.Column('differentiation_strategies', JSON),
        sa.Column('quality_score', sa.Float, default=0.0),
        sa.Column('completion_rate', sa.Float, default=0.0),
        sa.Column('satisfaction_score', sa.Float, default=0.0),
        sa.Column('is_public', sa.Boolean, default=False),
        sa.Column('is_template', sa.Boolean, default=False),
        sa.Column('template_category', sa.String(100)),
        sa.Column('version_number', sa.String(20), default='1.0.0'),
        sa.Column('parent_course_id', UUID(as_uuid=True), sa.ForeignKey('courses.id')),
        sa.Column('view_count', sa.Integer, default=0),
        sa.Column('use_count', sa.Integer, default=0),
        sa.Column('like_count', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True)),
        sa.Column('updated_by', UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('metadata', JSON)
    )
    
    # Lessons table
    op.create_table(
        'lessons',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('course_id', UUID(as_uuid=True), sa.ForeignKey('courses.id'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('objectives', JSON),
        sa.Column('sequence_number', sa.Integer, nullable=False),
        sa.Column('duration_minutes', sa.Integer, nullable=False),
        sa.Column('phase', sa.String(50)),
        sa.Column('activities', JSON),
        sa.Column('materials', JSON),
        sa.Column('homework', JSON),
        sa.Column('teaching_methods', JSON),
        sa.Column('student_grouping', sa.String(50)),
        sa.Column('teacher_notes', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True)),
        sa.Column('updated_by', UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('metadata', JSON)
    )
    
    # Assessments table
    op.create_table(
        'assessments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('course_id', UUID(as_uuid=True), sa.ForeignKey('courses.id'), nullable=False),
        sa.Column('lesson_id', UUID(as_uuid=True), sa.ForeignKey('lessons.id')),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('criteria', JSON),
        sa.Column('rubric', JSON),
        sa.Column('weight', sa.Float, default=1.0),
        sa.Column('due_date_offset', sa.Integer),
        sa.Column('estimated_time', sa.Integer),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True)),
        sa.Column('updated_by', UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('metadata', JSON)
    )
    
    # Resources table
    op.create_table(
        'resources',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('course_id', UUID(as_uuid=True), sa.ForeignKey('courses.id'), nullable=False),
        sa.Column('lesson_id', UUID(as_uuid=True), sa.ForeignKey('lessons.id')),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('url', sa.String(500)),
        sa.Column('file_path', sa.String(500)),
        sa.Column('file_size', sa.Integer),
        sa.Column('mime_type', sa.String(100)),
        sa.Column('is_required', sa.Boolean, default=False),
        sa.Column('access_level', sa.String(20), default='public'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True)),
        sa.Column('updated_by', UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('metadata', JSON)
    )
    
    # Course templates table
    op.create_table(
        'course_templates',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('template_data', JSON, nullable=False),
        sa.Column('preview_image', sa.String(500)),
        sa.Column('subjects', ARRAY(sa.String)),
        sa.Column('education_levels', ARRAY(sa.String)),
        sa.Column('use_count', sa.Integer, default=0),
        sa.Column('rating', sa.Float, default=0.0),
        sa.Column('course_id', UUID(as_uuid=True), sa.ForeignKey('courses.id')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True)),
        sa.Column('updated_by', UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('metadata', JSON)
    )
    
    # Course exports table
    op.create_table(
        'course_exports',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('course_id', UUID(as_uuid=True), sa.ForeignKey('courses.id'), nullable=False),
        sa.Column('format', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('export_options', JSON),
        sa.Column('file_path', sa.String(500)),
        sa.Column('file_size', sa.Integer),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('error_message', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True)),
        sa.Column('updated_by', UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('metadata', JSON)
    )
    
    # Course reviews table
    op.create_table(
        'course_reviews',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('course_id', UUID(as_uuid=True), sa.ForeignKey('courses.id'), nullable=False),
        sa.Column('reviewer_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('rating', sa.Integer, nullable=False),
        sa.Column('title', sa.String(200)),
        sa.Column('content', sa.Text),
        sa.Column('content_quality', sa.Integer),
        sa.Column('teaching_design', sa.Integer),
        sa.Column('resource_richness', sa.Integer),
        sa.Column('practicality', sa.Integer),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('is_featured', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True)),
        sa.Column('updated_by', UUID(as_uuid=True)),
        sa.Column('is_deleted', sa.Boolean, default=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('metadata', JSON)
    )
    
    # Course tags association table
    op.create_table(
        'course_tags',
        sa.Column('course_id', UUID(as_uuid=True), sa.ForeignKey('courses.id'), primary_key=True),
        sa.Column('tag_id', UUID(as_uuid=True), sa.ForeignKey('tags.id'), primary_key=True)
    )
    
    # Course collaborators association table
    op.create_table(
        'course_collaborators',
        sa.Column('course_id', UUID(as_uuid=True), sa.ForeignKey('courses.id'), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('role', sa.String(50), default='collaborator'),
        sa.Column('permissions', JSON, default=sa.text("'{}'::json"))
    )
    
    # Create indexes for better performance
    op.create_index('idx_courses_subject', 'courses', ['subject'])
    op.create_index('idx_courses_education_level', 'courses', ['education_level'])
    op.create_index('idx_courses_status', 'courses', ['status'])
    op.create_index('idx_courses_is_public', 'courses', ['is_public'])
    op.create_index('idx_courses_quality_score', 'courses', ['quality_score'])
    op.create_index('idx_courses_created_at', 'courses', ['created_at'])
    
    op.create_index('idx_lessons_course_id', 'lessons', ['course_id'])
    op.create_index('idx_lessons_sequence_number', 'lessons', ['sequence_number'])
    
    op.create_index('idx_assessments_course_id', 'assessments', ['course_id'])
    op.create_index('idx_assessments_type', 'assessments', ['type'])
    
    op.create_index('idx_resources_course_id', 'resources', ['course_id'])
    op.create_index('idx_resources_type', 'resources', ['type'])
    
    op.create_index('idx_course_templates_category', 'course_templates', ['category'])
    op.create_index('idx_course_templates_use_count', 'course_templates', ['use_count'])
    op.create_index('idx_course_templates_rating', 'course_templates', ['rating'])
    
    op.create_index('idx_course_exports_course_id', 'course_exports', ['course_id'])
    op.create_index('idx_course_exports_status', 'course_exports', ['status'])
    op.create_index('idx_course_exports_format', 'course_exports', ['format'])
    
    op.create_index('idx_course_reviews_course_id', 'course_reviews', ['course_id'])
    op.create_index('idx_course_reviews_rating', 'course_reviews', ['rating'])


def downgrade():
    """Drop course system tables"""
    
    # Drop indexes
    op.drop_index('idx_course_reviews_rating')
    op.drop_index('idx_course_reviews_course_id')
    op.drop_index('idx_course_exports_format')
    op.drop_index('idx_course_exports_status')
    op.drop_index('idx_course_exports_course_id')
    op.drop_index('idx_course_templates_rating')
    op.drop_index('idx_course_templates_use_count')
    op.drop_index('idx_course_templates_category')
    op.drop_index('idx_resources_type')
    op.drop_index('idx_resources_course_id')
    op.drop_index('idx_assessments_type')
    op.drop_index('idx_assessments_course_id')
    op.drop_index('idx_lessons_sequence_number')
    op.drop_index('idx_lessons_course_id')
    op.drop_index('idx_courses_created_at')
    op.drop_index('idx_courses_quality_score')
    op.drop_index('idx_courses_is_public')
    op.drop_index('idx_courses_status')
    op.drop_index('idx_courses_education_level')
    op.drop_index('idx_courses_subject')
    
    # Drop tables
    op.drop_table('course_collaborators')
    op.drop_table('course_tags')
    op.drop_table('course_reviews')
    op.drop_table('course_exports')
    op.drop_table('course_templates')
    op.drop_table('resources')
    op.drop_table('assessments')
    op.drop_table('lessons')
    op.drop_table('courses')
    op.drop_table('tags')