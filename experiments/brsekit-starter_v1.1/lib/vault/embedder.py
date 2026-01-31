"""Gemini embedding wrapper with rate limit handling."""
import os
import time
from typing import List, Optional

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class GeminiEmbedder:
    """Gemini embedding API wrapper with rate limit handling."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize embedder with API key."""
        if not GENAI_AVAILABLE:
            raise ImportError(
                "google-generativeai not installed. "
                "Install with: pip install google-generativeai"
            )

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not set")

        genai.configure(api_key=self.api_key)
        self.model = "models/embedding-001"
        self.dimensions = 768

    def embed(self, text: str, retry_count: int = 3) -> List[float]:
        """Generate embedding for single text with retry logic."""
        for attempt in range(retry_count):
            try:
                result = genai.embed_content(
                    model=self.model,
                    content=text,
                    task_type="retrieval_document"
                )
                return result["embedding"]
            except Exception as e:
                if "quota" in str(e).lower() or "rate limit" in str(e).lower():
                    if attempt < retry_count - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        time.sleep(wait_time)
                        continue
                raise

        raise RuntimeError(f"Failed to embed after {retry_count} attempts")

    def embed_batch(
        self,
        texts: List[str],
        retry_count: int = 3
    ) -> List[List[float]]:
        """Generate embeddings for batch of texts."""
        embeddings = []
        for text in texts:
            embedding = self.embed(text, retry_count)
            embeddings.append(embedding)
            time.sleep(0.1)  # Rate limit protection
        return embeddings

    def embed_query(self, text: str, retry_count: int = 3) -> List[float]:
        """Generate embedding for query text."""
        for attempt in range(retry_count):
            try:
                result = genai.embed_content(
                    model=self.model,
                    content=text,
                    task_type="retrieval_query"
                )
                return result["embedding"]
            except Exception as e:
                if "quota" in str(e).lower() or "rate limit" in str(e).lower():
                    if attempt < retry_count - 1:
                        wait_time = 2 ** attempt
                        time.sleep(wait_time)
                        continue
                raise

        raise RuntimeError(f"Failed to embed query after {retry_count} attempts")
