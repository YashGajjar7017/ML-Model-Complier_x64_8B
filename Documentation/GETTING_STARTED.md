# Getting Started with CodeForge AI

## Installation & Setup

### 1. Environment Setup

```bash
# Navigate to project directory
cd d:\Coding\Machine_learning\ML-Complier-Training

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Project Structure

```
ML-Complier-Training/
├── codeforge_ai/                    # Main package
│   ├── __init__.py                 # Package initialization
│   ├── core_engine.py              # Code generation engine (1,100+ lines)
│   ├── manual_training.py          # Manual learning system (400+ lines)
│   ├── automatic_training.py       # Automatic learning system (500+ lines)
│   ├── api_server.py               # REST API (400+ lines)
│   └── demo.py                     # Interactive demo
│
├── training_data/                  # Persistent storage (auto-created)
│   ├── feedback_history.json       # User feedback records
│   ├── test_results.json           # Automatic test results
│   └── learned_patterns.json       # Learned code patterns
│
├── test_cases/                     # Example problems
│   └── problems.json               # Problem definitions & test cases
│
├── models/                         # Trained models (future)
├── logs/                           # System logs
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── README.md                       # Main documentation
├── test_suite.py                   # Comprehensive test suite
├── interactive_cli.py              # Interactive CLI interface
└── GETTING_STARTED.md             # This file
```

---

## Quick Start Options

### Option 1: Run Interactive Demo (Recommended)

```bash
python codeforge_ai/demo.py
```

**Output:**
- Generates sample code in Python and JavaScript
- Executes automatic training with test cases
- Demonstrates manual training with user feedback
- Shows metrics and learning insights

**Time:** ~2 minutes

---

### Option 2: Start REST API Server

```bash
python codeforge_ai/api_server.py
```

**Server Details:**
- Host: `http://localhost:5000`
- Docs: Available via API endpoints
- Debug mode: Enabled for development

**In another terminal, test endpoints:**

```bash
# Generate code
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "problem_description": "Fibonacci sequence",
    "language": "python"
  }'

# Check system status
curl http://localhost:5000/status

# Get metrics
curl http://localhost:5000/metrics/manual
curl http://localhost:5000/metrics/automatic
```

---

### Option 3: Interactive CLI

```bash
python interactive_cli.py
```

**Menu Options:**
1. Generate Code - Create new code from problem descriptions
2. Test Code - Execute code against test cases
3. Submit Feedback - Provide user ratings and comments
4. View Metrics - See training progress
5. View Reports - Get comprehensive reports
6. Run Demo - Launch full demonstration
7. Exit

**Interactive Features:**
- Real-time code generation feedback
- Immediate learning from your input
- Metrics tracking for each interaction
- Reports on system learning progress

---

### Option 4: Run Tests

```bash
python test_suite.py
```

**Tests Included:**
- Code generation validation
- Syntax checking for multiple languages
- Manual training feedback processing
- Automatic training test execution
- Data persistence verification
- End-to-end integration tests

---

## Core Features Explained

### 1. Code Generation (`core_engine.py`)

**Capabilities:**
- Generate syntactically valid code in 7 languages
- Analyze code complexity (time & space)
- Calculate confidence scores
- Evaluate best practices compliance
- Maintain generation history

**Usage Example:**
```python
from codeforge_ai import CodeForgeAI, Language, CodeGenerationRequest

code_forge = CodeForgeAI()

request = CodeGenerationRequest(
    problem_description="Sort array efficiently",
    language=Language.PYTHON,
    constraints={"max_size": 1000}
)

response = code_forge.generate_code(request)
print(f"Code:\n{response.code}")
print(f"Confidence: {response.confidence}")
print(f"Complexity: {response.complexity}")
```

### 2. Automatic Training (`automatic_training.py`)

**How It Works:**
1. Execute generated code against test cases
2. Collect execution metrics (time, correctness, memory)
3. Analyze performance
4. Generate reinforcement learning signals
5. Update learned patterns

**Metrics Collected:**
- Pass rate (% tests passing)
- Execution time per test
- Correctness score (0-1)
- Optimization score (0-1)
- Error analysis

**Usage Example:**
```python
from codeforge_ai import AutomaticTrainingSystem

trainer = AutomaticTrainingSystem()

test_cases = [
    {"input": 5, "expected_output": [0, 1, 1, 2, 3]},
    {"input": 10, "expected_output": [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]}
]

results, metrics = trainer.execute_and_test(code, "python", test_cases)
feedback = trainer.generate_reinforcement_feedback(results)
print(f"Pass Rate: {metrics.pass_rate}")
print(f"Reward: {feedback['total_reward']}")
```

### 3. Manual Training (`manual_training.py`)

**How It Works:**
1. Collect user feedback (rating 1-5, correctness, efficiency, readability)
2. Extract learning insights from feedback
3. Identify best practices and anti-patterns
4. Store learned patterns
5. Update language-specific models

**Feedback Types:**
- Overall rating (1-5 stars)
- Correctness (boolean)
- Efficiency rating (1-5)
- Readability rating (1-5)
- Comments and suggestions

**Usage Example:**
```python
from codeforge_ai import ManualTrainingSystem, CodeFeedback

trainer = ManualTrainingSystem()

feedback = CodeFeedback(
    generation_id="gen_001",
    rating=5,
    correctness=True,
    efficiency_rating=4,
    readability_rating=5,
    comments="Excellent solution",
    suggested_improvements="Add more docstrings",
    timestamp=None,
    user_id="expert"
)

trainer.save_feedback(feedback)
insights = trainer.learn_from_feedback("gen_001", feedback)
print(f"Best Practices: {insights['best_practices_identified']}")
```

### 4. REST API (`api_server.py`)

**Available Endpoints:**

#### `/generate` (POST)
Generate code from problem description
```json
{
    "problem_description": "...",
    "language": "python|javascript|java|cpp|rust|go",
    "constraints": {...},
    "examples": [...]
}
```

#### `/test` (POST)
Execute code against test cases
```json
{
    "code": "...",
    "language": "python",
    "test_cases": [
        {"input": ..., "expected_output": ...}
    ]
}
```

#### `/feedback` (POST)
Submit user feedback for manual training
```json
{
    "generation_id": "...",
    "rating": 5,
    "correctness": true,
    "efficiency_rating": 4,
    "readability_rating": 5,
    "comments": "...",
    "suggested_improvements": "..."
}
```

#### `/metrics/manual` (GET)
Get manual training metrics
```
GET /metrics/manual?language=python
```

#### `/metrics/automatic` (GET)
Get automatic training metrics
```
GET /metrics/automatic?language=python
```

#### `/reports/manual` (GET)
Get comprehensive manual training report

#### `/reports/automatic` (GET)
Get comprehensive automatic training report

#### `/status` (GET)
Get system status and overall statistics

---

## Training Workflows

### Workflow 1: Automatic Learning

```
Generate Code
    ↓
Execute Tests
    ↓
Collect Metrics
    ↓
Analyze Performance
    ↓
Generate Reward Signal
    ↓
Update Patterns
    ↓
Improve Future Generations
```

### Workflow 2: Manual Learning

```
Generate Code
    ↓
User Reviews Code
    ↓
Submits Rating + Feedback
    ↓
Extract Insights
    ↓
Identify Best Practices
    ↓
Store Learned Patterns
    ↓
Improve Future Generations
```

### Workflow 3: Combined (Recommended)

```
Generate Code
    ↓
├─→ Automatic Training (Test Execution)
│       ├─ Check Correctness
│       └─ Measure Performance
│
├─→ Manual Training (User Feedback)
│       ├─ Collect Ratings
│       └─ Extract Insights
│
├─→ Pattern Learning
│       ├─ Store Successful Approaches
│       └─ Mark Anti-patterns
│
└─→ Generate Metrics & Reports
        └─ Show Progress & Recommendations
```

---

## Configuration

Edit `config.py` to customize:

**Key Settings:**
- `AUTOMATIC_TRAINING["enabled"]` - Enable/disable automatic testing
- `MANUAL_TRAINING["enabled"]` - Enable/disable manual feedback
- `SUPPORTED_LANGUAGES` - Add/remove language support
- `CODE_GENERATION["max_code_length"]` - Maximum code size
- `METRICS["aggregation_interval"]` - Metrics collection frequency

---

## Example Use Cases

### 1. Learning Algorithm Implementation

```
Problem: Implement merge sort
↓
Generate: CodeForge creates merge sort implementation
↓
Auto-Test: Executes against 10 test cases
↓
Result: 100% pass rate, O(n log n) confirmed
↓
User Rates: 5/5 - "Excellent, efficient, well-commented"
↓
Learning: Stores merge sort pattern for future sorting problems
```

### 2. Learning from Mistakes

```
Problem: Fibonacci with constraint (fast for n=100)
↓
Generate: CodeForge creates recursive solution
↓
Auto-Test: Timeout on large inputs
↓
Result: Slow performance detected
↓
Learning: Pattern marked as inefficient for large inputs
↓
Next Time: Generates iterative solution
```

### 3. Collaborative Improvement

```
User 1: Rates generated code 3/5 - "Works but inefficient"
↓
Learning: System notes efficiency concerns
↓
User 2: Rates generated code 2/5 - "Very slow"
↓
Learning: Anti-pattern confirmed
↓
System: Switches to alternative algorithm
↓
User 3: Rates new code 5/5 - "Perfect!"
↓
Learning: New pattern validated and stored
```

---

## Monitoring & Metrics

### Manual Training Metrics
- Average rating by language
- Success rate (% of 4-5 star ratings)
- Total feedback records
- Improvement patterns identified

### Automatic Training Metrics
- Test pass rate
- Avg execution time
- Correctness score
- Optimization score

### Combined Insights
- Total training data points
- Languages trained
- Learning acceleration
- Pattern effectiveness

---

## Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
pip install -r requirements.txt
# or for specific module:
pip install flask requests numpy pandas
```

### Issue: Port 5000 already in use

**Solution:**
```bash
# Change port in api_server.py:
# app.run(port=5001)
# or kill process using port 5000
```

### Issue: Automatic training gives errors

**Solution:**
- Some test execution requires proper Python/Node.js environment
- Check code syntax validity first
- Review test case format in problems.json

### Issue: No feedback data saving

**Solution:**
- Check training_data/ directory exists
- Verify write permissions
- Check logs/ for error messages

---

## Next Steps

1. **Run the demo** to see all features
2. **Explore the API** using the interactive CLI
3. **Add custom problems** to test_cases/problems.json
4. **Submit feedback** to train the system
5. **Monitor metrics** to track learning progress

---

## Performance Notes

- **First Generation:** ~1-2 seconds
- **Test Execution:** Depends on code complexity (typically <1 second per test)
- **Feedback Processing:** Immediate
- **Report Generation:** <1 second
- **Memory Usage:** ~50-100 MB baseline

---

## Support & Contribution

### Contributing
- Add new language support in core_engine.py
- Extend syntax validators
- Create new test problem sets
- Improve algorithm patterns

### Reporting Issues
- Check error logs in logs/
- Review README.md and GETTING_STARTED.md
- Test with demo.py first

---

## Summary

CodeForge AI provides a **complete, self-improving code generation system** that learns through:
- ✅ Automatic training (test execution & metrics)
- ✅ Manual training (user feedback & ratings)
- ✅ Reinforcement learning (reward signals)
- ✅ Pattern storage & reuse
- ✅ Comprehensive metrics & reporting

**Start exploring now:**
```bash
python codeforge_ai/demo.py
```

Enjoy! 🚀
