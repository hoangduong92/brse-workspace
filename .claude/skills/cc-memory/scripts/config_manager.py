"""Configuration manager for memory settings."""
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add script dir to path
sys.path.insert(0, str(Path(__file__).parent))

from memory_db import MemoryDB

# Default configuration
DEFAULT_CONFIG = {
    "auto_extract": True,
    "extract_method": "hybrid",  # heuristic, gemini, hybrid
    "min_session_messages": 5,  # Skip short sessions
    "max_facts_loaded": 50,  # Max facts in context
    "gemini_threshold_messages": 20,  # Use Gemini for longer sessions
    "fact_categories": [
        "preference",    # User preferences
        "decision",      # Architectural/design decisions
        "requirement",   # Project requirements
        "context",       # General context
        "use_case",      # Use cases discussed
        "insight"        # Key insights
    ],
    "importance_keywords": {
        "decision": ["decided", "decision", "chose", "choice", "selected"],
        "requirement": ["must", "should", "requirement", "needs to", "required"],
        "preference": ["prefer", "preference", "like", "dislike", "want"],
        "use_case": ["use case", "scenario", "example", "when user"],
        "insight": ["learned", "realized", "important", "key insight"]
    }
}


class ConfigManager:
    """Manage memory configuration."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config manager."""
        self.config_path = config_path or (MemoryDB.get_memory_dir() / "config.json")
        self._config: Optional[Dict[str, Any]] = None

    def load(self) -> Dict[str, Any]:
        """Load configuration, creating defaults if needed."""
        if self._config is not None:
            return self._config

        if self.config_path.exists():
            try:
                with open(self.config_path, encoding="utf-8") as f:
                    user_config = json.load(f)
                # Merge with defaults (user config takes precedence)
                self._config = {**DEFAULT_CONFIG, **user_config}
            except json.JSONDecodeError:
                self._config = DEFAULT_CONFIG.copy()
        else:
            self._config = DEFAULT_CONFIG.copy()
            self.save(self._config)  # Create default config file

        return self._config

    def save(self, config: Optional[Dict[str, Any]] = None):
        """Save configuration to file."""
        if config is not None:
            self._config = config

        if self._config is None:
            return

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.load().get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value and save."""
        config = self.load()
        config[key] = value
        self.save(config)

    def reset(self):
        """Reset to default configuration."""
        self._config = DEFAULT_CONFIG.copy()
        self.save(self._config)

    def get_importance_keywords(self) -> Dict[str, list]:
        """Get importance keywords for fact extraction."""
        return self.get("importance_keywords", DEFAULT_CONFIG["importance_keywords"])

    def get_fact_categories(self) -> list:
        """Get list of fact categories."""
        return self.get("fact_categories", DEFAULT_CONFIG["fact_categories"])
