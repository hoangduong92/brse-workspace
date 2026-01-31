# Phase 3: Knowledge Layer

## Priority: P2
## Status: pending
## Effort: 2h

## Overview

Implement glossary/knowledge fallback chain: project-specific → shared workspace.

## Key Insights

- Current bk-convert has `glossaries/default-it-terms.json`
- bk-translate has `glossary_manager.py` for term lookup
- Need fallback: `projects/{name}/glossary.json` → `knowledge/glossary-it-terms.json`

## Requirements

### Functional
- Shared glossary at `knowledge/glossary-it-terms.json`
- Project-specific glossary at `projects/{name}/glossary.json`
- Fallback chain: project → shared
- Merge terms with project taking precedence

### Non-functional
- Lazy loading (don't load until needed)
- Cache loaded glossaries
- Support multiple file formats (JSON, YAML)

## Architecture

```
knowledge/
└── glossary-it-terms.json      # Shared IT terms

projects/HB21373/
├── glossary.json               # Project-specific overrides
└── context.yaml                # May reference additional glossaries
```

## Implementation Steps

### 1. Create knowledge manager

```python
# .claude/skills/lib/knowledge_manager.py
"""Knowledge and glossary management with fallback chain."""
import json
from pathlib import Path
from typing import Optional, Dict, List
import yaml


class KnowledgeManager:
    """Manages glossaries with project → shared fallback."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or Path.cwd()
        self.knowledge_dir = self.workspace_root / "knowledge"
        self.projects_dir = self.workspace_root / "projects"
        self._cache: Dict[str, Dict] = {}

    def _load_json_or_yaml(self, path: Path) -> Dict:
        """Load JSON or YAML file."""
        if not path.exists():
            return {}

        cache_key = str(path)
        if cache_key in self._cache:
            return self._cache[cache_key]

        with open(path, encoding="utf-8") as f:
            if path.suffix in [".yaml", ".yml"]:
                data = yaml.safe_load(f) or {}
            else:
                data = json.load(f)

        self._cache[cache_key] = data
        return data

    def get_glossary(self, project: Optional[str] = None) -> Dict[str, str]:
        """Get merged glossary with project → shared fallback.

        Returns dict of {term: translation}.
        """
        result = {}

        # 1. Load shared glossary
        shared_path = self.knowledge_dir / "glossary-it-terms.json"
        shared = self._load_json_or_yaml(shared_path)
        if "terms" in shared:
            result.update(shared["terms"])
        else:
            result.update(shared)

        # 2. Load project-specific (overrides shared)
        if project:
            project_path = self.projects_dir / project / "glossary.json"
            project_glossary = self._load_json_or_yaml(project_path)
            if "terms" in project_glossary:
                result.update(project_glossary["terms"])
            else:
                result.update(project_glossary)

        return result

    def get_term(self, term: str, project: Optional[str] = None) -> Optional[str]:
        """Lookup single term with fallback."""
        glossary = self.get_glossary(project)
        # Try exact match first, then case-insensitive
        if term in glossary:
            return glossary[term]
        term_lower = term.lower()
        for key, value in glossary.items():
            if key.lower() == term_lower:
                return value
        return None

    def list_terms(self, project: Optional[str] = None, prefix: Optional[str] = None) -> List[str]:
        """List all terms, optionally filtered by prefix."""
        glossary = self.get_glossary(project)
        terms = list(glossary.keys())
        if prefix:
            terms = [t for t in terms if t.lower().startswith(prefix.lower())]
        return sorted(terms)

    def add_term(self, term: str, translation: str, project: str) -> None:
        """Add term to project glossary."""
        project_path = self.projects_dir / project / "glossary.json"

        # Load existing
        glossary = self._load_json_or_yaml(project_path)
        if "terms" not in glossary:
            glossary["terms"] = {}

        glossary["terms"][term] = translation

        # Save
        project_path.parent.mkdir(parents=True, exist_ok=True)
        with open(project_path, "w", encoding="utf-8") as f:
            json.dump(glossary, f, ensure_ascii=False, indent=2)

        # Invalidate cache
        cache_key = str(project_path)
        if cache_key in self._cache:
            del self._cache[cache_key]
```

### 2. Create default shared glossary

```json
// knowledge/glossary-it-terms.json
{
  "meta": {
    "name": "IT Terms Glossary",
    "version": "1.0",
    "description": "Shared IT terminology for BrseKit projects"
  },
  "terms": {
    "API": "API（Application Programming Interface）",
    "bug": "バグ",
    "deploy": "デプロイ",
    "feature": "機能",
    "fix": "修正",
    "frontend": "フロントエンド",
    "backend": "バックエンド",
    "database": "データベース",
    "server": "サーバー",
    "client": "クライアント",
    "user": "ユーザー",
    "login": "ログイン",
    "logout": "ログアウト",
    "password": "パスワード",
    "email": "メール",
    "notification": "通知",
    "setting": "設定",
    "profile": "プロフィール",
    "dashboard": "ダッシュボード",
    "report": "レポート",
    "export": "エクスポート",
    "import": "インポート",
    "upload": "アップロード",
    "download": "ダウンロード",
    "search": "検索",
    "filter": "フィルター",
    "sort": "並び替え",
    "pagination": "ページネーション",
    "cache": "キャッシュ",
    "session": "セッション",
    "token": "トークン",
    "authentication": "認証",
    "authorization": "認可",
    "permission": "権限",
    "role": "ロール",
    "admin": "管理者",
    "guest": "ゲスト"
  }
}
```

### 3. Update bk-convert to use KnowledgeManager

```python
# In bk-convert/scripts/glossary_manager.py:

from lib.knowledge_manager import KnowledgeManager

class GlossaryManager:
    def __init__(self, project: Optional[str] = None):
        self.km = KnowledgeManager()
        self.project = project

    def get_translation(self, term: str) -> Optional[str]:
        return self.km.get_term(term, self.project)

    def get_all_terms(self) -> Dict[str, str]:
        return self.km.get_glossary(self.project)
```

### 4. Update bk-translate to use KnowledgeManager

Similar integration pattern.

## Related Code Files

### Create
- `.claude/skills/lib/knowledge_manager.py`
- `knowledge/glossary-it-terms.json`

### Update
- `.claude/skills/bk-convert/scripts/glossary_manager.py`
- `.claude/skills/bk-translate/scripts/glossary_manager.py`

## Todo List

- [ ] Create `lib/knowledge_manager.py`
- [ ] Create `knowledge/glossary-it-terms.json` with common IT terms
- [ ] Update bk-convert to use KnowledgeManager
- [ ] Update bk-translate to use KnowledgeManager
- [ ] Write unit tests for KnowledgeManager

## Success Criteria

- [ ] `KnowledgeManager().get_glossary()` returns shared terms
- [ ] `KnowledgeManager().get_glossary("HB21373")` merges project + shared
- [ ] Project terms override shared terms
- [ ] bk-convert uses merged glossary

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Missing shared glossary | Low | Create with common terms |
| Glossary format mismatch | Medium | Support both flat and nested |
| Performance with large glossaries | Low | Cache loaded files |

## Next Steps

After Phase 3, proceed to [Phase 4: cc-memory Integration](./phase-04-cc-memory-integration.md).
