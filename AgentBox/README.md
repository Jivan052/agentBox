# 🧠 CodeGuard Environment

## 📌 Overview
CodeGuard is a deterministic RL-style environment for evaluating code-fixing agents.  
It simulates tasks like lint fixing, vulnerability patching, and structural refactoring with strict reward and grading rules.

---

## 🧩 Environment Schema

### State
```json
{
	"score": "float",
	"history": [
		{
			"step": "int",
			"action": "str",
			"reward": "float"
		}
	]
}
```

### Action
- Type: `str`
- Constraints:
	- Non-empty
	- Max length: 1000 chars

### Reward
- Range: `[-2.5, 1.0]`
- Components:
	- Task score (grader)
	- `-0.02` step penalty
	- `-2.0` destructive penalty

## 🧪 Tasks & Difficulty

### 🟢 Easy — Lint Fix
- Goal: Fix syntax errors
- Grader: `ast.parse()`
- Output: `0.0` or `1.0`

### 🟡 Medium — Vulnerability Patch
- Goal: Remove unsafe calls (`eval`, `exec`, etc.)
- Checks:
	- Unsafe calls removed
	- Function structure preserved
- Output: `0.0 – 1.0`

### 🔴 Hard — Refactor + Type Hints
- Goal: Improve structure + add typing
- Checks:
	- Structural preservation
	- Type annotations present
- Output: `0.0 – 1.0`

## ⚙️ Setup & Usage

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run API Server
```bash
uvicorn src.env:app --host 0.0.0.0 --port 7860
```

### Run Inference Loop
```bash
export HF_TOKEN=your_token
python inference.py
```

## 📊 Baseline Scores (Mock)

| Task | Score |
|---|---:|
| Easy | 0.88 |
| Medium | 0.71 |
| Hard | 0.54 |

Model: `gpt-4.1-mini`

## 🧪 Testing

Run validation tests:

```bash
pytest tests/
```

## 📌 Notes
- All graders are deterministic & stateless
- Execution time per grading <50ms
- No randomness in reward or evaluation
