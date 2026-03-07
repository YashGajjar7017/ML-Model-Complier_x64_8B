"""
Manual Training System - Learn from user feedback and ratings
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class CodeFeedback:
    """User feedback on generated code"""
    generation_id: str
    rating: int  # 1-5 scale
    correctness: bool
    efficiency_rating: int  # 1-5
    readability_rating: int  # 1-5
    comments: str
    suggested_improvements: str
    timestamp: str
    user_id: str


@dataclass
class LearningMetric:
    """Metric for tracking learning progress"""
    language: str
    problem_type: str
    avg_rating: float
    success_rate: float
    improvement_count: int
    total_attempts: int


class ManualTrainingSystem:
    """
    Manual learning system that improves code generation
    through user feedback and ratings
    """
    
    def __init__(self, storage_path: str = "training_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.feedback_history = []
        self.learned_improvements = {}
        self.language_patterns = {}
        
        self._load_training_data()
    
    def _load_training_data(self):
        """Load existing training data from disk"""
        feedback_file = self.storage_path / "feedback_history.json"
        patterns_file = self.storage_path / "learned_patterns.json"
        
        if feedback_file.exists():
            with open(feedback_file, 'r') as f:
                self.feedback_history = json.load(f)
                logger.info(f"Loaded {len(self.feedback_history)} feedback records")
        
        if patterns_file.exists():
            with open(patterns_file, 'r') as f:
                self.language_patterns = json.load(f)
                logger.info(f"Loaded learned patterns for languages: {list(self.language_patterns.keys())}")
    
    def save_feedback(self, feedback: CodeFeedback) -> bool:
        """
        Save user feedback on generated code
        
        Args:
            feedback: CodeFeedback object with user ratings
            
        Returns:
            bool: True if saved successfully
        """
        try:
            feedback_dict = asdict(feedback)
            self.feedback_history.append(feedback_dict)
            
            # Persist to disk
            self._save_feedback_to_disk()
            
            logger.info(f"Saved feedback for generation {feedback.generation_id}, rating: {feedback.rating}/5")
            return True
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            return False
    
    def _save_feedback_to_disk(self):
        """Persist feedback to JSON file"""
        feedback_file = self.storage_path / "feedback_history.json"
        with open(feedback_file, 'w') as f:
            json.dump(self.feedback_history, f, indent=2)
    
    def learn_from_feedback(self, generation_id: str, feedback: CodeFeedback) -> Dict:
        """
        Extract learning from user feedback
        
        Args:
            generation_id: ID of generated code
            feedback: User feedback
            
        Returns:
            Dict with extracted insights
        """
        insights = {
            'generation_id': generation_id,
            'rating': feedback.rating,
            'key_improvements': [],
            'anti_patterns': [],
            'best_practices_identified': []
        }
        
        # Low ratings trigger pattern analysis
        if feedback.rating <= 2:
            insights['anti_patterns'] = self._identify_anti_patterns(feedback)
        
        # High ratings confirm best practices
        if feedback.rating >= 4:
            insights['best_practices_identified'] = self._extract_best_practices(feedback)
        
        # Suggested improvements become training data
        if feedback.suggested_improvements:
            insights['key_improvements'] = feedback.suggested_improvements.split(';')
        
        logger.info(f"Extracted insights from feedback: {insights}")
        self.learned_improvements[generation_id] = insights
        
        return insights
    
    def _identify_anti_patterns(self, feedback: CodeFeedback) -> List[str]:
        """Identify patterns that caused low ratings"""
        anti_patterns = []
        
        if feedback.efficiency_rating <= 2:
            anti_patterns.append("Inefficient algorithm used")
        if feedback.readability_rating <= 2:
            anti_patterns.append("Poor code readability and structure")
        if not feedback.correctness:
            anti_patterns.append("Code produces incorrect results")
        
        return anti_patterns
    
    def _extract_best_practices(self, feedback: CodeFeedback) -> List[str]:
        """Extract best practices from high-rated feedback"""
        practices = []
        
        if feedback.efficiency_rating >= 4:
            practices.append("Efficient algorithm implementation")
        if feedback.readability_rating >= 4:
            practices.append("Clean, well-structured code")
        if feedback.correctness:
            practices.append("Correct solution producing expected output")
        
        return practices
    
    def get_learning_metrics(self, language: Optional[str] = None) -> Dict[str, LearningMetric]:
        """
        Calculate learning metrics for a language
        
        Args:
            language: Target language (if None, return all)
            
        Returns:
            Dict of learning metrics
        """
        metrics = {}
        
        # Group feedback by language and problem type
        feedback_groups = {}
        
        for feedback in self.feedback_history:
            lang = feedback.get('language', 'unknown')
            problem_type = feedback.get('problem_type', 'general')
            
            if language and lang != language:
                continue
            
            key = f"{lang}_{problem_type}"
            if key not in feedback_groups:
                feedback_groups[key] = []
            
            feedback_groups[key].append(feedback)
        
        # Calculate metrics
        for key, feedbacks in feedback_groups.items():
            lang, problem_type = key.split('_', 1)
            
            ratings = [f.get('rating', 0) for f in feedbacks]
            correct = sum(1 for f in feedbacks if f.get('correctness', False))
            
            metric = LearningMetric(
                language=lang,
                problem_type=problem_type,
                avg_rating=sum(ratings) / len(ratings) if ratings else 0,
                success_rate=correct / len(feedbacks) if feedbacks else 0,
                improvement_count=sum(1 for f in feedbacks if f.get('rating', 0) >= 4),
                total_attempts=len(feedbacks)
            )
            
            metrics[key] = metric
        
        return metrics
    
    def update_language_patterns(self, language: str, pattern_name: str, pattern_data: Dict):
        """
        Update learned patterns for a language based on feedback
        
        Args:
            language: Programming language
            pattern_name: Name of the pattern
            pattern_data: Pattern implementation data
        """
        if language not in self.language_patterns:
            self.language_patterns[language] = {}
        
        self.language_patterns[language][pattern_name] = pattern_data
        self._save_patterns_to_disk()
        
        logger.info(f"Updated pattern '{pattern_name}' for {language}")
    
    def _save_patterns_to_disk(self):
        """Persist learned patterns to disk"""
        patterns_file = self.storage_path / "learned_patterns.json"
        with open(patterns_file, 'w') as f:
            json.dump(self.language_patterns, f, indent=2)
    
    def get_improvement_recommendations(self, generation_id: str) -> List[str]:
        """
        Get recommendations for improving future generations
        
        Args:
            generation_id: ID of generation to analyze
            
        Returns:
            List of improvement recommendations
        """
        insights = self.learned_improvements.get(generation_id, {})
        recommendations = []
        
        if insights.get('anti_patterns'):
            recommendations.append(f"Avoid: {', '.join(insights['anti_patterns'])}")
        
        if insights.get('key_improvements'):
            recommendations.append(f"Improvements needed: {', '.join(insights['key_improvements'][:3])}")
        
        if insights.get('best_practices_identified'):
            recommendations.append(f"Continue using: {', '.join(insights['best_practices_identified'])}")
        
        return recommendations
    
    def generate_training_report(self) -> Dict:
        """Generate comprehensive training report"""
        metrics = self.get_learning_metrics()
        
        report = {
            'total_feedback_records': len(self.feedback_history),
            'total_languages_trained': len(set(f.get('language', 'unknown') for f in self.feedback_history)),
            'avg_rating_overall': sum(f.get('rating', 0) for f in self.feedback_history) / len(self.feedback_history) if self.feedback_history else 0,
            'metrics_by_language': {k: asdict(v) for k, v in metrics.items()},
            'learned_patterns_count': sum(len(v) for v in self.language_patterns.values()),
            'timestamp': datetime.now().isoformat()
        }
        
        return report


def create_feedback_from_dict(data: Dict) -> CodeFeedback:
    """Create CodeFeedback from dictionary"""
    return CodeFeedback(
        generation_id=data.get('generation_id'),
        rating=data.get('rating', 0),
        correctness=data.get('correctness', False),
        efficiency_rating=data.get('efficiency_rating', 0),
        readability_rating=data.get('readability_rating', 0),
        comments=data.get('comments', ''),
        suggested_improvements=data.get('suggested_improvements', ''),
        timestamp=data.get('timestamp', datetime.now().isoformat()),
        user_id=data.get('user_id', 'anonymous')
    )
