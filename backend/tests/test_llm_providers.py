import httpx

from app.services import llm_service
from app.services.llm_service import (
    FallbackProvider,
    GeminiProvider,
    MockLLMProvider,
    OpenAIProvider,
    parse_json_object,
)
from app.services.profile_service import PROFILE_SCHEMA_HINT, extract_profile_from_text


def _with_transport(provider, handler):
    provider._client = httpx.Client(
        base_url=str(provider._client.base_url),
        headers=provider._client.headers,
        transport=httpx.MockTransport(handler),
    )
    return provider


def test_parse_json_object_handles_fences_and_prose():
    assert parse_json_object('{"age": 20}') == {"age": 20}
    assert parse_json_object('```json\n{"age": 20}\n```') == {"age": 20}
    assert parse_json_object('Here you go: {"age": 20} thanks') == {"age": 20}
    assert parse_json_object("not json") == {}
    assert parse_json_object("[1, 2]") == {}


def test_gemini_structured_output_request_and_parsing():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["key"] = request.headers["x-goog-api-key"]
        seen["body"] = request.content.decode()
        return httpx.Response(
            200,
            json={"candidates": [{"content": {"parts": [{"text": '{"age": 30, "state": "Kerala"}'}]}}]},
        )

    provider = _with_transport(GeminiProvider("test-key", "gemini-2.5-flash"), handler)
    result = provider.structured_output("I am 30 from Kerala", PROFILE_SCHEMA_HINT)

    assert result == {"age": 30, "state": "Kerala"}
    assert seen["url"].endswith("/models/gemini-2.5-flash:generateContent")
    assert seen["key"] == "test-key"
    assert "application/json" in seen["body"]


def test_openai_structured_output_parsing():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json={"choices": [{"message": {"content": '{"occupation": "farmer"}'}}]}
        )

    provider = _with_transport(OpenAIProvider("test-key", "gpt-4o-mini"), handler)
    assert provider.structured_output("I am a farmer", PROFILE_SCHEMA_HINT) == {"occupation": "farmer"}


def test_fallback_provider_uses_mock_when_primary_fails():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "bad key"})

    failing = _with_transport(GeminiProvider("bad", "gemini-2.5-flash"), handler)
    provider = FallbackProvider(failing, MockLLMProvider(), "gemini")
    result = provider.structured_output("I am a 45 year old farmer from Tamil Nadu", PROFILE_SCHEMA_HINT)
    assert result["age"] == 45
    assert result["occupation"] == "farmer"


def test_get_llm_provider_selection(monkeypatch):
    from app.config import Settings

    def build(**env):
        monkeypatch.setattr(llm_service, "_provider_instance", None)
        monkeypatch.setattr(llm_service, "get_settings", lambda: Settings(_env_file=None, **env))
        return llm_service.get_llm_provider()

    assert isinstance(build(llm_provider="mock"), MockLLMProvider)
    # a real provider without a key degrades to the mock instead of crashing
    assert isinstance(build(llm_provider="gemini"), MockLLMProvider)
    gemini = build(llm_provider="gemini", llm_api_key="k")
    assert isinstance(gemini, FallbackProvider) and isinstance(gemini._primary, GeminiProvider)
    assert gemini._primary._model == "gemini-2.5-flash"
    openai = build(llm_provider="openai", llm_api_key="k", llm_model="gpt-4o")
    assert isinstance(openai._primary, OpenAIProvider) and openai._primary._model == "gpt-4o"


def test_extraction_cleans_llm_output(monkeypatch):
    class Messy(MockLLMProvider):
        def structured_output(self, prompt, schema_hint):
            return {
                "age": "34",
                "annual_income": "1,50,000",
                "student": "no",
                "state": " Kerala ",
                "land_ownership": "OWNED",
                "favourite_colour": "blue",
                "district": None,
                "family_size": "many",
            }

    monkeypatch.setattr(llm_service, "_provider_instance", Messy())
    profile = extract_profile_from_text("anything")
    assert profile == {
        "age": 34,
        "annual_income": 150000.0,
        "student": False,
        "state": "Kerala",
        "land_ownership": "owned",
    }
