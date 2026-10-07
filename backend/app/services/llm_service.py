"""LLM provider abstraction.

The LLM is used ONLY for: understanding natural language, extracting a
structured profile, generating follow-up questions, and phrasing
explanations/translations. It is NEVER the source of truth for scheme
existence, eligibility rules, documents, or URLs — those always come from
the verified scheme database (see scheme_service.py / rag_service.py).
"""
from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod

from app.config import get_settings

logger = logging.getLogger(__name__)

DEFAULT_MODELS = {"openai": "gpt-4o-mini", "gemini": "gemini-2.5-flash"}

EXTRACTION_INSTRUCTIONS = (
    "Extract a structured user profile as JSON from the user's message. The message may be in "
    "English, Hindi, or Tamil. Expected fields: {schema_hint}. "
    "Only include fields explicitly stated or clearly implied. Never invent values. "
    "Use English values (e.g. state names like \"Tamil Nadu\"). "
    "If the user says they farm on someone else's or family land, set land_ownership to "
    "\"family\", never \"owned\". Respond with a single JSON object only."
)


def parse_json_object(content: str) -> dict:
    """Parse an LLM reply into a dict, tolerating ```json fences and stray prose."""
    content = (content or "").strip()
    fenced = re.match(r"^```(?:json)?\s*(.*?)\s*```$", content, re.DOTALL | re.IGNORECASE)
    if fenced:
        content = fenced.group(1)
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        braces = re.search(r"\{.*\}", content, re.DOTALL)
        if not braces:
            return {}
        try:
            parsed = json.loads(braces.group(0))
        except json.JSONDecodeError:
            return {}
    return parsed if isinstance(parsed, dict) else {}


class LLMProvider(ABC):
    @abstractmethod
    def structured_output(self, prompt: str, schema_hint: str) -> dict:
        """Return a JSON-serializable dict extracted/derived from the prompt."""

    @abstractmethod
    def chat(self, prompt: str) -> str:
        """Return a free-text response."""


class MockLLMProvider(LLMProvider):
    """A deterministic, offline, heuristic LLM stand-in.

    It uses regex/keyword rules to extract profile fields from English,
    Hindi, and Tamil text so the whole application is runnable without any
    paid API key. Swap in OpenAIProvider (or another real provider) via
    LLM_PROVIDER env var for higher-quality extraction.
    """

    STATE_KEYWORDS = [
        "Tamil Nadu", "Kerala", "Karnataka", "Andhra Pradesh", "Telangana",
        "Maharashtra", "Gujarat", "Rajasthan", "Punjab", "Uttar Pradesh",
        "West Bengal", "Bihar", "Odisha", "Madhya Pradesh",
    ]

    TAMIL_STATE_MAP = {"தமிழ்நாடு": "Tamil Nadu"}

    HINDI_STATE_MAP = {
        "तमिलनाडु": "Tamil Nadu",
        "केरल": "Kerala",
        "कर्नाटक": "Karnataka",
        "आंध्र प्रदेश": "Andhra Pradesh",
        "तेलंगाना": "Telangana",
        "महाराष्ट्र": "Maharashtra",
        "गुजरात": "Gujarat",
        "राजस्थान": "Rajasthan",
        "पंजाब": "Punjab",
        "उत्तर प्रदेश": "Uttar Pradesh",
        "पश्चिम बंगाल": "West Bengal",
        "बिहार": "Bihar",
        "ओडिशा": "Odisha",
        "मध्य प्रदेश": "Madhya Pradesh",
    }

    def structured_output(self, prompt: str, schema_hint: str) -> dict:
        text = prompt
        profile: dict = {}

        # age — Hindi speakers commonly still write the number in Latin
        # digits (e.g. "मैं 20 साल का हूं"), so only the unit word varies.
        m = re.search(r"(\d{1,3})\s*(?:years? old|year-old|yrs?|வயது|साल|वर्ष)", text, re.IGNORECASE)
        if m:
            profile["age"] = int(m.group(1))
        else:
            m2 = re.search(r"\bage\s*(?:is|:)?\s*(\d{1,3})\b|उम्र\s*(\d{1,3})", text, re.IGNORECASE)
            if m2:
                profile["age"] = int(m2.group(1) or m2.group(2))

        # income (₹ / rs / lakh / लाख)
        m = re.search(
            r"(?:₹|rs\.?|rupees)?\s*([\d,]+(?:\.\d+)?)\s*(lakh|lakhs|lac|लाख)", text, re.IGNORECASE
        )
        if m:
            value = float(m.group(1).replace(",", "")) * 100000
            profile["annual_income"] = value
        else:
            m2 = re.search(r"(?:income|earn|salary|आय|वेतन|कमाता)[^\d]{0,15}([\d,]{4,9})", text, re.IGNORECASE)
            if m2:
                profile["annual_income"] = float(m2.group(1).replace(",", ""))

        # state
        for state in self.STATE_KEYWORDS:
            if state.lower() in text.lower():
                profile["state"] = state
                break
        for ta_state, en_state in self.TAMIL_STATE_MAP.items():
            if ta_state in text:
                profile["state"] = en_state
        for hi_state, en_state in self.HINDI_STATE_MAP.items():
            if hi_state in text:
                profile["state"] = en_state

        # student status
        if re.search(r"\bstudent\b|studying|engineering student|மாணவ|छात्र|पढ़ाई", text, re.IGNORECASE):
            profile["student"] = True
        if re.search(r"engineering|इंजीनियरिंग", text, re.IGNORECASE):
            profile["course"] = "engineering"

        # occupation: farmer
        if re.search(r"\bfarmer\b|\bfarming\b|\bfarm\b|agricult|விவசாயி|किसान|खेती|कृषि", text, re.IGNORECASE):
            profile["occupation"] = "farmer"
            if re.search(r"uncle|leased|lease|family land|father's land|relative|चाचा|पट्टे|पारिवारिक", text, re.IGNORECASE):
                profile["land_ownership"] = "family"
            elif re.search(r"own\s+(?:land|acre)|my land|I own|अपनी ज़मीन|अपनी जमीन|मेरी ज़मीन", text, re.IGNORECASE):
                profile["land_ownership"] = "owned"

        # land area
        m = re.search(r"(\d+(?:\.\d+)?)\s*(?:acres?|एकड़)", text, re.IGNORECASE)
        if m:
            profile["land_area_acres"] = float(m.group(1))

        # gender
        if re.search(r"\bwoman\b|\bwomen\b|\bfemale\b|I am a woman|महिला|औरत", text, re.IGNORECASE):
            profile["gender"] = "female"
        if re.search(r"\bman\b|\bmale\b|पुरुष", text, re.IGNORECASE) and "gender" not in profile:
            profile["gender"] = "male"

        # disability
        if re.search(r"disab|physically challenged|विकलांग|दिव्यांग", text, re.IGNORECASE):
            profile["disability_status"] = True

        # employment status
        if re.search(r"unemployed|बेरोज़गार|बेरोजगार", text, re.IGNORECASE):
            profile["employment_status"] = "unemployed"
        elif re.search(r"business owner|own business|entrepreneur|व्यवसायी|अपना व्यवसाय", text, re.IGNORECASE):
            profile["employment_status"] = "business owner"
        elif re.search(r"self.?employed|स्व.?रोजगार|स्व.?रोज़गार", text, re.IGNORECASE):
            profile["employment_status"] = "self-employed"

        # senior citizen keyword hint (doesn't set a field, age already captured)
        return profile

    def chat(self, prompt: str) -> str:
        # Deterministic canned fallback; real deployments should use a real provider.
        return "I can help you find government benefits. Could you tell me a bit more about your situation?"


class OpenAIProvider(LLMProvider):
    """Thin wrapper around the OpenAI chat completions API (httpx, no SDK needed)."""

    def __init__(self, api_key: str, model: str):
        import httpx

        self._client = httpx.Client(
            base_url="https://api.openai.com/v1",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0,
        )
        self._model = model

    def structured_output(self, prompt: str, schema_hint: str) -> dict:
        resp = self._client.post(
            "/chat/completions",
            json={
                "model": self._model,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": EXTRACTION_INSTRUCTIONS.format(schema_hint=schema_hint)},
                    {"role": "user", "content": prompt},
                ],
            },
        )
        resp.raise_for_status()
        return parse_json_object(resp.json()["choices"][0]["message"]["content"])

    def chat(self, prompt: str) -> str:
        resp = self._client.post(
            "/chat/completions",
            json={"model": self._model, "messages": [{"role": "user", "content": prompt}]},
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


class GeminiProvider(LLMProvider):
    """Google Gemini via the Generative Language REST API (httpx, no SDK needed)."""

    def __init__(self, api_key: str, model: str):
        import httpx

        self._client = httpx.Client(
            base_url="https://generativelanguage.googleapis.com/v1beta",
            headers={"x-goog-api-key": api_key},
            timeout=30.0,
        )
        self._model = model

    def _generate(self, body: dict) -> str:
        resp = self._client.post(f"/models/{self._model}:generateContent", json=body)
        resp.raise_for_status()
        parts = resp.json()["candidates"][0]["content"]["parts"]
        return "".join(part.get("text", "") for part in parts)

    def structured_output(self, prompt: str, schema_hint: str) -> dict:
        text = self._generate(
            {
                "systemInstruction": {
                    "parts": [{"text": EXTRACTION_INSTRUCTIONS.format(schema_hint=schema_hint)}]
                },
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json", "temperature": 0},
            }
        )
        return parse_json_object(text)

    def chat(self, prompt: str) -> str:
        return self._generate({"contents": [{"role": "user", "parts": [{"text": prompt}]}]})


class FallbackProvider(LLMProvider):
    """Wraps a real provider; if a call fails (bad key, quota, network), logs the
    reason and answers with the offline provider so the app keeps working."""

    def __init__(self, primary: LLMProvider, fallback: LLMProvider, name: str):
        self._primary = primary
        self._fallback = fallback
        self._name = name

    def structured_output(self, prompt: str, schema_hint: str) -> dict:
        try:
            return self._primary.structured_output(prompt, schema_hint)
        except Exception as exc:
            logger.warning("%s extraction failed (%s); using offline extractor.", self._name, exc)
            return self._fallback.structured_output(prompt, schema_hint)

    def chat(self, prompt: str) -> str:
        try:
            return self._primary.chat(prompt)
        except Exception as exc:
            logger.warning("%s chat failed (%s); using offline reply.", self._name, exc)
            return self._fallback.chat(prompt)


_provider_instance: LLMProvider | None = None


def get_llm_provider() -> LLMProvider:
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance

    settings = get_settings()
    name = settings.llm_provider.lower()
    if name in DEFAULT_MODELS and settings.llm_api_key:
        model = settings.llm_model or DEFAULT_MODELS[name]
        provider_cls = GeminiProvider if name == "gemini" else OpenAIProvider
        _provider_instance = FallbackProvider(
            provider_cls(settings.llm_api_key, model), MockLLMProvider(), name
        )
        logger.info("LLM provider: %s (%s)", name, model)
    else:
        if name in DEFAULT_MODELS:
            logger.warning("LLM_PROVIDER=%s but LLM_API_KEY is empty; using the offline mock provider.", name)
        elif name != "mock":
            logger.warning("Unknown LLM_PROVIDER '%s'; using the offline mock provider.", name)
        _provider_instance = MockLLMProvider()
    return _provider_instance