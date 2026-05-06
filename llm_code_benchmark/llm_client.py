from __future__ import annotations

import json
import os
import urllib.request

from .prompts import SYSTEM_PROMPT


class LlmClient:
    def complete(self, prompt: str) -> str:
        raise NotImplementedError


class OpenAIClient(LlmClient):
    def __init__(self, model: str) -> None:
        self.model = model
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

    def complete(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required unless --dry-run or --sample is used.")

        url = f"{self.base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
        }
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=90) as response:
            data = json.loads(response.read().decode("utf-8"))

        return data["choices"][0]["message"]["content"]


class AnthropicClient(LlmClient):
    def __init__(self, model: str) -> None:
        self.model = model
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1")
        self.max_tokens = int(os.environ.get("ANTHROPIC_MAX_TOKENS", "4096"))

    def complete(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is required unless --dry-run or --sample is used.")

        url = f"{self.base_url.rstrip('/')}/messages"
        payload = {
            "model": self.model,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": self.max_tokens,
        }
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=90) as response:
            data = json.loads(response.read().decode("utf-8"))

        for block in data.get("content", []):
            if block.get("type") == "text":
                return block.get("text", "")
        return ""


PROVIDERS = {
    "openai": OpenAIClient,
    "anthropic": AnthropicClient,
}


def build_client(model: str, provider: str | None = None) -> LlmClient:
    resolved = provider or _detect_provider(model)
    if resolved not in PROVIDERS:
        raise ValueError(
            f"Unknown provider '{resolved}'. Choose from: {', '.join(PROVIDERS)}"
        )
    return PROVIDERS[resolved](model)


def _detect_provider(model: str) -> str:
    name = model.lower()
    if name.startswith("claude-") or name.startswith("claude/"):
        return "anthropic"
    if name.startswith(("gpt-", "o1-", "o3-", "o4-", "chatgpt-")):
        return "openai"
    raise ValueError(
        f"Cannot auto-detect provider for model '{model}'. "
        f"Pass --provider {{{', '.join(PROVIDERS)}}}."
    )
