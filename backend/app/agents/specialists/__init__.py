"""Specialized agents for PBL course design"""

from .education_theorist import EducationTheoristAgent
from .course_architect import CourseArchitectAgent
from .content_designer import ContentDesignerAgent
from .assessment_expert import AssessmentExpertAgent
from .material_creator import MaterialCreatorAgent

__all__ = [
    'EducationTheoristAgent',
    'CourseArchitectAgent',
    'ContentDesignerAgent',
    'AssessmentExpertAgent',
    'MaterialCreatorAgent'
]