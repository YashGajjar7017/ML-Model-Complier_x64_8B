"""
REST API for CodeForge AI
Provides endpoints for code generation, testing, and training
"""

from flask import Flask, request, jsonify
import json
import logging
from datetime import datetime

from codeforge_ai.core_engine import CodeForgeAI, Language, CodeGenerationRequest, format_json_response, ModelType
from codeforge_ai.manual_training import ManualTrainingSystem, CodeFeedback, create_feedback_from_dict
from codeforge_ai.automatic_training import AutomaticTrainingSystem

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize systems
code_forge = CodeForgeAI()
manual_trainer = ManualTrainingSystem(storage_path="training_data")
auto_trainer = AutomaticTrainingSystem(storage_path="training_data", models_path="models")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


@app.route('/generate', methods=['POST'])
def generate_code():
    """
    Generate code from problem description
    
    Request body:
    {
        "problem_description": "...",
        "language": "python|javascript|java|cpp|rust|go",
        "model_type": "pattern_based|template_based|optimization_focused|readability_focused|performance_focused",
        "constraints": {...},
        "examples": [...]
    }
    """
    try:
        data = request.json
        
        # Validate input
        if not data.get('problem_description'):
            return jsonify({'error': 'Missing problem_description'}), 400
        
        if not data.get('language'):
            return jsonify({'error': 'Missing language'}), 400
        
        # Create request
        language = Language[data['language'].upper()]
        model_type = ModelType[data.get('model_type', 'pattern_based').upper().replace('-', '_')]
        
        request_obj = CodeGenerationRequest(
            problem_description=data['problem_description'],
            language=language,
            model_type=model_type,
            constraints=data.get('constraints'),
            examples=data.get('examples'),
            style_guide=data.get('style_guide')
        )
        
        # Generate code
        response = code_forge.generate_code(request_obj)
        
        logger.info(f"Generated {language.value} code using {model_type.value} model with confidence: {response.confidence:.2f}")
        
        # Return JSON response
        return jsonify(format_json_response(response)), 200
    
    except KeyError as e:
        return jsonify({'error': f'Invalid language or model type: {e}'}), 400
    except Exception as e:
        logger.error(f"Error during code generation: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/test', methods=['POST'])
def test_code():
    """
    Execute generated code against test cases
    
    Request body:
    {
        "code": "...",
        "language": "python|javascript",
        "test_cases": [
            {"input": ..., "expected_output": ...},
            ...
        ]
    }
    """
    try:
        data = request.json
        
        code = data.get('code')
        language = data.get('language', 'python')
        test_cases = data.get('test_cases', [])
        
        if not code:
            return jsonify({'error': 'Missing code'}), 400
        
        # Run tests
        results, metric = auto_trainer.execute_and_test(code, language, test_cases)
        
        # Generate feedback
        feedback = auto_trainer.generate_reinforcement_feedback(results)
        
        # Format results
        response = {
            'test_results': [
                {
                    'test_id': r.test_id,
                    'passed': r.passed,
                    'execution_time': r.execution_time,
                    'output': r.output,
                    'expected': r.expected_output,
                    'error': r.error
                }
                for r in results
            ],
            'metrics': {
                'language': metric.language,
                'test_count': metric.test_count,
                'pass_rate': metric.pass_rate,
                'avg_execution_time': metric.avg_execution_time,
                'correctness_score': metric.correctness_score,
                'optimization_score': metric.optimization_score
            },
            'reinforcement_feedback': feedback
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error during testing: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """
    Submit user feedback on generated code
    
    Request body:
    {
        "generation_id": "...",
        "rating": 1-5,
        "correctness": true/false,
        "efficiency_rating": 1-5,
        "readability_rating": 1-5,
        "comments": "...",
        "suggested_improvements": "..."
    }
    """
    try:
        data = request.json
        
        # Create feedback object
        feedback_dict = {
            'generation_id': data.get('generation_id'),
            'rating': data.get('rating', 3),
            'correctness': data.get('correctness', True),
            'efficiency_rating': data.get('efficiency_rating', 3),
            'readability_rating': data.get('readability_rating', 3),
            'comments': data.get('comments', ''),
            'suggested_improvements': data.get('suggested_improvements', ''),
            'timestamp': datetime.now().isoformat(),
            'user_id': data.get('user_id', 'anonymous'),
            'language': data.get('language', 'unknown'),
            'problem_type': data.get('problem_type', 'general')
        }
        
        feedback = create_feedback_from_dict(feedback_dict)
        
        # Save feedback
        manual_trainer.save_feedback(feedback)
        
        # Learn from feedback
        insights = manual_trainer.learn_from_feedback(data.get('generation_id', 'unknown'), feedback)
        
        # Get recommendations
        recommendations = manual_trainer.get_improvement_recommendations(data.get('generation_id', 'unknown'))
        
        response = {
            'status': 'feedback_recorded',
            'generation_id': data.get('generation_id'),
            'rating': data.get('rating'),
            'insights': insights,
            'recommendations': recommendations
        }
        
        logger.info(f"Feedback recorded with rating: {data.get('rating')}/5")
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/metrics/manual', methods=['GET'])
def get_manual_metrics():
    """Get manual training metrics"""
    try:
        language = request.args.get('language')
        metrics = manual_trainer.get_learning_metrics(language)
        
        response = {
            'timestamp': datetime.now().isoformat(),
            'metrics': {k: dict(v.__dict__) if hasattr(v, '__dict__') else v 
                       for k, v in metrics.items()}
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error getting manual metrics: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/metrics/automatic', methods=['GET'])
def get_automatic_metrics():
    """Get automatic training metrics"""
    try:
        language = request.args.get('language')
        metrics = auto_trainer.get_performance_metrics(language)
        
        response = {
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error getting automatic metrics: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/reports/manual', methods=['GET'])
def get_manual_report():
    """Get comprehensive manual training report"""
    try:
        report = manual_trainer.generate_training_report()
        return jsonify(report), 200
    
    except Exception as e:
        logger.error(f"Error generating manual report: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/reports/automatic', methods=['GET'])
def get_automatic_report():
    """Get comprehensive automatic training report"""
    try:
        report = auto_trainer.generate_automatic_training_report()
        return jsonify(report), 200
    
    except Exception as e:
        logger.error(f"Error generating automatic report: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/patterns/<language>', methods=['GET'])
def get_learned_patterns(language):
    """Get learned patterns for a specific language"""
    try:
        patterns = manual_trainer.get_language_patterns(language)
        
        response = {
            'language': language,
            'patterns_count': len(patterns) if patterns else 0,
            'patterns': patterns or {}
        }
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error getting patterns: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/data/statistics', methods=['GET'])
def get_data_statistics():
    """Get statistics about categorized training data"""
    try:
        stats = code_forge.get_data_statistics()
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'statistics': stats
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting data statistics: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/data/similar', methods=['POST'])
def find_similar_problems():
    """
    Find similar problems based on description
    
    Request body:
    {
        "problem_description": "...",
        "limit": 5
    }
    """
    try:
        data = request.json
        problem_description = data.get('problem_description', '')
        limit = data.get('limit', 5)
        
        if not problem_description:
            return jsonify({'error': 'Missing problem_description'}), 400
        
        similar_problems = code_forge.get_similar_problems(problem_description, limit)
        
        return jsonify({
            'query': problem_description,
            'limit': limit,
            'similar_problems': similar_problems,
            'count': len(similar_problems)
        }), 200
    
    except Exception as e:
        logger.error(f"Error finding similar problems: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/data/recommendations', methods=['POST'])
def get_recommendations():
    """
    Get recommendations based on criteria
    
    Request body:
    {
        "language": "python",
        "problem_type": "sorting",
        "complexity": "medium",
        "min_rating": 3
    }
    """
    try:
        criteria = request.json or {}
        recommendations = code_forge.get_recommendations(criteria)
        
        return jsonify({
            'criteria': criteria,
            'recommendations': recommendations,
            'count': len(recommendations)
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info("Starting CodeForge AI API server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
