from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
import time


def call_llm(prompt: str, provider: str | None = None) -> tuple[str, str]:
    """Call a configured LLM provider and return (text, model_name).

    Supported providers:
    - gemini: Google Gemini via google-genai
    - openai: OpenAI Responses API
    - github: GitHub Models inference API (useful in GitHub Actions with GITHUB_TOKEN)
    """
    provider = (provider or os.getenv("LLM_PROVIDER", "mock")).lower()

    if provider == "gemini":
        from google import genai

        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text or "", model

    if provider == "openai":
        from openai import OpenAI

        model = os.getenv("OPENAI_MODEL", "gpt-5-mini")
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        return client.responses.create(model=model, input=prompt).output_text, model

    if provider == "github":
        token = (
            os.getenv("GITHUB_MODELS_TOKEN")
            or os.getenv("GITHUB_TOKEN")
            or os.getenv("GH_TOKEN")
        )
        if not token:
            raise RuntimeError(
                "GitHub Models requires GITHUB_MODELS_TOKEN, GITHUB_TOKEN or GH_TOKEN."
            )
        model = os.getenv("GITHUB_MODELS_MODEL", "openai/gpt-4o-mini")
        endpoint = os.getenv(
            "GITHUB_MODELS_ENDPOINT",
            "https://models.github.ai/inference/chat/completions",
        )
        body = json.dumps(
            {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 900,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            endpoint,
            data=body,
            method="POST",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        retry_delays = [5, 10, 20, 40, 60]
        last_error = None
        for attempt, delay in enumerate(retry_delays + [None]):
            try:
                with urllib.request.urlopen(request, timeout=90) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                text = payload["choices"][0]["message"]["content"]
                return text or "", model
            except urllib.error.HTTPError as error:
                last_error = error
                if error.code == 429 and delay is not None:
                    time.sleep(delay)
                    continue
                raise
        raise last_error

    raise ValueError(f"Unsupported LLM_PROVIDER={provider}")
