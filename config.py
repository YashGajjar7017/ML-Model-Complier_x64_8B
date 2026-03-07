# CodeForge AI Configuration

# System Settings
SYSTEM_NAME = "CodeForge AI"
VERSION = "1.0.0"
DEBUG = True

# Storage Configuration
STORAGE_PATH = "training_data"
MODELS_PATH = "models"
LOGS_PATH = "logs"

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 5000
API_DEBUG = True
API_WORKERS = 4

# Automatic Training Configuration
AUTOMATIC_TRAINING = {
    "enabled": True,
    "execution_timeout": 5.0,
    "max_concurrent_tests": 4,
    "metric_collection": {
        "execution_time": True,
        "memory_usage": True,
        "correctness": True,
        "output_matching": True
    }
}

# Manual Training Configuration
MANUAL_TRAINING = {
    "enabled": True,
    "feedback_types": [
        "rating",
        "correctness",
        "efficiency_rating",
        "readability_rating",
        "comments",
        "suggested_improvements"
    ],
    "rating_scale": 5,
    "learning_frequency": "immediate"
}

# Reinforcement Learning Configuration
REINFORCEMENT_LEARNING = {
    "enabled": True,
    "reward_function": "correctness_weighted",
    "penalty_for_timeout": -0.5,
    "penalty_for_error": -0.3,
    "bonus_for_optimization": 0.1,
    "bonus_for_all_tests_pass": 0.2
}

# Supported Languages
SUPPORTED_LANGUAGES = [
    "python",
    "javascript",
    "java",
    "cpp",
    "rust",
    "go",
    "typescript"
]

# Code Generation Configuration
CODE_GENERATION = {
    "max_code_length": 5000,
    "min_code_length": 10,
    "include_comments": True,
    "include_docstrings": True,
    "syntax_validation": True,
    "best_practices_check": True
}

# Complexity Analysis Configuration
COMPLEXITY_ANALYSIS = {
    "enabled": True,
    "target_time_complexity": ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n²)"],
    "target_space_complexity": ["O(1)", "O(log n)", "O(n)"]
}

# Metrics Configuration
METRICS = {
    "track_confidence": True,
    "track_best_practices_score": True,
    "track_pass_rate": True,
    "track_execution_time": True,
    "track_optimization_score": True,
    "aggregation_interval": 3600  # seconds
}

# Logging Configuration
LOGGING = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/codeforge.log",
    "max_file_size": 10485760,  # 10 MB
    "backup_count": 5
}

# Learning Rate Configuration
LEARNING_CONFIG = {
    "pattern_storage_threshold": 0.75,  # Store patterns with >75% success rate
    "anti_pattern_threshold": 0.3,      # Mark as anti-pattern if <30% success
    "update_frequency": "adaptive",      # Update patterns after N feedbacks
    "update_count": 5                    # After 5 feedbacks
}

# Test Case Configuration
TEST_CASES = {
    "auto_generate": False,
    "validation_on_execution": True,
    "timeout_per_case": 5.0,
    "max_output_size": 1000000  # 1 MB
}

# Performance Optimization
PERFORMANCE = {
    "cache_generated_code": True,
    "cache_test_results": True,
    "cache_patterns": True,
    "cache_ttl": 3600  # 1 hour
}

# Feedback Processing
FEEDBACK_PROCESSING = {
    "normalize_ratings": True,
    "weighted_averaging": True,
    "anomaly_detection": False,
    "min_feedback_for_metric": 3
}

# System Behavior
BEHAVIOR = {
    "auto_save_training_data": True,
    "auto_save_interval": 300,  # 5 minutes
    "persist_to_disk": True,
    "aggregate_metrics": True,
    "generate_reports": True
}
