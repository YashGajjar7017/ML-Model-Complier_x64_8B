# CodeForge AI - ML Compiler Training System

A self-improving programming assistant that learns through **both manual and automatic training** to generate high-quality code across multiple programming languages.

## 🎯 Core Capabilities

1. **Multi-Language Code Generation** - Generate syntactically valid code in Python, JavaScript, Java, C++, Rust, and Go
2. **Automatic Training** - Improve through test execution, metrics collection, and reinforcement learning
3. **Manual Training** - Learn from user feedback, ratings, and improvement suggestions
4. **Reinforcement Learning** - Generate reward signals based on test results and performance
5. **Pattern Learning** - Store and reuse successful code patterns
6. **Comprehensive Metrics** - Track progress across multiple dimensions

## 📁 Project Structure

```
ML-Complier-Training/
├── codeforge_ai/              # Main system
│   ├── core_engine.py        # Code generation engine
│   ├── manual_training.py    # User feedback learning
│   ├── automatic_training.py # Test execution learning
│   ├── api_server.py         # REST API
│   └── demo.py               # Interactive demonstration
│
├── training_data/            # Persistent storage
│   ├── feedback_history.json
│   ├── test_results.json
│   └── learned_patterns.json
│
├── test_cases/              # Example problems
│   └── problems.json
│
├── models/                  # Trained models
├── logs/                    # System logs
└── requirements.txt
```

## 🚀 Quick Start

### Installation

```bash
cd ML-Complier-Training
pip install -r requirements.txt
```

### Run Demo

```bash
python codeforge_ai/demo.py
```

This demonstrates:
- Code generation for multiple languages
- Automatic training through test execution
- Manual training through user feedback
- Complete end-to-end workflow

### Start API Server

```bash
python codeforge_ai/api_server.py
```

Server runs on `http://localhost:5000`

## 📡 API Endpoints

### Generate Code

```bash
POST /generate
Content-Type: application/json

{
    "problem_description": "Generate a function to compute Fibonacci sequence",
    "language": "python",
    "constraints": {"max_n": 100},
    "examples": [{"input": 5, "output": [0, 1, 1, 2, 3]}]
}
```

**Response:**
```json
{
    "language": "python",
    "description": "Generated solution for: Generate Fibonacci...",
    "code": "def fibonacci(n):\n    ...",
    "complexity": "O(n)",
    "confidence": 0.85,
    "syntax_valid": true,
    "best_practices_score": 0.9
}
```

### Test Code

```bash
POST /test
Content-Type: application/json

{
    "code": "def fibonacci(n):\n    ...",
    "language": "python",
    "test_cases": [
        {"input": 5, "expected_output": [0, 1, 1, 2, 3]},
        {"input": 10, "expected_output": [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]}
    ]
}
```

### Submit Feedback (Manual Training)

```bash
POST /feedback
Content-Type: application/json

{
    "generation_id": "gen_001",
    "rating": 5,
    "correctness": true,
    "efficiency_rating": 4,
    "readability_rating": 5,
    "comments": "Excellent solution",
    "suggested_improvements": "Add type hints; Add more examples",
    "language": "python",
    "problem_type": "algorithm_design"
}
```

### Get Metrics

```bash
GET /metrics/manual?language=python
GET /metrics/automatic?language=python
```

### Get Reports

```bash
GET /reports/manual
GET /reports/automatic
```

## 🧠 Training Systems

### Automatic Training

Learns through code execution against test cases:

- **Test Execution**: Runs generated code with test inputs
- **Metrics Collection**: Tracks execution time, correctness, memory
- **Reinforcement Signals**: Generates rewards/penalties based on results
- **Performance Analysis**: Identifies optimization opportunities
- **Pattern Extraction**: Stores successful algorithms and approaches

**Example Flow:**
```
Generate Code → Execute Tests → Collect Metrics → 
Analyze Performance → Extract Patterns → Update Model
```

### Manual Training

Learns from expert feedback and user ratings:

- **Feedback Collection**: Rating (1-5), correctness, efficiency, readability
- **Insight Extraction**: Identifies best practices and anti-patterns
- **Pattern Storage**: Saves successful approaches for reuse
- **Recommendation Generation**: Provides improvement suggestions
- **Metrics Tracking**: Monitors learning progress by language and problem type

**Example Flow:**
```
User Reviews Code → Provides Rating + Feedback → 
System Analyzes Feedback → Extracts Insights → 
Updates Learned Patterns → Improves Future Generations
```

## 📊 Metrics & Reporting

### Manual Training Metrics
- Average rating by language/problem type
- Success rate (% of high-rated solutions)
- Learning progress over time
- Improvement patterns identified

### Automatic Training Metrics
- Pass rate across test cases
- Average execution time
- Correctness score (0-1)
- Optimization score (0-1)
- Performance trends

### Combined Reporting
- Overall system performance
- Language-specific progress
- Pattern effectiveness
- Learning acceleration metrics

## 🔧 Configuration

Edit `test_cases/problems.json` to:
- Add new example problems
- Define test cases and constraints
- Set evaluation criteria
- Configure training behavior

## 💡 Key Features

✅ **Dual Learning**: Both automatic (tests) and manual (feedback) training
✅ **Multi-Language**: Extensible support for new languages
✅ **Self-Improvement**: System gets better with more training data
✅ **Transparency**: Full metrics and insights into learning process
✅ **Scalability**: API-based architecture for distributed learning
✅ **Persistence**: All training data and patterns stored persistently
✅ **Reinforcement**: Reward/penalty signals guide improvement

## 🎓 Learning Examples

### Automatic Learning Example
```
Problem: Sort array
Generated Code: Basic bubble sort (O(n²))
Test Results: Pass 90%, Avg time 2.5s
Feedback: Slow performance detected
Learning: Store merge sort pattern as better alternative
Next Generation: Generates merge sort (O(n log n))
```

### Manual Learning Example
```
Generated Code: Fibonacci (recursive without memoization)
User Rating: 2/5 stars
Feedback: "Very slow, add memoization"
Learning: Extract pattern "use memoization for recursion"
Next Generation: Generates optimized version with memoization
Updated Confidence: ↑ from 0.65 to 0.85
```

## 🚀 Future Enhancements

- [ ] Large Language Model (LLM) integration for better code generation
- [ ] Distributed training across multiple machines
- [ ] Advanced pattern recognition with ML
- [ ] Code quality metrics (cyclomatic complexity, etc.)
- [ ] Real-time performance monitoring
- [ ] Feedback loop optimization
- [ ] Multi-library support and imports
- [ ] Security vulnerability detection

## 📝 License

MIT License - See LICENSE file

## 👥 Contributing

Contributions welcome! Areas for improvement:
- Add more language support
- Enhance test case generation
- Improve pattern recognition
- Optimize reinforcement learning rewards

---

**Created**: March 2026
**System Status**: Active and Learning
**Total Training Data**: Accumulating
