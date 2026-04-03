import httpx
import json
from config import settings

class OpenRouterProvider:
    def __init__(self, api_key=None):
        self.api_key = api_key or settings.get("api_keys", {}).get("openrouter")
        self.base_url = "https://openrouter.ai/api/v1"

    async def chat(self, model, messages, tools=None, stream=True):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://llama-agentic.ai", # Site URL for OpenRouter
            "X-Title": "Llama Agentic",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=60) as client:
            if not stream:
                response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                yield response.json()
            else:
                async with client.stream("POST", f"{self.base_url}/chat/completions", json=payload, headers=headers) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                yield json.loads(data)
                            except json.JSONDecodeError:
                                pass

    async def list_models(self) -> list[str]:
        # We can return a curated list or fetch from their API
        return [
            "meta-llama/llama-3.1-8b-instruct:free",
            "meta-llama/llama-3.1-70b-instruct",
            "anthropic/claude-3.5-sonnet",
            "google/gemini-pro-1.5"
        ]
