"""
CodeForge AI - Multi-Language Code Generation with Reinforcement Learning
Version 1.0.0
"""

from .core_engine import (
    CodeForgeAI,
    Language,
    CodeGenerationRequest,
    CodeGenerationResponse,
    format_json_response
)

from .manual_training import (
    ManualTrainingSystem,
    CodeFeedback,
    LearningMetric
)

from .automatic_training import (
    AutomaticTrainingSystem,
    TestResult,
    ExecutionMetric
)

__version__ = "1.0.0"
__author__ = "CodeForge Team"
__all__ = [
    'CodeForgeAI',
    'Language',
    'CodeGenerationRequest',
    'CodeGenerationResponse',
    'format_json_response',
    'ManualTrainingSystem',
    'CodeFeedback',
    'LearningMetric',
    'AutomaticTrainingSystem',
    'TestResult',
    'ExecutionMetric'
]
