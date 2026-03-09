#!/usr/bin/env python3
"""
Simple test script for the enhanced CodeForge AI functionality
"""

from codeforge_ai.core_engine import CodeForgeAI, ModelType, Language, CodeGenerationRequest

def test_models():
    """Test different model types"""
    print("Testing CodeForge AI Enhanced Models")
    print("=" * 50)

    # Initialize the engine
    engine = CodeForgeAI()

    # Test problem
    problem = "Generate a fibonacci sequence with 10 terms"

    # Test each model type
    model_types = [
        ModelType.PATTERN_BASED,
        ModelType.TEMPLATE_BASED,
        ModelType.OPTIMIZATION_FOCUSED,
        ModelType.READABILITY_FOCUSED,
        ModelType.PERFORMANCE_FOCUSED
    ]

    for model_type in model_types:
        print(f"\n--- Testing {model_type.value} ---")

        request = CodeGenerationRequest(
            problem_description=problem,
            language=Language.PYTHON,
            model_type=model_type
        )

        try:
            response = engine.generate_code(request)
            print(f"✓ Success! Confidence: {response.confidence:.2f}")
            print(f"Complexity: {response.complexity}")
            print(f"Code length: {len(response.code)} characters")
            print("Code preview:")
            lines = response.code.split('\n')[:5]  # First 5 lines
            for line in lines:
                print(f"  {line}")
            if len(response.code.split('\n')) > 5:
                print("  ...")

        except Exception as e:
            print(f"✗ Error: {e}")

def test_data_management():
    """Test data management functionality"""
    print("\n" + "=" * 50)
    print("Testing Data Management")
    print("=" * 50)

    engine = CodeForgeAI()

    # Test statistics
    print("\n--- Data Statistics ---")
    try:
        stats = engine.get_data_statistics()
        print("✓ Statistics retrieved successfully")
        for category, cat_stats in stats.items():
            print(f"  {category}: {cat_stats['total_items']} items, {cat_stats['subcategories']} subcategories")
    except Exception as e:
        print(f"✗ Statistics error: {e}")

    # Test similar problems
    print("\n--- Similar Problems ---")
    try:
        similar = engine.get_similar_problems("sort an array", limit=3)
        print(f"✓ Found {len(similar)} similar problems")
    except Exception as e:
        print(f"✗ Similar problems error: {e}")

    # Test recommendations
    print("\n--- Recommendations ---")
    try:
        recommendations = engine.get_recommendations({"language": "python"})
        print(f"✓ Found {len(recommendations)} recommendations")
    except Exception as e:
        print(f"✗ Recommendations error: {e}")

if __name__ == "__main__":
    test_models()
    test_data_management()
    print("\n" + "=" * 50)
    print("Testing completed!")