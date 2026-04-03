import httpx
import json
from config import settings

class OllamaProvider:
    def __init__(self, base_url=None):
        self.base_url = base_url or settings.get("ollama_url", "http://localhost:11434")

    def is_running(self) -> bool:
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list[str]:
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m["name"] for m in models]
            return []
        except Exception:
            return []

    async def chat(self, model, messages, tools=None, stream=True):
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        if tools:
            # Ollama supports a subset of OpenAI-like tool definitions
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=60) as client:
            if not stream:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                yield response.json()
            else:
                async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response:
                    async for line in response.aiter_lines():
                        if line:
                            yield json.loads(line)
