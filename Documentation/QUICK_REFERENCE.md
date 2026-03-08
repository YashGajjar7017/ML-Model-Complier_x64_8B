# CodeForge AI - Quick Reference Card

## 🚀 Get Started in 30 Seconds

```bash
cd d:\Coding\Machine_learning\ML-Complier-Training
pip install -r requirements.txt
python codeforge_ai/demo.py
```

## 📱 Three Ways to Use

### 1️⃣ Demo Script (Automatic - 2 min)
```bash
python codeforge_ai/demo.py
```
Shows all features with examples

### 2️⃣ Interactive CLI (Manual - Per use)
```bash
python interactive_cli.py
```
Menu-driven interface, interactive prompts

### 3️⃣ REST API (Integration - Continuous)
```bash
python codeforge_ai/api_server.py
# Then: curl http://localhost:5000/generate -X POST
```

---

## 🔥 Most Common Commands

### Generate Code
```python
from codeforge_ai import CodeForgeAI, Language, CodeGenerationRequest

code_forge = CodeForgeAI()
response = code_forge.generate_code(
    CodeGenerationRequest("Fibonacci sequence", Language.PYTHON)
)
print(response.code)
```

### Test Code
```python
from codeforge_ai import AutomaticTrainingSystem

trainer = AutomaticTrainingSystem()
results, metrics = trainer.execute_and_test(
    code="def fib(n): ...",
    language="python",
    test_cases=[{"input": 5, "expected_output": [0,1,1,2,3]}]
)
print(f"Pass: {metrics.pass_rate:.1%}")
```

### Submit Feedback
```python
from codeforge_ai import ManualTrainingSystem, CodeFeedback

trainer = ManualTrainingSystem()
feedback = CodeFeedback(
    generation_id="gen_001", rating=5, correctness=True,
    efficiency_rating=4, readability_rating=5,
    comments="Great!", suggested_improvements="",
    timestamp=None, user_id="me"
)
trainer.save_feedback(feedback)
```

### Get Metrics
```python
from codeforge_ai import ManualTrainingSystem

trainer = ManualTrainingSystem()
metrics = trainer.get_learning_metrics()
for key, m in metrics.items():
    print(f"{key}: {m.avg_rating:.1f}/5.0")
```

---

## 🌐 API Endpoints

### Generate
```bash
POST /generate
{
    "problem_description": "...",
    "language": "python"
}
```

### Test
```bash
POST /test
{
    "code": "...",
    "language": "python",
    "test_cases": [{"input": ..., "expected_output": ...}]
}
```

### Feedback
```bash
POST /feedback
{
    "generation_id": "...",
    "rating": 5,
    "correctness": true,
    "efficiency_rating": 4,
    "readability_rating": 5
}
```

### Metrics & Reports
```bash
GET /metrics/manual
GET /metrics/automatic
GET /reports/manual
GET /reports/automatic
GET /status
```

---

## 📊 Supported Languages

```python
Language.PYTHON        # ✅
Language.JAVASCRIPT    # ✅
Language.JAVA          # ✅
Language.CPP           # ✅
Language.RUST          # ✅
Language.GO            # ✅
Language.TYPESCRIPT    # ✅
```

---

## 📁 Key Files & Their Purpose

| File | Purpose | When to Use |
|------|---------|------------|
| `core_engine.py` | Code generation | Generating code |
| `manual_training.py` | User feedback learning | Collecting ratings |
| `automatic_training.py` | Test execution learning | Running tests |
| `api_server.py` | REST API | Integration, web apps |
| `demo.py` | Full demonstration | Learning the system |
| `interactive_cli.py` | Command-line interface | Interactive use |
| `test_suite.py` | Tests | Validation |
| `config.py` | Configuration | Customization |

---

## ⚙️ Configuration

Edit `config.py` for:
- Storage paths
- API settings
- Training parameters
- Language support
- Metric collection

---

## 📈 What Gets Stored

**Persistent Data** (auto-created):
- `training_data/feedback_history.json` - User ratings
- `training_data/test_results.json` - Test execution results
- `training_data/learned_patterns.json` - Learned patterns

**Access Example**:
```bash
# View feedback
cat training_data/feedback_history.json

# View test results
cat training_data/test_results.json

# View patterns
cat training_data/learned_patterns.json
```

---

## 🎯 Learning Flow

```
Generate Code
    ↓
├─ Automatic: Run tests → Collect metrics
│
├─ Manual: User rates → Extract insights
│
└─ Result: Both improve future generations
```

---

## 🔍 Example Problem Types

Predefined in `test_cases/problems.json`:
- Fibonacci sequence (easy)
- Sorting algorithm (medium)
- Binary search (medium)
- Dynamic programming (hard)

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| "Module not found" | `pip install -r requirements.txt` |
| Port 5000 in use | Change port in `api_server.py` |
| Tests fail | Check Python environment, review logs/ |
| No data saved | Verify training_data/ directory exists |

---

## 📊 Check System Status

```bash
# Via API
curl http://localhost:5000/status

# Via Python
from codeforge_ai import ManualTrainingSystem
trainer = ManualTrainingSystem()
report = trainer.generate_training_report()
print(f"Feedback records: {report['total_feedback_records']}")
```

---

## 🎓 Learning Examples

### Example 1: Fibonacci
```bash
# Generate → Test → Get Feedback
curl -X POST http://localhost:5000/generate \
  -d '{"problem_description": "Fibonacci", "language": "python"}'

# Test the code
curl -X POST http://localhost:5000/test \
  -d '{"code": "...", "language": "python", "test_cases": [...]}'

# Submit rating
curl -X POST http://localhost:5000/feedback \
  -d '{"generation_id": "...", "rating": 5, ...}'
```

### Example 2: Full Workflow
```python
# 1. Generate
code_forge = CodeForgeAI()
response = code_forge.generate_code(request)

# 2. Test
auto_trainer = AutomaticTrainingSystem()
results, metrics = auto_trainer.execute_and_test(response.code, ...)

# 3. Feedback
manual_trainer = ManualTrainingSystem()
feedback = CodeFeedback(...)
manual_trainer.save_feedback(feedback)

# 4. Learn
insights = manual_trainer.learn_from_feedback(gen_id, feedback)

# 5. Report
report = manual_trainer.generate_training_report()
```

---

## 💡 Pro Tips

✅ **Start with demo**: `python codeforge_ai/demo.py`
✅ **Use interactive CLI**: `python interactive_cli.py`
✅ **Check status**: `curl http://localhost:5000/status`
✅ **View metrics**: `curl http://localhost:5000/metrics/manual`
✅ **Run tests**: `python test_suite.py`

---

## 📚 Documentation

- **README.md** - Main overview
- **GETTING_STARTED.md** - Installation & setup
- **PROJECT_SUMMARY.md** - Detailed design
- **INDEX.md** - Complete file reference
- **QUICK_REFERENCE.md** - This file

---

## 🎯 Key Concepts

**Automatic Training**: System learns by running tests and analyzing results
**Manual Training**: System learns from user feedback and ratings
**Reinforcement**: Positive results rewarded, negative results penalized
**Patterns**: Successful approaches stored for future reuse
**Metrics**: System progress tracked with detailed analytics

---

## ✅ Verification

All components working?
```bash
python test_suite.py
```

Everything set up?
```bash
python codeforge_ai/demo.py
```

Ready to code?
```bash
python interactive_cli.py
```

---

## 📞 Need Help?

1. Read `GETTING_STARTED.md` for common issues
2. Check `logs/` directory for error details
3. Run `test_suite.py` to validate system
4. Review docstrings in source code
5. Try the demo: `python codeforge_ai/demo.py`

---

## 🚀 You're Ready!

Pick one and go:

1. **Try Demo**: `python codeforge_ai/demo.py`
2. **Use CLI**: `python interactive_cli.py`
3. **Start API**: `python codeforge_ai/api_server.py`
4. **Run Tests**: `python test_suite.py`

Enjoy! 🎉
