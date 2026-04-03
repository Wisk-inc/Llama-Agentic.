class Compactor:
    def __init__(self, keep_last_n: int = 20):
        self.keep_last_n = keep_last_n

    def compact(self, messages: list) -> list:
        if len(messages) <= self.keep_last_n:
            return messages

        # In a more advanced version, this would use the LLM to summarize
        # for now, we'll keep the system prompt (if any) and the last N messages

        system_prompt = next((msg for msg in messages if msg["role"] == "system"), None)
        recent_messages = messages[-self.keep_last_n:]

        compacted = []
        if system_prompt and system_prompt not in recent_messages:
            compacted.append(system_prompt)

        # Add a summary placeholder
        compacted.append({
            "role": "system",
            "content": "[Context summarized: some older messages have been removed to save space]"
        })

        compacted.extend(recent_messages)
        return compacted
