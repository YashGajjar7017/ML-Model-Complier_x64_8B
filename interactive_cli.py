#!/usr/bin/env python3
"""
CodeForge AI - Quick Start Script
Interactive guide to using the system
"""

import sys
import json
import time
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from codeforge_ai.core_engine import CodeForgeAI, Language, CodeGenerationRequest
from codeforge_ai.manual_training import ManualTrainingSystem, CodeFeedback
from codeforge_ai.automatic_training import AutomaticTrainingSystem


def print_menu():
    """Display main menu"""
    print("\n" + "="*60)
    print("CodeForge AI - Main Menu")
    print("="*60)
    print("1. Generate Code")
    print("2. Test Generated Code")
    print("3. Submit Feedback (Manual Training)")
    print("4. View Training Metrics")
    print("5. View Generated Reports")
    print("6. Run Complete Demo")
    print("7. Exit")
    print("="*60)


def menu_generate_code():
    """Interactive code generation"""
    print("\n--- Code Generation ---")
    
    problem = input("Enter problem description: ").strip()
    if not problem:
        print("Error: Problem description cannot be empty")
        return
    
    print("\nSupported languages:")
    for i, lang in enumerate(Language, 1):
        print(f"  {i}. {lang.value}")
    
    try:
        lang_choice = int(input("Select language (1-7): ")) - 1
        if lang_choice < 0 or lang_choice >= len(Language):
            print("Invalid selection")
            return
        
        language = list(Language)[lang_choice]
    except ValueError:
        print("Invalid input")
        return
    
    print(f"\nGenerating {language.value} code for: {problem[:50]}...")
    
    code_forge = CodeForgeAI()
    request = CodeGenerationRequest(
        problem_description=problem,
        language=language
    )
    
    response = code_forge.generate_code(request)
    
    print(f"\n✓ Code Generated!")
    print(f"Confidence: {response.confidence:.2f}")
    print(f"Complexity: {response.complexity}")
    print(f"Syntax Valid: {response.syntax_valid}")
    print(f"\nGenerated Code:\n{'-'*60}")
    print(response.code)
    print('-'*60)
    
    # Store for later use
    return response.code, language.value


def menu_test_code():
    """Interactive code testing"""
    print("\n--- Test Code ---")
    
    code = input("Enter code to test (or paste): ").strip()
    if not code:
        code_str = ""
        print("Enter code (press Ctrl+D when done):")
        try:
            while True:
                code_str += input() + "\n"
        except EOFError:
            code = code_str
    
    language = input("Language (python/javascript): ").strip().lower()
    if language not in ["python", "javascript"]:
        print("Invalid language")
        return
    
    test_input = input("Test input: ").strip()
    expected_output = input("Expected output: ").strip()
    
    test_cases = [{'input': test_input, 'expected_output': expected_output}]
    
    print(f"\nTesting {language} code...")
    
    auto_trainer = AutomaticTrainingSystem()
    
    try:
        results, metric = auto_trainer.execute_and_test(code, language, test_cases)
        
        print(f"\n✓ Test Complete!")
        print(f"Pass Rate: {metric.pass_rate*100:.1f}%")
        print(f"Execution Time: {metric.avg_execution_time:.4f}s")
        print(f"Correctness Score: {metric.correctness_score:.2f}")
        
        for result in results:
            status = "PASS" if result.passed else "FAIL"
            print(f"\nTest {result.test_id}: {status}")
            if not result.passed:
                print(f"  Expected: {result.expected_output}")
                print(f"  Got: {result.output}")
        
        feedback = auto_trainer.generate_reinforcement_feedback(results)
        print(f"\nFeedback: {feedback['suggestion']}")
    
    except Exception as e:
        print(f"Error: {e}")


def menu_submit_feedback():
    """Interactive feedback submission"""
    print("\n--- Submit Feedback ---")
    
    gen_id = input("Generation ID: ").strip()
    rating = int(input("Rating (1-5): ").strip())
    correctness = input("Correctness (y/n): ").strip().lower() == 'y'
    efficiency = int(input("Efficiency Rating (1-5): ").strip())
    readability = int(input("Readability Rating (1-5): ").strip())
    comments = input("Comments: ").strip()
    improvements = input("Suggested improvements: ").strip()
    
    manual_trainer = ManualTrainingSystem()
    
    feedback = CodeFeedback(
        generation_id=gen_id,
        rating=rating,
        correctness=correctness,
        efficiency_rating=efficiency,
        readability_rating=readability,
        comments=comments,
        suggested_improvements=improvements,
        timestamp=None,
        user_id="user"
    )
    
    manual_trainer.save_feedback(feedback)
    insights = manual_trainer.learn_from_feedback(gen_id, feedback)
    
    print(f"\n✓ Feedback Recorded!")
    print(f"Rating: {rating}/5")
    print(f"Key Insights:")
    for pattern in insights.get('best_practices_identified', []):
        print(f"  ✓ {pattern}")
    for anti in insights.get('anti_patterns', []):
        print(f"  ✗ {anti}")


def menu_view_metrics():
    """View training metrics"""
    print("\n--- Training Metrics ---")
    
    manual_trainer = ManualTrainingSystem()
    auto_trainer = AutomaticTrainingSystem()
    
    print("\nManual Training Metrics:")
    manual_metrics = manual_trainer.get_learning_metrics()
    if manual_metrics:
        for key, metric in manual_metrics.items():
            print(f"  [{key}]")
            print(f"    Avg Rating: {metric.avg_rating:.2f}")
            print(f"    Success Rate: {metric.success_rate*100:.1f}%")
    else:
        print("  No manual training data yet")
    
    print("\nAutomatic Training Metrics:")
    auto_metrics = auto_trainer.get_performance_metrics()
    if auto_metrics:
        for lang, data in auto_metrics.items():
            print(f"  [{lang}]")
            print(f"    Pass Rate: {data['pass_rate']*100:.1f}%")
            print(f"    Avg Time: {data['avg_execution_time']:.4f}s")
    else:
        print("  No automatic training data yet")


def menu_view_reports():
    """View comprehensive reports"""
    print("\n--- Training Reports ---")
    
    manual_trainer = ManualTrainingSystem()
    auto_trainer = AutomaticTrainingSystem()
    
    print("\nManual Training Report:")
    report = manual_trainer.generate_training_report()
    print(f"  Total Feedback Records: {report['total_feedback_records']}")
    print(f"  Languages Trained: {report['total_languages_trained']}")
    print(f"  Avg Rating: {report['avg_rating_overall']:.2f}")
    
    print("\nAutomatic Training Report:")
    report = auto_trainer.generate_automatic_training_report()
    print(f"  Total Executions: {report['total_executions']}")
    print(f"  Overall Pass Rate: {report['overall_pass_rate']:.2f}")


def interactive_menu():
    """Run interactive menu"""
    while True:
        print_menu()
        choice = input("Select option (1-7): ").strip()
        
        if choice == '1':
            menu_generate_code()
        elif choice == '2':
            menu_test_code()
        elif choice == '3':
            menu_submit_feedback()
        elif choice == '4':
            menu_view_metrics()
        elif choice == '5':
            menu_view_reports()
        elif choice == '6':
            print("\nLaunching complete demo...")
            import subprocess
            subprocess.run([sys.executable, "codeforge_ai/demo.py"])
        elif choice == '7':
            print("\nThank you for using CodeForge AI!")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == '__main__':
    print("\n╔" + "="*58 + "╗")
    print("║" + " "*10 + "Welcome to CodeForge AI" + " "*26 + "║")
    print("║" + " "*8 + "Self-Improving Code Generation System" + " "*13 + "║")
    print("╚" + "="*58 + "╝")
    
    interactive_menu()
