import anthropic
from config import settings

class AnthropicProvider:
    def __init__(self, api_key=None):
        self.api_key = api_key or settings.get("api_keys", {}).get("anthropic")
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)

    async def chat(self, model, messages, tools=None, stream=True):
        system = ""
        user_msgs = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                user_msgs.append(msg)

        if not stream:
            response = await self.client.messages.create(
                model=model,
                max_tokens=4096,
                system=system,
                messages=user_msgs,
                tools=tools or anthropic.NOT_GIVEN
            )
            # Convert to OpenAI-like dictionary format
            yield {
                "message": {
                    "role": "assistant",
                    "content": response.content[0].text if response.content else ""
                }
            }
        else:
            async with self.client.messages.stream(
                model=model,
                max_tokens=4096,
                system=system,
                messages=user_msgs,
                tools=tools or anthropic.NOT_GIVEN
            ) as stream_resp:
                async for event in stream_resp:
                    if event.type == "content_block_delta":
                        yield {
                            "choices": [{
                                "delta": {
                                    "content": event.delta.text
                                }
                            }]
                        }

    async def list_models(self) -> list[str]:
        return ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-haiku-20240307"]
