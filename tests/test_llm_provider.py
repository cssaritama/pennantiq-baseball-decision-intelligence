import pytest

from src.pennantiq.llm_provider import call_llm


def test_github_models_requires_token(monkeypatch):
    for name in ("GITHUB_MODELS_TOKEN", "GITHUB_TOKEN", "GH_TOKEN"):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(RuntimeError, match="GitHub Models requires"):
        call_llm("test", provider="github")
