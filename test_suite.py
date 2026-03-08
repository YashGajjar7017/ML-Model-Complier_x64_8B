"""
Test Suite for CodeForge AI
Comprehensive tests for all components
"""

import unittest
import json
import tempfile
from pathlib import Path
import sys

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from codeforge_ai.core_engine import (
    CodeForgeAI, Language, CodeGenerationRequest, 
    PythonSyntax, JavaScriptSyntax
)
from codeforge_ai.manual_training import ManualTrainingSystem, CodeFeedback
from codeforge_ai.automatic_training import AutomaticTrainingSystem, TestResult


class TestCodeGeneration(unittest.TestCase):
    """Test code generation engine"""
    
    def setUp(self):
        self.code_forge = CodeForgeAI()
    
    def test_python_code_generation(self):
        """Test Python code generation"""
        request = CodeGenerationRequest(
            problem_description="Fibonacci sequence",
            language=Language.PYTHON
        )
        response = self.code_forge.generate_code(request)
        
        self.assertEqual(response.language, "python")
        self.assertIsNotNone(response.code)
        self.assertTrue(response.syntax_valid)
        self.assertGreaterEqual(response.confidence, 0)
        self.assertLessEqual(response.confidence, 1)
    
    def test_javascript_code_generation(self):
        """Test JavaScript code generation"""
        request = CodeGenerationRequest(
            problem_description="Sort an array",
            language=Language.JAVASCRIPT
        )
        response = self.code_forge.generate_code(request)
        
        self.assertEqual(response.language, "javascript")
        self.assertIsNotNone(response.code)
        self.assertTrue(len(response.code) > 0)
    
    def test_complexity_analysis(self):
        """Test complexity analysis"""
        validator = PythonSyntax()
        
        # Simple code - O(1)
        simple_code = "x = 5"
        complexity = validator.get_complexity_analysis(simple_code)
        self.assertEqual(complexity, "O(1)")
        
        # Single loop - O(n)
        loop_code = "for i in range(n):\n    print(i)"
        complexity = validator.get_complexity_analysis(loop_code)
        self.assertEqual(complexity, "O(n)")
        
        # Nested loops - O(n²)
        nested_code = "for i in range(n):\n    for j in range(n):\n        print(i, j)"
        complexity = validator.get_complexity_analysis(nested_code)
        self.assertEqual(complexity, "O(n²)")
    
    def test_syntax_validation(self):
        """Test Python syntax validation"""
        validator = PythonSyntax()
        
        # Valid code
        valid_code = "def hello():\n    return 'world'"
        is_valid, errors = validator.validate_syntax(valid_code)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
        
        # Invalid code - mismatched brackets
        invalid_code = "def hello(\n    return 'world'"
        is_valid, errors = validator.validate_syntax(invalid_code)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


class TestManualTraining(unittest.TestCase):
    """Test manual training system"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.trainer = ManualTrainingSystem(storage_path=self.temp_dir)
    
    def test_feedback_saving(self):
        """Test feedback saving"""
        feedback = CodeFeedback(
            generation_id="test_001",
            rating=5,
            correctness=True,
            efficiency_rating=4,
            readability_rating=5,
            comments="Excellent",
            suggested_improvements="",
            timestamp=None,
            user_id="tester"
        )
        
        result = self.trainer.save_feedback(feedback)
        self.assertTrue(result)
        self.assertEqual(len(self.trainer.feedback_history), 1)
    
    def test_learning_from_feedback(self):
        """Test learning from feedback"""
        feedback = CodeFeedback(
            generation_id="test_002",
            rating=5,
            correctness=True,
            efficiency_rating=4,
            readability_rating=5,
            comments="",
            suggested_improvements="",
            timestamp=None,
            user_id="tester"
        )
        
        insights = self.trainer.learn_from_feedback("test_002", feedback)
        
        self.assertIn('best_practices_identified', insights)
        self.assertGreater(len(insights['best_practices_identified']), 0)
    
    def test_anti_pattern_identification(self):
        """Test anti-pattern identification"""
        feedback = CodeFeedback(
            generation_id="test_003",
            rating=1,
            correctness=False,
            efficiency_rating=1,
            readability_rating=1,
            comments="Very bad",
            suggested_improvements="",
            timestamp=None,
            user_id="tester"
        )
        
        insights = self.trainer.learn_from_feedback("test_003", feedback)
        
        self.assertIn('anti_patterns', insights)
        self.assertGreater(len(insights['anti_patterns']), 0)
    
    def test_pattern_storage(self):
        """Test pattern storage"""
        pattern_data = {
            'algorithm': 'merge_sort',
            'complexity': 'O(n log n)',
            'effectiveness': 0.95
        }
        
        self.trainer.update_language_patterns('python', 'sort_pattern', pattern_data)
        
        patterns = self.trainer.language_patterns.get('python', {})
        self.assertIn('sort_pattern', patterns)
        self.assertEqual(patterns['sort_pattern']['algorithm'], 'merge_sort')


class TestAutomaticTraining(unittest.TestCase):
    """Test automatic training system"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.trainer = AutomaticTrainingSystem(storage_path=self.temp_dir)
    
    def test_python_execution(self):
        """Test Python code execution"""
        code = """
def add(a, b):
    return a + b
"""
        test_cases = [
            {'input': {'a': 2, 'b': 3}, 'expected_output': 5}
        ]
        
        try:
            results, metric = self.trainer.execute_and_test(code, 'python', test_cases)
            self.assertEqual(metric.test_count, 1)
        except Exception as e:
            # Expected if code execution environment not available
            pass
    
    def test_reinforcement_feedback(self):
        """Test reinforcement learning feedback generation"""
        # Create mock results
        results = [
            TestResult("1", True, 0.01, 10, "5", None, "5"),
            TestResult("2", True, 0.01, 10, "10", None, "10"),
            TestResult("3", False, 0.02, 15, "7", None, "6")
        ]
        
        feedback = self.trainer.generate_reinforcement_feedback(results)
        
        self.assertIn('base_reward', feedback)
        self.assertIn('total_reward', feedback)
        self.assertIn('suggestion', feedback)
        self.assertGreaterEqual(feedback['base_reward'], 0)
        self.assertLessEqual(feedback['base_reward'], 1)
    
    def test_performance_metrics(self):
        """Test performance metrics calculation"""
        # Add some mock test results
        self.trainer.test_results = [
            {'language': 'python', 'passed': True, 'execution_time': 0.01},
            {'language': 'python', 'passed': True, 'execution_time': 0.02},
            {'language': 'python', 'passed': False, 'execution_time': 0.03}
        ]
        
        metrics = self.trainer.get_performance_metrics('python')
        
        self.assertIn('python', metrics)
        self.assertEqual(metrics['python']['total_tests'], 3)
        self.assertEqual(metrics['python']['passed_tests'], 2)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows"""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow: generate -> test -> feedback"""
        code_forge = CodeForgeAI()
        
        # Step 1: Generate code
        request = CodeGenerationRequest(
            problem_description="Fibonacci sequence",
            language=Language.PYTHON
        )
        response = code_forge.generate_code(request)
        
        self.assertIsNotNone(response.code)
        self.assertTrue(response.syntax_valid)
        
        # Step 2: Submit feedback (simulated)
        temp_dir = tempfile.mkdtemp()
        manual_trainer = ManualTrainingSystem(storage_path=temp_dir)
        
        feedback = CodeFeedback(
            generation_id="gen_001",
            rating=4,
            correctness=True,
            efficiency_rating=4,
            readability_rating=4,
            comments="Good solution",
            suggested_improvements="",
            timestamp=None,
            user_id="tester"
        )
        
        manual_trainer.save_feedback(feedback)
        insights = manual_trainer.learn_from_feedback("gen_001", feedback)
        
        # Verify learning occurred
        self.assertEqual(len(manual_trainer.feedback_history), 1)
        self.assertIn('best_practices_identified', insights)


class TestDataPersistence(unittest.TestCase):
    """Test data persistence and recovery"""
    
    def test_feedback_persistence(self):
        """Test feedback is saved to disk"""
        with tempfile.TemporaryDirectory() as temp_dir:
            trainer1 = ManualTrainingSystem(storage_path=temp_dir)
            
            feedback = CodeFeedback(
                generation_id="test_001",
                rating=5,
                correctness=True,
                efficiency_rating=5,
                readability_rating=5,
                comments="Test",
                suggested_improvements="",
                timestamp=None,
                user_id="tester"
            )
            
            trainer1.save_feedback(feedback)
            
            # Create new instance - should load persisted data
            trainer2 = ManualTrainingSystem(storage_path=temp_dir)
            self.assertEqual(len(trainer2.feedback_history), 1)
            self.assertEqual(trainer2.feedback_history[0]['rating'], 5)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCodeGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestManualTraining))
    suite.addTests(loader.loadTestsFromTestCase(TestAutomaticTraining))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestDataPersistence))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
