"""Prompt builder for bk-spec - build Claude/Gemini prompts with context."""
from pathlib import Path
from typing import Dict, Optional


class PromptBuilder:
    """Build prompts for LLM analysis with context enrichment."""

    # Built-in templates for different task types
    TEMPLATES = {
        "analyze": """要件分析タスク

以下の要件を分析し、機能要件、非機能要件、曖昧な点を特定してください。

## 入力要件
{input_text}

{context_section}

## 出力形式
- 機能要件リスト
- 非機能要件リスト
- 曖昧な点と明確化が必要な質問
""",
        "test": """テストケース生成タスク

以下の要件に基づいて、テストケースを生成してください。

## 入力要件
{input_text}

{context_section}

## 出力形式
- テスト観点の抽出
- 具体的なテストケース（正常系、異常系、境界値）
- テスト優先順位
""",
        "story": """ユーザーストーリー生成タスク

以下の要件からユーザーストーリーを作成してください。

## 入力要件
{input_text}

{context_section}

## 出力形式
各ストーリーを以下の形式で記述：
- [役割]として、[機能]したい、なぜなら[理由]
- 受入基準
- 優先度
""",
        "gap": """ギャップ分析タスク

以下の要件を分析し、不足している情報やギャップを特定してください。

## 入力要件
{input_text}

{context_section}

## 出力形式
- 不足している要件
- 考慮すべき非機能要件
- リスクとその対策
""",
        "viewpoint": """テスト観点抽出タスク

以下の要件から、テスト観点を網羅的に抽出してください。

## 入力要件
{input_text}

{context_section}

## 出力形式
| 観点 | 詳細 | 優先度 |
|------|------|--------|
| ... | ... | ... |
"""
    }

    def __init__(self, template_dir: Optional[Path] = None):
        """Initialize prompt builder.

        Args:
            template_dir: Directory containing custom templates (optional)
        """
        self.template_dir = template_dir
        if template_dir and not template_dir.exists():
            template_dir.mkdir(parents=True, exist_ok=True)

    def build(
        self,
        task_type: str,
        input_text: str,
        context: Optional[Dict] = None
    ) -> str:
        """Build prompt for LLM.

        Args:
            task_type: "analyze", "test", "story", "gap", "viewpoint"
            input_text: User input/requirements
            context: Optional enriched context from ContextEnricher

        Returns:
            Formatted prompt string
        """
        # Load template
        template = self.load_template(task_type)

        # Build context section
        context_section = ""
        if context:
            context_section = self._build_context_section(context)

        # Inject variables into template
        prompt = template.format(
            input_text=input_text,
            context_section=context_section
        )

        return prompt

    def load_template(self, name: str) -> str:
        """Load prompt template from file or built-in.

        Args:
            name: Template name (analyze, test, story, gap, viewpoint)

        Returns:
            Template string
        """
        # Try to load from custom template directory
        if self.template_dir:
            template_file = self.template_dir / f"{name}.txt"
            if template_file.exists():
                return template_file.read_text(encoding="utf-8")

        # Fall back to built-in template
        template = self.TEMPLATES.get(name)
        if not template:
            raise ValueError(
                f"Template '{name}' not found. "
                f"Available: {', '.join(self.TEMPLATES.keys())}"
            )

        return template

    def _build_context_section(self, context: Dict) -> str:
        """Build context section from enriched context.

        Args:
            context: EnrichedContext dict with keywords and related_items

        Returns:
            Formatted context string
        """
        sections = []

        # Add keywords
        if context.get("keywords"):
            keywords_str = ", ".join(context["keywords"][:10])
            sections.append(f"## 関連キーワード\n{keywords_str}")

        # Add related items from vault
        if context.get("related_items"):
            sections.append("## 関連する過去の情報")
            for item in context["related_items"][:5]:
                title = item.get("title", "無題")
                source = item.get("source", "不明")
                score = item.get("score", 0)
                sections.append(
                    f"- [{source}] {title} (関連度: {score:.2f})"
                )

        # Add context summary
        if context.get("context_summary"):
            sections.append(f"\n## コンテキスト要約\n{context['context_summary']}")

        if sections:
            return "\n\n".join(sections)

        return ""

    def save_template(self, name: str, content: str) -> Path:
        """Save custom template to file.

        Args:
            name: Template name
            content: Template content

        Returns:
            Path to saved template file
        """
        if not self.template_dir:
            raise ValueError("template_dir not set")

        template_file = self.template_dir / f"{name}.txt"
        template_file.write_text(content, encoding="utf-8")
        return template_file

    def list_templates(self) -> Dict[str, str]:
        """List all available templates.

        Returns:
            Dict mapping template names to their sources (built-in/custom)
        """
        templates = {}

        # Built-in templates
        for name in self.TEMPLATES.keys():
            templates[name] = "built-in"

        # Custom templates
        if self.template_dir and self.template_dir.exists():
            for template_file in self.template_dir.glob("*.txt"):
                name = template_file.stem
                templates[name] = "custom"

        return templates
