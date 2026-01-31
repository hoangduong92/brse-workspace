# Fix Import Issues: Phase 1 & 2

**Issue:** 64 tests fail due to relative import path issues
**Impact:** Cannot validate bk-recall and bk-track modules
**Priority:** P0 - CRITICAL BLOCKER
**Effort:** 1-2 hours

---

## Root Cause Analysis

### Problem
Tests in Phase 1 and Phase 2 use relative imports that fail when pytest runs from workspace root:

```python
# In .claude/skills/bk-recall/scripts/summarizer.py (line 5)
from ..lib.vault import VaultSearch
# ❌ ImportError: attempted relative import with no known parent package

# In .claude/skills/bk-track/scripts/status_analyzer.py (line 10)
from ..common.backlog.client import BacklogClient
# ❌ ImportError: attempted relative import with no known parent package
```

### Why It Happens
- Pytest runs from: `c:\Users\duongbibo\brse-workspace`
- Tests try to import from: `..\..\..\lib\vault` (relative path)
- Python can't resolve relative imports when module is not properly nested

---

## Solution Approaches

### Approach 1: Fix conftest.py (Quick Fix) ⚡
Add sys.path manipulation in conftest.py to make modules discoverable

**Location:** `.claude/skills/bk-recall/tests/conftest.py` (already exists)

**Change:**
```python
# Add at top of file
import sys
from pathlib import Path

# Add parent directories to path
skills_root = Path(__file__).parent.parent
sys.path.insert(0, str(skills_root))
sys.path.insert(0, str(skills_root.parent / "lib"))  # For lib.vault
sys.path.insert(0, str(skills_root.parent / "common"))  # For common modules
```

**Pros:** Quick, doesn't change source code
**Cons:** Temporary workaround, not ideal for production

---

### Approach 2: Convert to Absolute Imports (Recommended) ✅
Update source files to use absolute imports instead of relative imports

**Example Conversion:**

```python
# BEFORE (relative import - fails)
from ..lib.vault import VaultSearch, VaultStore, VaultItem
from ..lib.vault.embedder import GeminiEmbedder

# AFTER (absolute import - works)
from lib.vault import VaultSearch, VaultStore, VaultItem
from lib.vault.embedder import GeminiEmbedder

# OR with full path
from .claude.skills.lib.vault import VaultSearch
from .claude.skills.lib.vault.embedder import GeminiEmbedder
```

**Pros:** Clean, production-ready, standard Python practice
**Cons:** Requires editing multiple files

---

### Approach 3: Restructure as Proper Python Packages
Add `__init__.py` files to create proper package structure

**Current Structure:**
```
.claude/skills/
├── bk-recall/
│   ├── scripts/
│   │   ├── summarizer.py
│   │   ├── sync_manager.py
│   │   └── sources/
│   └── tests/
│       └── conftest.py
└── lib/
    └── vault/
        └── __init__.py  (exists)
```

**Needed Structure:**
```
.claude/skills/
├── __init__.py  (NEW - empty file)
├── bk-recall/
│   ├── __init__.py  (NEW - empty file)
│   ├── scripts/
│   │   ├── __init__.py  (NEW - empty file)
│   │   ├── summarizer.py
│   │   ├── sync_manager.py
│   │   └── sources/
│   │       └── __init__.py  (NEW - empty file)
│   └── tests/
│       ├── __init__.py  (NEW - empty file)
│       └── conftest.py
└── lib/
    ├── __init__.py  (NEW - empty file)
    └── vault/
        └── __init__.py  (exists)
```

**Pros:** Standard Python best practice
**Cons:** Requires more changes

---

## Recommended Solution

**Use Approach 1 + Approach 2:**
1. Quick fix with conftest.py (Approach 1) to get tests running immediately
2. Refactor to absolute imports (Approach 2) for long-term solution

---

## Implementation Steps

### STEP 1: Analyze Current Imports

**Phase 1 (bk-recall):**
```bash
cd /c/Users/duongbibo/brse-workspace
grep -r "from \.\." .claude/skills/bk-recall/scripts/ 2>/dev/null | head -20
grep -r "import.*from" .claude/skills/bk-recall/tests/ 2>/dev/null | head -20
```

**Phase 2 (bk-track):**
```bash
grep -r "from \.\." .claude/skills/bk-track/scripts/ 2>/dev/null | head -20
grep -r "import.*from" .claude/skills/bk-track/tests/ 2>/dev/null | head -20
```

### STEP 2: Quick Fix - Update conftest.py Files

**File 1: `.claude/skills/bk-recall/tests/conftest.py`**

Add this at the top:
```python
import sys
from pathlib import Path

# Add skills directory to path for imports
SKILLS_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_ROOT))
sys.path.insert(0, str(SKILLS_ROOT / "lib"))
```

**File 2: `.claude/skills/bk-track/tests/conftest.py`**

Add this at the top:
```python
import sys
from pathlib import Path

# Add skills directory to path for imports
SKILLS_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_ROOT))
sys.path.insert(0, str(SKILLS_ROOT / "common"))
sys.path.insert(0, str(SKILLS_ROOT / "lib"))
```

### STEP 3: Verify Tests Pass

```bash
cd /c/Users/duongbibo/brse-workspace

# Test Phase 1
.claude/skills/.venv/Scripts/python.exe -m pytest .claude/skills/bk-recall/tests/ -v --tb=short

# Test Phase 2
.claude/skills/.venv/Scripts/python.exe -m pytest .claude/skills/bk-track/tests/ -v --tb=short
```

### STEP 4: Long-term Fix - Convert to Absolute Imports

**Files to Update:**

Phase 1 (bk-recall):
- `.claude/skills/bk-recall/scripts/summarizer.py`
- `.claude/skills/bk-recall/scripts/sync_manager.py`
- `.claude/skills/bk-recall/scripts/sources/email_sync.py`
- `.claude/skills/bk-recall/scripts/sources/slack_sync.py`
- `.claude/skills/bk-recall/scripts/sources/backlog_sync.py`

Phase 2 (bk-track):
- `.claude/skills/bk-track/scripts/status_analyzer.py`
- `.claude/skills/bk-track/scripts/report_generator.py`
- `.claude/skills/bk-track/scripts/formatters/markdown_formatter.py`
- `.claude/skills/bk-track/scripts/formatters/pptx_formatter.py`

**Conversion Pattern:**

Before:
```python
from ..lib.vault import VaultSearch, VaultStore
from ..common.backlog.client import BacklogClient
from ..lib.vault.embedder import GeminiEmbedder
```

After:
```python
from lib.vault import VaultSearch, VaultStore
from common.backlog.client import BacklogClient
from lib.vault.embedder import GeminiEmbedder
```

### STEP 5: Add Missing Imports

**File: `.claude/skills/bk-recall/scripts/sources/email_sync.py`**

Add after other imports:
```python
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
```

**File: `.claude/skills/bk-recall/scripts/sources/slack_sync.py`**

Add after other imports:
```python
from slack_sdk import WebClient
```

### STEP 6: Final Verification

```bash
cd /c/Users/duongbibo/brse-workspace

# Run all phase tests
.claude/skills/.venv/Scripts/python.exe -m pytest .claude/skills/lib/vault/tests/ -v
.claude/skills/.venv/Scripts/python.exe -m pytest .claude/skills/bk-recall/tests/ -v
.claude/skills/.venv/Scripts/python.exe -m pytest .claude/skills/bk-track/tests/ -v
.claude/skills/.venv/Scripts/python.exe -m pytest .claude/skills/bk-init/tests/ -v
.claude/skills/.venv/Scripts/python.exe -m pytest .claude/skills/bk-capture/tests/ -v
```

---

## Expected Results After Fix

### Phase 1 (bk-recall)
**Current:** 35 passed, 28 failed
**Expected:** 60+ passed, 3 failed (remaining failures are assertion issues, not import)

### Phase 2 (bk-track)
**Current:** 55 passed, 36 failed
**Expected:** 85+ passed, 6 failed (remaining failures are minor issues)

### Combined Test Suite
**Current:** 159 passed, 64 failed (59 import-related)
**Expected:** 200+ passed, 5 failed (real logic issues)

---

## Files to Modify

### Quick Fix Only (5 minutes)
```
✏️  .claude/skills/bk-recall/tests/conftest.py
✏️  .claude/skills/bk-track/tests/conftest.py
```

### Complete Fix (1-2 hours)
```
✏️  .claude/skills/bk-recall/scripts/summarizer.py
✏️  .claude/skills/bk-recall/scripts/sync_manager.py
✏️  .claude/skills/bk-recall/scripts/sources/email_sync.py
✏️  .claude/skills/bk-recall/scripts/sources/slack_sync.py
✏️  .claude/skills/bk-recall/scripts/sources/backlog_sync.py
✏️  .claude/skills/bk-track/scripts/status_analyzer.py
✏️  .claude/skills/bk-track/scripts/report_generator.py
✏️  .claude/skills/bk-track/scripts/formatters/markdown_formatter.py
✏️  .claude/skills/bk-track/scripts/formatters/pptx_formatter.py
```

---

## Verification Checklist

After implementing fix, verify:

- [ ] Phase 1 tests run without import errors
- [ ] Phase 2 tests run without import errors
- [ ] Tests can import from lib.vault
- [ ] Tests can import from common.backlog
- [ ] Gmail imports work (if credentials available)
- [ ] Slack imports work (if SDK installed)
- [ ] All 56 Phase 0 tests still pass
- [ ] All 99 Phase 5 tests still pass
- [ ] All 4 Phase 3 tests still pass
- [ ] Coverage above 80% for critical modules

---

## Time Estimate

| Step | Time | Notes |
|------|------|-------|
| 1. Analyze imports | 10 min | Quick grep analysis |
| 2. Update conftest.py | 5 min | 2 files to edit |
| 3. Verify tests run | 2 min | Pytest execution |
| 4-5. Convert to absolute imports | 45 min | 9 files, ~3-5 lines each |
| 6. Final verification | 5 min | Run full test suite |
| **TOTAL** | **~70 minutes** | Can be done in 1-2 hours |

---

## Rollback Plan

If changes break something:
```bash
# Revert all changes
git checkout .

# Re-run tests
.claude/skills/.venv/Scripts/python.exe -m pytest .claude/skills/lib/vault/tests/ -v
```

---

## Related Documentation

- Main Report: `tester-260130-0957-brsekit-v2-test-execution.md`
- Test Plan: `plans/reports/tester-260130-0907-brsekit-v2-test-plan.md`
- Source Code: `.claude/skills/bk-recall/scripts/` and `.claude/skills/bk-track/scripts/`

---

## Status Tracking

- [ ] Analyze imports (Step 1)
- [ ] Update conftest.py (Step 2)
- [ ] Verify tests pass with quick fix (Step 3)
- [ ] Convert to absolute imports (Step 4)
- [ ] Add missing imports (Step 5)
- [ ] Final verification (Step 6)
- [ ] Document results in test execution report

---

*Report Generated: 2026-01-30 09:57 AM*
*Severity: P0 - CRITICAL*
*Status: Ready for implementation*
