import google.generativeai as genai
from config import settings

class GeminiProvider:
    def __init__(self, api_key=None):
        self.api_key = api_key or settings.get("api_keys", {}).get("gemini")
        genai.configure(api_key=self.api_key)

    async def chat(self, model, messages, tools=None, stream=True):
        model_obj = genai.GenerativeModel(model)

        # Convert messages to Gemini history format
        # Gemini history format: list of {'role': 'user'|'model', 'parts': [str]}
        history = []
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [msg["content"]]})

        chat = model_obj.start_chat(history=history)
        last_msg = messages[-1]["content"]

        if not stream:
            response = await chat.send_message_async(last_msg, tools=tools)
            yield {
                "message": {
                    "role": "assistant",
                    "content": response.text
                }
            }
        else:
            async for chunk in await chat.send_message_async(last_msg, tools=tools, stream=True):
                yield {
                    "choices": [{
                        "delta": {
                            "content": chunk.text
                        }
                    }]
                }

    async def list_models(self) -> list[str]:
        return ["gemini-1.5-pro", "gemini-1.5-flash"]
