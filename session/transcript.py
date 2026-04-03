import json
import time
from session.compactor import Compactor

class TranscriptStore:
    def __init__(self, keep_last_n: int = 20):
        self.messages = []
        self.is_dirty = False
        self.compactor = Compactor(keep_last_n=keep_last_n)

    def append(self, role: str, content: str = None, tool_calls: list = None, tool_results: list = None):
        msg = {
            "role": role,
            "timestamp": time.time(),
            "content": content,
            "tool_calls": tool_calls,
            "tool_results": tool_results
        }
        self.messages.append(msg)
        self.is_dirty = True

        # Check if we need to compact
        if len(self.messages) > 30: # Some buffer
            self.compact()

    def replay(self) -> list:
        return self.messages

    def compact(self):
        self.messages = self.compactor.compact(self.messages)
        self.is_dirty = True

    def flush(self):
        self.is_dirty = False
