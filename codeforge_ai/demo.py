"""
Demo and testing script for CodeForge AI
Shows how to use the system for both manual and automatic training
"""

import json
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from codeforge_ai.core_engine import (
    CodeForgeAI, Language, CodeGenerationRequest, 
    PythonSyntax, format_json_response
)
from codeforge_ai.manual_training import ManualTrainingSystem, CodeFeedback
from codeforge_ai.automatic_training import AutomaticTrainingSystem


def demo_code_generation():
    """Demonstrate code generation capabilities"""
    print("\n" + "="*70)
    print("DEMO 1: CODE GENERATION")
    print("="*70)
    
    code_forge = CodeForgeAI()
    
    # Example 1: Python Fibonacci
    print("\n[1] Generating Python Fibonacci solution...")
    request1 = CodeGenerationRequest(
        problem_description="Generate a function to compute the Fibonacci sequence",
        language=Language.PYTHON,
        constraints={'max_n': 100}
    )
    
    response1 = code_forge.generate_code(request1)
    print(f"Language: {response1.language}")
    print(f"Confidence: {response1.confidence:.2f}")
    print(f"Syntax Valid: {response1.syntax_valid}")
    print(f"Complexity: {response1.complexity}")
    print(f"\nGenerated Code:\n{response1.code}")
    
    # Example 2: JavaScript sorting
    print("\n[2] Generating JavaScript sorting solution...")
    request2 = CodeGenerationRequest(
        problem_description="Implement an efficient sorting algorithm",
        language=Language.JAVASCRIPT
    )
    
    response2 = code_forge.generate_code(request2)
    print(f"Language: {response2.language}")
    print(f"Confidence: {response2.confidence:.2f}")
    print(f"Complexity: {response2.complexity}")
    print(f"\nGenerated Code:\n{response2.code}")
    
    return response1, response2


def demo_automatic_training(python_code):
    """Demonstrate automatic training through test execution"""
    print("\n" + "="*70)
    print("DEMO 2: AUTOMATIC TRAINING (Test Execution & Metrics)")
    print("="*70)
    
    auto_trainer = AutomaticTrainingSystem()
    
    # Create test cases for Fibonacci
    test_cases = [
        {'input': 0, 'expected_output': []},
        {'input': 1, 'expected_output': [0]},
        {'input': 5, 'expected_output': [0, 1, 1, 2, 3]},
        {'input': 7, 'expected_output': [0, 1, 1, 2, 3, 5, 8]},
    ]
    
    print(f"\nTesting {len(test_cases)} test cases...")
    
    try:
        results, metric = auto_trainer.execute_and_test(
            python_code, 
            'python',
            test_cases
        )
        
        # Display test results
        print(f"\nTest Results:")
        print(f"  Pass Rate: {metric.pass_rate*100:.1f}%")
        print(f"  Avg Execution Time: {metric.avg_execution_time:.4f}s")
        print(f"  Correctness Score: {metric.correctness_score:.2f}")
        print(f"  Optimization Score: {metric.optimization_score:.2f}")
        
        # Show individual results
        print(f"\nDetailed Results:")
        for i, result in enumerate(results):
            status = "✓ PASS" if result.passed else "✗ FAIL"
            print(f"  Test {i+1}: {status} | Time: {result.execution_time:.4f}s")
            if not result.passed:
                print(f"    Expected: {result.expected_output}")
                print(f"    Got: {result.output}")
        
        # Learning insights
        insights = auto_trainer.learn_from_execution(metric, python_code)
        print(f"\nLearning Insights:")
        for opportunity in insights.get('optimization_opportunities', []):
            print(f"  • {opportunity}")
        for pattern in insights.get('patterns_identified', []):
            print(f"  ✓ {pattern}")
        
        # Reinforcement feedback
        feedback = auto_trainer.generate_reinforcement_feedback(results)
        print(f"\nReinforcement Feedback:")
        print(f"  Base Reward: {feedback['base_reward']:.2f}")
        print(f"  Speed Bonus: {feedback['speed_bonus']:+.2f}")
        print(f"  Total Reward: {feedback['total_reward']:.2f}")
        print(f"  Feedback Type: {feedback['feedback_type']}")
        print(f"  Suggestion: {feedback['suggestion']}")
        
        # Generate automatic report
        print(f"\nAutomatic Training Report:")
        report = auto_trainer.generate_automatic_training_report()
        print(f"  Total Executions: {report['total_executions']}")
        print(f"  Overall Pass Rate: {report['overall_pass_rate']:.2f}")
        
    except Exception as e:
        print(f"Note: Automatic testing requires proper code execution environment")
        print(f"Error: {e}")


def demo_manual_training(generation_id, response):
    """Demonstrate manual training through user feedback"""
    print("\n" + "="*70)
    print("DEMO 3: MANUAL TRAINING (User Feedback & Learning)")
    print("="*70)
    
    manual_trainer = ManualTrainingSystem()
    
    # Simulate user feedback on generated code
    feedback_data = {
        'generation_id': generation_id,
        'rating': 5,  # 5/5 - excellent
        'correctness': True,
        'efficiency_rating': 4,
        'readability_rating': 5,
        'comments': 'Very clean and efficient implementation',
        'suggested_improvements': 'Could add type hints; Could add docstring examples',
        'language': 'python',
        'problem_type': 'algorithm_design',
        'user_id': 'expert_reviewer'
    }
    
    print(f"\nSubmitting feedback for generation: {generation_id}")
    print(f"Rating: {feedback_data['rating']}/5 stars")
    
    # Create and save feedback
    feedback = CodeFeedback(
        generation_id=feedback_data['generation_id'],
        rating=feedback_data['rating'],
        correctness=feedback_data['correctness'],
        efficiency_rating=feedback_data['efficiency_rating'],
        readability_rating=feedback_data['readability_rating'],
        comments=feedback_data['comments'],
        suggested_improvements=feedback_data['suggested_improvements'],
        timestamp=feedback_data.get('timestamp'),
        user_id=feedback_data['user_id']
    )
    
    manual_trainer.save_feedback(feedback)
    print("✓ Feedback saved successfully")
    
    # Learn from feedback
    insights = manual_trainer.learn_from_feedback(generation_id, feedback)
    print(f"\nLearning Insights:")
    print(f"  Rating: {insights['rating']}/5")
    if insights.get('best_practices_identified'):
        print(f"  Best Practices Identified:")
        for practice in insights['best_practices_identified']:
            print(f"    ✓ {practice}")
    
    # Get recommendations
    recommendations = manual_trainer.get_improvement_recommendations(generation_id)
    print(f"\nImprovement Recommendations:")
    for rec in recommendations:
        print(f"  • {rec}")
    
    # Update language patterns
    pattern_data = {
        'algorithm': 'fibonacci',
        'approach': 'iterative',
        'time_complexity': 'O(n)',
        'space_complexity': 'O(n)',
        'user_rating': 5
    }
    manual_trainer.update_language_patterns('python', 'fibonacci_pattern', pattern_data)
    print("\n✓ Pattern stored for future learning")
    
    # Get learning metrics
    metrics = manual_trainer.get_learning_metrics()
    print(f"\nLearning Metrics:")
    for key, metric in metrics.items():
        print(f"  [{key}]")
        print(f"    Average Rating: {metric.avg_rating:.2f}")
        print(f"    Success Rate: {metric.success_rate*100:.1f}%")
        print(f"    Total Attempts: {metric.total_attempts}")
    
    # Generate comprehensive report
    print(f"\nManual Training Report:")
    report = manual_trainer.generate_training_report()
    print(f"  Total Feedback Records: {report['total_feedback_records']}")
    print(f"  Languages Trained: {report['total_languages_trained']}")
    print(f"  Overall Average Rating: {report['avg_rating_overall']:.2f}")
    print(f"  Learned Patterns: {report['learned_patterns_count']}")


def demo_end_to_end_workflow():
    """Demonstrate complete end-to-end workflow"""
    print("\n" + "="*70)
    print("DEMO 4: END-TO-END WORKFLOW")
    print("="*70)
    
    print("\nCompleting workflow:")
    print("  1. Generate code from problem description")
    print("  2. Test code against test cases (automatic training)")
    print("  3. Collect user feedback (manual training)")
    print("  4. Learn patterns and improve future generations")
    print("  5. Generate metrics and reports")
    
    print("\n✓ Workflow demonstration completed")
    print("  Both manual and automatic training systems are integrated and learning")


def main():
    """Run all demonstrations"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*10 + "CodeForge AI - ML Compiler Training" + " "*24 + "║")
    print("║" + " "*8 + "Self-Improving Code Generation System" + " "*21 + "║")
    print("╚" + "="*68 + "╝")
    
    # Demo 1: Code Generation
    response1, response2 = demo_code_generation()
    
    # Demo 2: Automatic Training
    demo_automatic_training(response1.code)
    
    # Demo 3: Manual Training
    demo_manual_training("gen_001", response1)
    
    # Demo 4: Complete Workflow
    demo_end_to_end_workflow()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("\nCodeForge AI successfully demonstrates:")
    print("  ✓ Multi-language code generation")
    print("  ✓ Automatic training through test execution")
    print("  ✓ Manual training through user feedback")
    print("  ✓ Reinforcement learning signals")
    print("  ✓ Pattern learning and storage")
    print("  ✓ Comprehensive metrics and reporting")
    
    print("\nKey Components:")
    print("  • Core Engine: Multi-language code generation with syntax validation")
    print("  • Automatic Trainer: Test execution and metrics collection")
    print("  • Manual Trainer: User feedback and pattern learning")
    print("  • API Server: REST endpoints for all operations")
    
    print("\nNext Steps:")
    print("  1. Run API server: python codeforge_ai/api_server.py")
    print("  2. Send POST requests to /generate endpoint")
    print("  3. Submit feedback via /feedback endpoint")
    print("  4. Monitor metrics and training progress")
    
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    main()
