"""Core LangChain agent that generates LinkedIn posts using Google Gemini."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI

from .prompts import build_prompt

DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_TEMPERATURE = 0.7


@dataclass
class PostRequest:
    """Inputs for generating a LinkedIn post."""

    topic: str
    language: str = "English"
    tone: Optional[str] = None
    audience: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.topic or not self.topic.strip():
            raise ValueError("topic must be a non-empty string")
        if not self.language or not self.language.strip():
            raise ValueError("language must be a non-empty string")
        self.topic = self.topic.strip()
        self.language = self.language.strip()


class LinkedInPostAgent:
    """A LangChain-powered agent that writes professional LinkedIn posts.

    The agent wires a chat prompt template to Google's Gemini LLM via LCEL:
        prompt | llm | output_parser
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        api_key: Optional[str] = None,
    ) -> None:
        self.model = model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
        self.temperature = (
            temperature
            if temperature is not None
            else float(os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE))
        )
        # Accept either GOOGLE_API_KEY or GEMINI_API_KEY for convenience.
        self.api_key = (
            api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        )

        if not self.api_key:
            raise EnvironmentError(
                "GOOGLE_API_KEY is not set. Add it to your environment or a .env file."
            )

        self.chain: Runnable = self._build_chain()

    def _build_chain(self) -> Runnable:
        llm = ChatGoogleGenerativeAI(
            model=self.model,
            temperature=self.temperature,
            google_api_key=self.api_key,
        )
        prompt = build_prompt()
        return prompt | llm | StrOutputParser()

    @staticmethod
    def _format_inputs(request: PostRequest) -> dict:
        tone_line = f"Tone: {request.tone}\n" if request.tone else ""
        audience_line = (
            f"Target audience: {request.audience}\n" if request.audience else ""
        )
        return {
            "topic": request.topic,
            "language": request.language,
            "tone_line": tone_line,
            "audience_line": audience_line,
        }

    def generate(self, request: PostRequest) -> str:
        """Generate a LinkedIn post for the given request."""
        result = self.chain.invoke(self._format_inputs(request))
        return result.strip()

    def generate_post(
        self,
        topic: str,
        language: str = "English",
        tone: Optional[str] = None,
        audience: Optional[str] = None,
    ) -> str:
        """Convenience wrapper that builds a PostRequest and generates a post."""
        request = PostRequest(
            topic=topic, language=language, tone=tone, audience=audience
        )
        return self.generate(request)
