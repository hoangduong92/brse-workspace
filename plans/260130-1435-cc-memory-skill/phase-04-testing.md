# Phase 4: Testing

## Context Links
- Vault tests: `.claude/skills/lib/vault/tests/test_vault.py`
- bk-recall tests: `.claude/skills/bk-recall/tests/`

## Overview
- **Priority:** P2 (quality assurance)
- **Status:** pending
- **Effort:** 0.5h

Unit tests for memory infrastructure and integration tests for commands.

## Key Insights

1. Follow existing vault test patterns
2. Mock Gemini API for unit tests
3. Use temporary directories for DB tests
4. Test extraction heuristics thoroughly

## Requirements

### Unit Tests
- memory_db.py - Table creation, connections
- memory_store.py - CRUD operations
- fact_extractor.py - Heuristic patterns
- config_manager.py - Load/save config

### Integration Tests
- CLI commands end-to-end
- Fact extraction pipeline
- Search functionality

## Related Code Files

### Create
- `.claude/skills/cc-memory/tests/__init__.py`
- `.claude/skills/cc-memory/tests/conftest.py`
- `.claude/skills/cc-memory/tests/test_memory_db.py`
- `.claude/skills/cc-memory/tests/test_memory_store.py`
- `.claude/skills/cc-memory/tests/test_fact_extractor.py`
- `.claude/skills/cc-memory/tests/test_cli.py`
- `.claude/skills/cc-memory/pytest.ini`

## Implementation Steps

### Step 1: Create conftest.py

```python
"""Pytest fixtures for cc-memory tests."""
import pytest
import tempfile
from pathlib import Path
import sys
import os

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

@pytest.fixture
def temp_memory_dir(tmp_path):
    """Create temporary memory directory."""
    memory_dir = tmp_path / "claude_client" / "memory"
    memory_dir.mkdir(parents=True)
    return memory_dir

@pytest.fixture
def mock_db(temp_memory_dir, monkeypatch):
    """Initialize MemoryDB with temp directory."""
    from memory_db import MemoryDB

    db_path = temp_memory_dir / "vault.db"
    MemoryDB.initialize(db_path)

    # Patch get_memory_dir to return temp
    monkeypatch.setattr(MemoryDB, "get_memory_dir", lambda cls: temp_memory_dir)

    yield MemoryDB

    MemoryDB.close()

@pytest.fixture
def sample_transcript():
    """Sample JSONL transcript for testing."""
    return '''{"type":"user","message":{"content":[{"type":"text","text":"I prefer using TypeScript for this project"}]}}
{"type":"assistant","message":{"content":[{"type":"text","text":"Understood, I'll use TypeScript"}]}}
{"type":"user","message":{"content":[{"type":"text","text":"We decided to use PostgreSQL for the database"}]}}
{"type":"assistant","message":{"content":[{"type":"text","text":"I'll configure PostgreSQL connection"}]}}
{"type":"user","message":{"content":[{"type":"text","text":"Important: always use snake_case for DB columns"}]}}'''

@pytest.fixture
def mock_gemini(monkeypatch):
    """Mock Gemini API calls."""
    class MockResponse:
        text = '[{"content": "Test fact", "category": "preference", "confidence": 0.8}]'

    class MockModel:
        def generate_content(self, prompt):
            return MockResponse()

    import google.generativeai as genai
    monkeypatch.setattr(genai, "GenerativeModel", lambda name: MockModel())
    monkeypatch.setattr(genai, "configure", lambda api_key: None)
```

### Step 2: Create test_memory_db.py

```python
"""Tests for MemoryDB."""
import pytest
from memory_db import MemoryDB

class TestMemoryDB:

    def test_initialize_creates_tables(self, mock_db, temp_memory_dir):
        """Test database initialization creates required tables."""
        conn = mock_db.get_connection()
        cursor = conn.cursor()

        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}

        assert "memory_sessions" in tables
        assert "memory_facts" in tables
        assert "vault_items" in tables

    def test_get_memory_dir_returns_user_path(self):
        """Test memory dir is under user home."""
        from pathlib import Path
        dir_path = MemoryDB.get_memory_dir()
        assert "claude_client" in str(dir_path)
        assert "memory" in str(dir_path)

    def test_thread_safe_connection(self, mock_db):
        """Test connections are thread-local."""
        conn1 = mock_db.get_connection()
        conn2 = mock_db.get_connection()
        assert conn1 is conn2  # Same thread, same connection
```

### Step 3: Create test_memory_store.py

```python
"""Tests for MemoryStore."""
import pytest
from datetime import datetime
from memory_store import MemoryStore, Session, Fact

class TestMemoryStore:

    def test_add_session(self, mock_db):
        """Test adding a session."""
        store = MemoryStore()
        session = Session(
            session_id="test-123",
            workspace="/path/to/project",
            start_time=datetime.now(),
            message_count=10
        )

        result = store.add_session(session)
        assert result == "test-123"

        sessions = store.get_recent_sessions(10)
        assert len(sessions) == 1
        assert sessions[0].session_id == "test-123"

    def test_add_fact(self, mock_db):
        """Test adding a fact."""
        store = MemoryStore()
        fact = Fact(
            id=None,
            content="User prefers dark mode",
            category="preference",
            confidence=0.9
        )

        fact_id = store.add_fact(fact)
        assert fact_id is not None

        facts = store.get_all_facts()
        assert len(facts) == 1
        assert "dark mode" in facts[0].content

    def test_delete_fact(self, mock_db):
        """Test deleting a fact."""
        store = MemoryStore()
        fact = Fact(id="del-123", content="To delete", category="test")
        store.add_fact(fact)

        result = store.delete_fact("del-123")
        assert result is True

        facts = store.get_all_facts()
        assert len(facts) == 0

    def test_delete_nonexistent_fact(self, mock_db):
        """Test deleting non-existent fact returns False."""
        store = MemoryStore()
        result = store.delete_fact("nonexistent")
        assert result is False
```

### Step 4: Create test_fact_extractor.py

```python
"""Tests for fact extraction."""
import pytest
from fact_extractor import FactExtractor, FACT_PATTERNS

class TestFactExtractor:

    def test_extract_preferences(self, mock_db, sample_transcript):
        """Test extracting preference facts."""
        extractor = FactExtractor()
        facts = extractor.extract_heuristic(sample_transcript)

        # Should find "prefer using TypeScript"
        preference_facts = [f for f in facts if f.category == "preference"]
        assert len(preference_facts) >= 1
        assert any("TypeScript" in f.content for f in preference_facts)

    def test_extract_decisions(self, mock_db, sample_transcript):
        """Test extracting decision facts."""
        extractor = FactExtractor()
        facts = extractor.extract_heuristic(sample_transcript)

        # Should find "decided to use PostgreSQL"
        decision_facts = [f for f in facts if f.category == "decision"]
        assert len(decision_facts) >= 1
        assert any("PostgreSQL" in f.content for f in decision_facts)

    def test_extract_requirements(self, mock_db, sample_transcript):
        """Test extracting requirement facts."""
        extractor = FactExtractor()
        facts = extractor.extract_heuristic(sample_transcript)

        # Should find "always use snake_case"
        req_facts = [f for f in facts if f.category == "requirement"]
        assert len(req_facts) >= 1

    def test_deduplication(self, mock_db):
        """Test duplicate facts are removed."""
        extractor = FactExtractor()
        transcript = '''{"type":"user","message":{"content":[{"type":"text","text":"I prefer TypeScript"}]}}
{"type":"user","message":{"content":[{"type":"text","text":"I prefer TypeScript for everything"}]}}'''

        facts = extractor.extract_heuristic(transcript)
        # Similar facts should be deduplicated
        typescript_facts = [f for f in facts if "TypeScript" in f.content]
        assert len(typescript_facts) <= 1

    def test_gemini_extraction(self, mock_db, sample_transcript, mock_gemini):
        """Test Gemini-based extraction."""
        extractor = FactExtractor()
        facts = extractor.extract_gemini(sample_transcript, "test-session")

        assert len(facts) >= 1
        assert facts[0].content == "Test fact"
```

### Step 5: Create pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short
filterwarnings =
    ignore::DeprecationWarning
```

## Todo List

- [ ] Create conftest.py with fixtures
- [ ] Create test_memory_db.py
- [ ] Create test_memory_store.py
- [ ] Create test_fact_extractor.py
- [ ] Create test_cli.py for integration tests
- [ ] Create pytest.ini
- [ ] Run tests and fix failures

## Success Criteria

- [ ] All unit tests pass
- [ ] Test coverage >80% for core modules
- [ ] Integration tests verify CLI commands
- [ ] Mocked Gemini tests work offline

## Test Commands

```bash
# Run all tests
cd .claude/skills/cc-memory
../.venv/Scripts/python.exe -m pytest

# Run with coverage
../.venv/Scripts/python.exe -m pytest --cov=scripts --cov-report=term-missing

# Run specific test file
../.venv/Scripts/python.exe -m pytest tests/test_memory_store.py -v
```
