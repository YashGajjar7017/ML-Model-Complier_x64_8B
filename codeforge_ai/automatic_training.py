"""
Automatic Training System - Learn through test execution and metrics
"""

import json
import logging
import subprocess
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result of executing generated code against test cases"""
    test_id: str
    passed: bool
    execution_time: float
    memory_usage: float
    output: str
    error: Optional[str]
    expected_output: str


@dataclass
class ExecutionMetric:
    """Metric collected during code execution"""
    language: str
    test_count: int
    pass_rate: float
    avg_execution_time: float
    correctness_score: float
    optimization_score: float


class AutomaticTrainingSystem:
    """
    Automatic learning system that improves code generation
    through test execution, metrics analysis, and reinforcement learning
    """
    
    def __init__(self, storage_path: str = "training_data", models_path: str = "models"):
        self.storage_path = Path(storage_path)
        self.models_path = Path(models_path)
        
        self.storage_path.mkdir(exist_ok=True)
        self.models_path.mkdir(exist_ok=True)
        
        self.test_results = []
        self.execution_metrics = {}
        self.learned_optimizations = {}
        self.performance_history = []
        
        self._load_training_data()
    
    def _load_training_data(self):
        """Load existing training data from disk"""
        results_file = self.storage_path / "test_results.json"
        metrics_file = self.storage_path / "execution_metrics.json"
        
        if results_file.exists():
            with open(results_file, 'r') as f:
                self.test_results = json.load(f)
                logger.info(f"Loaded {len(self.test_results)} test results")
        
        if metrics_file.exists():
            with open(metrics_file, 'r') as f:
                self.execution_metrics = json.load(f)
    
    def execute_and_test(self, code: str, language: str, test_cases: List[Dict]) -> Tuple[List[TestResult], ExecutionMetric]:
        """
        Execute generated code against test cases
        
        Args:
            code: Generated code to test
            language: Programming language
            test_cases: List of test cases with input/expected output
            
        Returns:
            Tuple of (test results, execution metrics)
        """
        results = []
        execution_times = []
        passed_count = 0
        
        logger.info(f"Executing {language} code against {len(test_cases)} test cases")
        
        for i, test_case in enumerate(test_cases):
            result = self._run_single_test(code, language, test_case, i)
            results.append(result)
            
            if result.passed:
                passed_count += 1
            execution_times.append(result.execution_time)
        
        # Calculate metrics
        metric = ExecutionMetric(
            language=language,
            test_count=len(test_cases),
            pass_rate=passed_count / len(test_cases) if test_cases else 0,
            avg_execution_time=sum(execution_times) / len(execution_times) if execution_times else 0,
            correctness_score=passed_count / len(test_cases) if test_cases else 0,
            optimization_score=self._calculate_optimization_score(code, execution_times)
        )
        
        # Store results
        for result in results:
            self.test_results.append(asdict(result))
        
        self._save_results_to_disk()
        
        logger.info(f"Test results: {passed_count}/{len(test_cases)} passed, "
                   f"avg time: {metric.avg_execution_time:.3f}s")
        
        return results, metric
    
    def _run_single_test(self, code: str, language: str, test_case: Dict, test_id: int) -> TestResult:
        """
        Execute a single test case
        
        Args:
            code: Code to execute
            language: Language
            test_case: Test case with input/expected output
            test_id: Test identifier
            
        Returns:
            TestResult with execution details
        """
        try:
            start_time = time.time()
            
            if language == "python":
                output = self._execute_python(code, test_case)
            elif language == "javascript":
                output = self._execute_javascript(code, test_case)
            else:
                output = f"Language {language} not supported for execution"
            
            execution_time = time.time() - start_time
            expected = test_case.get('expected_output', '')
            passed = str(output).strip() == str(expected).strip()
            
            return TestResult(
                test_id=f"{test_id}",
                passed=passed,
                execution_time=execution_time,
                memory_usage=0.0,  # Would use psutil for actual measurement
                output=str(output),
                error=None,
                expected_output=str(expected)
            )
        
        except Exception as e:
            logger.error(f"Test {test_id} failed with error: {e}")
            return TestResult(
                test_id=f"{test_id}",
                passed=False,
                execution_time=0.0,
                memory_usage=0.0,
                output="",
                error=str(e),
                expected_output=test_case.get('expected_output', '')
            )
    
    def _execute_python(self, code: str, test_case: Dict) -> str:
        """Execute Python code safely"""
        try:
            # Create a temporary module
            local_scope = {}
            exec(code, local_scope)
            
            # Get input and call main function if exists
            test_input = test_case.get('input', None)
            
            # Find the main function
            main_func = None
            for name, obj in local_scope.items():
                if callable(obj) and not name.startswith('_'):
                    main_func = obj
                    break
            
            if main_func:
                if test_input is not None:
                    result = main_func(test_input)
                else:
                    result = main_func()
            else:
                result = "No executable function found"
            
            return result
        
        except Exception as e:
            raise RuntimeError(f"Python execution error: {e}")
    
    def _execute_javascript(self, code: str, test_case: Dict) -> str:
        """Execute JavaScript code safely (requires Node.js)"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                f.write("\n")
                f.write(f"console.log(solution({json.dumps(test_case.get('input'))}));")
                temp_file = f.name
            
            result = subprocess.run(
                ['node', temp_file],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            Path(temp_file).unlink()  # Clean up
            
            if result.returncode != 0:
                raise RuntimeError(result.stderr)
            
            return result.stdout.strip()
        
        except Exception as e:
            raise RuntimeError(f"JavaScript execution error: {e}")
    
    def _calculate_optimization_score(self, code: str, execution_times: List[float]) -> float:
        """
        Calculate optimization score based on execution metrics
        
        Args:
            code: Code to analyze
            execution_times: List of execution times
            
        Returns:
            Score from 0-1
        """
        # Base score
        score = 0.5
        
        # Faster execution
        if execution_times and sum(execution_times) / len(execution_times) < 0.1:
            score += 0.3
        
        # Code length efficiency (shorter is often better)
        if len(code) < 1000:
            score += 0.2
        
        return min(1.0, score)
    
    def _save_results_to_disk(self):
        """Persist test results to disk"""
        results_file = self.storage_path / "test_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
    
    def learn_from_execution(self, metric: ExecutionMetric, code: str) -> Dict:
        """
        Extract learning insights from execution metrics
        
        Args:
            metric: ExecutionMetric from test execution
            code: The code that was executed
            
        Returns:
            Dict with learning insights
        """
        insights = {
            'timestamp': datetime.now().isoformat(),
            'language': metric.language,
            'pass_rate': metric.pass_rate,
            'optimization_opportunities': [],
            'patterns_identified': [],
            'performance_feedback': ''
        }
        
        # Identify optimization opportunities
        if metric.avg_execution_time > 1.0:
            insights['optimization_opportunities'].append("Code execution is slow, consider optimization")
        
        if metric.pass_rate < 1.0:
            insights['optimization_opportunities'].append(f"Code fails {(1 - metric.pass_rate) * 100:.1f}% of tests")
        
        # Identify patterns that work well
        if metric.pass_rate >= 0.9:
            insights['patterns_identified'].append("High test pass rate - pattern is effective")
        
        if metric.optimization_score >= 0.8:
            insights['patterns_identified'].append("Efficient code structure - continue using this pattern")
        
        # Performance feedback
        if metric.correctness_score == 1.0:
            insights['performance_feedback'] = "Perfect correctness achieved"
        elif metric.correctness_score >= 0.8:
            insights['performance_feedback'] = "Good correctness with room for improvement"
        else:
            insights['performance_feedback'] = "Significant correctness issues detected"
        
        logger.info(f"Learning insights: {insights}")
        return insights
    
    def get_performance_metrics(self, language: Optional[str] = None) -> Dict:
        """
        Get aggregated performance metrics
        
        Args:
            language: Target language (if None, return all)
            
        Returns:
            Dict of performance metrics by language
        """
        metrics = {}
        
        for result in self.test_results:
            lang = result.get('language', 'unknown')
            
            if language and lang != language:
                continue
            
            if lang not in metrics:
                metrics[lang] = {
                    'total_tests': 0,
                    'passed_tests': 0,
                    'total_time': 0.0,
                    'test_results': []
                }
            
            metrics[lang]['total_tests'] += 1
            if result.get('passed'):
                metrics[lang]['passed_tests'] += 1
            metrics[lang]['total_time'] += result.get('execution_time', 0)
            metrics[lang]['test_results'].append(result)
        
        # Calculate aggregates
        for lang, data in metrics.items():
            total = data['total_tests']
            data['pass_rate'] = data['passed_tests'] / total if total > 0 else 0
            data['avg_execution_time'] = data['total_time'] / total if total > 0 else 0
        
        return metrics
    
    def generate_reinforcement_feedback(self, results: List[TestResult]) -> Dict:
        """
        Generate reinforcement learning feedback signal
        
        Args:
            results: List of test results
            
        Returns:
            Reinforcement signal (reward/penalty)
        """
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        
        # Reward: higher for better performance
        reward = (passed / total) if total > 0 else 0
        
        # Speed bonus
        avg_time = sum(r.execution_time for r in results) / len(results) if results else 0
        if avg_time < 0.1:
            reward += 0.1
        elif avg_time > 1.0:
            reward -= 0.1
        
        feedback = {
            'base_reward': passed / total if total > 0 else 0,
            'speed_bonus': 0.1 if avg_time < 0.1 else (-0.1 if avg_time > 1.0 else 0),
            'total_reward': min(1.0, max(-1.0, reward)),
            'feedback_type': 'positive' if reward > 0.5 else 'negative',
            'suggestion': self._generate_suggestion(results)
        }
        
        return feedback
    
    def _generate_suggestion(self, results: List[TestResult]) -> str:
        """Generate suggestion based on test results"""
        failed = [r for r in results if not r.passed]
        
        if not failed:
            return "Excellent performance! Code passes all tests."
        
        if len(failed) / len(results) > 0.5:
            return "Major correctness issues. Review algorithm logic."
        
        return f"Minor issues found in {len(failed)} test(s). Debug and retest."
    
    def generate_automatic_training_report(self) -> Dict:
        """Generate comprehensive automatic training report"""
        metrics = self.get_performance_metrics()
        
        report = {
            'total_executions': len(self.test_results),
            'execution_by_language': metrics,
            'overall_pass_rate': sum(m['passed_tests'] for m in metrics.values()) / sum(m['total_tests'] for m in metrics.values()) if metrics else 0,
            'avg_execution_time': sum(m['avg_execution_time'] for m in metrics.values()) / len(metrics) if metrics else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        return report


import json
