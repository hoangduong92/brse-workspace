"""Extract memorable facts from conversation transcripts."""
import json
import re
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Add script dir to path
sys.path.insert(0, str(Path(__file__).parent))

from memory_store import Fact
from config_manager import ConfigManager

# Try to import Gemini for smart extraction
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


@dataclass
class ExtractionResult:
    """Result of fact extraction."""
    facts: List[Fact]
    method: str  # heuristic, gemini, hybrid
    session_summary: Optional[str] = None


class FactExtractor:
    """Extract memorable facts from conversation content."""

    def __init__(self, config: Optional[ConfigManager] = None):
        """Initialize extractor with config."""
        self.config = config or ConfigManager()
        self._genai_configured = False

    def extract(
        self,
        content: str,
        session_id: Optional[str] = None,
        method: Optional[str] = None
    ) -> ExtractionResult:
        """Extract facts from conversation content."""
        method = method or self.config.get("extract_method", "hybrid")

        if method == "gemini" and self._can_use_gemini():
            return self._extract_with_gemini(content, session_id)
        elif method == "hybrid" and self._can_use_gemini():
            # Use heuristics first, then enhance with Gemini
            heuristic_result = self._extract_with_heuristics(content, session_id)
            if len(content) > 5000:  # Only use Gemini for longer content
                gemini_result = self._extract_with_gemini(content, session_id)
                return self._merge_results(heuristic_result, gemini_result)
            return heuristic_result
        else:
            return self._extract_with_heuristics(content, session_id)

    def _can_use_gemini(self) -> bool:
        """Check if Gemini is available and configured."""
        if not GENAI_AVAILABLE:
            return False

        if not self._genai_configured:
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self._genai_configured = True
            else:
                return False

        return True

    def _extract_with_heuristics(
        self,
        content: str,
        session_id: Optional[str] = None
    ) -> ExtractionResult:
        """Extract facts using keyword patterns."""
        facts = []
        keywords = self.config.get_importance_keywords()

        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', content)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20 or len(sentence) > 500:
                continue

            # Check each category's keywords
            for category, kw_list in keywords.items():
                for keyword in kw_list:
                    if keyword.lower() in sentence.lower():
                        # Calculate confidence based on keyword match quality
                        confidence = 0.7 if keyword in sentence else 0.5

                        # Clean up the sentence
                        clean_content = self._clean_fact(sentence)
                        if clean_content and len(clean_content) > 15:
                            facts.append(Fact(
                                id=None,  # Will be generated on save
                                content=clean_content,
                                source_session=session_id,
                                confidence=confidence,
                                category=category
                            ))
                        break  # One category per sentence

        # Deduplicate similar facts
        facts = self._deduplicate_facts(facts)

        return ExtractionResult(
            facts=facts,
            method="heuristic",
            session_summary=self._generate_summary_heuristic(content)
        )

    def _extract_with_gemini(
        self,
        content: str,
        session_id: Optional[str] = None
    ) -> ExtractionResult:
        """Extract facts using Gemini LLM."""
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")

            prompt = f"""Analyze this conversation and extract key memorable facts.

For each fact, identify:
1. The fact itself (concise, actionable statement)
2. Category: one of [preference, decision, requirement, context, use_case, insight]
3. Confidence: 0.0-1.0 based on how clearly stated

Also provide a brief 1-2 sentence summary of the conversation.

Respond in JSON format:
{{
  "summary": "...",
  "facts": [
    {{"content": "...", "category": "...", "confidence": 0.8}},
    ...
  ]
}}

Conversation:
{content[:10000]}  # Limit to avoid token limits
"""

            response = model.generate_content(prompt)
            result_text = response.text

            # Parse JSON response
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                data = json.loads(json_match.group())

                facts = []
                for f in data.get("facts", []):
                    facts.append(Fact(
                        id=None,
                        content=f.get("content", ""),
                        source_session=session_id,
                        confidence=float(f.get("confidence", 0.8)),
                        category=f.get("category", "context")
                    ))

                return ExtractionResult(
                    facts=facts,
                    method="gemini",
                    session_summary=data.get("summary")
                )

        except Exception as e:
            # Fallback to heuristics on any error
            pass

        return self._extract_with_heuristics(content, session_id)

    def _merge_results(
        self,
        heuristic: ExtractionResult,
        gemini: ExtractionResult
    ) -> ExtractionResult:
        """Merge heuristic and Gemini results."""
        # Combine facts, preferring Gemini for duplicates
        all_facts = gemini.facts.copy()

        # Add heuristic facts not covered by Gemini
        gemini_contents = {f.content.lower()[:50] for f in gemini.facts}
        for fact in heuristic.facts:
            if fact.content.lower()[:50] not in gemini_contents:
                all_facts.append(fact)

        return ExtractionResult(
            facts=self._deduplicate_facts(all_facts),
            method="hybrid",
            session_summary=gemini.session_summary or heuristic.session_summary
        )

    def _clean_fact(self, text: str) -> str:
        """Clean and normalize a fact string."""
        # Remove common prefixes
        text = re.sub(r'^(user:|assistant:|human:|ai:)\s*', '', text, flags=re.I)
        # Remove markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _deduplicate_facts(self, facts: List[Fact]) -> List[Fact]:
        """Remove duplicate or very similar facts."""
        seen = set()
        unique = []

        for fact in facts:
            # Use first 50 chars as dedup key
            key = fact.content.lower()[:50]
            if key not in seen:
                seen.add(key)
                unique.append(fact)

        return unique

    def _generate_summary_heuristic(self, content: str) -> str:
        """Generate a simple summary using heuristics."""
        # Extract first substantial paragraph or sentences
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        if not lines:
            return "No content"

        # Find lines that look like topics
        topics = []
        for line in lines[:20]:  # Check first 20 lines
            if any(kw in line.lower() for kw in ['implement', 'create', 'build', 'fix', 'add', 'update']):
                topics.append(line[:100])
                if len(topics) >= 3:
                    break

        if topics:
            return "Topics: " + "; ".join(topics)

        return lines[0][:200] if lines else "Conversation"
