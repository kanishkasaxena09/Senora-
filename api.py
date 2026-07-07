"""
Groq API client — model registry, LLM calls, vision calls, and safe JSON parsing.
"""

import os
import json
from typing import List, Dict, Optional

import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ── Model Registry ──────────────────────────────────────────────
GROQ_MODELS: Dict[str, str] = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Llama 4 Scout": "meta-llama/llama-4-scout-17b-16e-instruct",
    "GPT-OSS 20B": "openai/gpt-oss-20b",
    "GPT-OSS 120B": "openai/gpt-oss-120b",
    "Qwen 3.6 27B": "qwen/qwen3.6-27b",
    "Llama 3.1 8B": "llama-3.1-8b-instant",
    "GPT-OSS Safeguard 20B": "openai/gpt-oss-safeguard-20b",
}

DEFAULT_MODEL = "llama-3.3-70b-versatile"

VISION_MODELS = [
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "qwen/qwen3.6-27b",
]


# ── Client ──────────────────────────────────────────────────────
@st.cache_resource
def get_groq_client() -> Optional[Groq]:
    """Return a cached Groq client, or None if no API key is available."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except (KeyError, FileNotFoundError):
            pass
    return Groq(api_key=api_key) if api_key else None


# ── Text completion ─────────────────────────────────────────────
def call_groq(
    messages: List[Dict],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    stream: bool = False,
    response_format: Optional[Dict] = None,
) -> str:
    """Send a chat-completion request and return the text response."""
    client = get_groq_client()
    if not client:
        return "⚠️ API key not found. Set `GROQ_API_KEY` in your `.env` file."
    try:
        kwargs: Dict = {
            "messages": messages,
            "model": model or DEFAULT_MODEL,
            "temperature": temperature,
            "max_completion_tokens": max_tokens,
            "stream": stream,
        }
        if response_format:
            kwargs["response_format"] = response_format
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    except Exception as exc:
        return f"API Error: {exc}"


# ── Vision completion ───────────────────────────────────────────
def call_groq_vision(
    image_url: str,
    prompt: str,
    model: str = "meta-llama/llama-4-scout-17b-16e-instruct",
) -> str:
    """Send an image + text prompt to a vision-capable model."""
    client = get_groq_client()
    if not client:
        return "⚠️ API key not found."
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            max_completion_tokens=2048,
            temperature=0.5,
        )
        return response.choices[0].message.content
    except Exception as exc:
        return f"Vision API Error: {exc}"


# ── Safe JSON parsing ──────────────────────────────────────────
def parse_json_response(text: str) -> Optional[dict | list]:
    """
    Try to extract and parse JSON from an LLM response.
    Handles markdown code-fences, plain JSON, and dict-wrapped arrays.
    Returns None on failure.
    """
    if not text or text.startswith("API Error") or text.startswith("⚠️"):
        return None

    # Strip markdown code fences if present
    cleaned = text
    if "```" in cleaned:
        cleaned = cleaned.split("```json")[-1].split("```")[0]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        return None


def extract_cards_from_json(data) -> List[Dict]:
    """
    Given parsed JSON (list or dict), extract a list of flashcard dicts.
    Handles: raw list, {"flashcards": [...]}, {"cards": [...]}.
    """
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("flashcards", "cards", "items", "data"):
            if key in data and isinstance(data[key], list):
                return data[key]
    return []
