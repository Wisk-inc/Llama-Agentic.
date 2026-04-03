import json
import os
import time
from pathlib import Path
from config import settings

SESSION_DIR = Path.home() / ".llama-agentic" / "sessions"

class SessionStore:
    def __init__(self):
        if not SESSION_DIR.exists():
            SESSION_DIR.mkdir(parents=True, exist_ok=True)

    def save_session(self, session_id: str, messages: list, metadata: dict = None) -> Path:
        filepath = SESSION_DIR / f"{session_id}.json"
        data = {
            "session_id": session_id,
            "timestamp": time.time(),
            "metadata": metadata or {},
            "messages": messages
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        return filepath

    def load_session(self, session_id: str) -> dict:
        filepath = SESSION_DIR / f"{session_id}.json"
        if not filepath.exists():
            raise FileNotFoundError(f"Session '{session_id}' not found.")
        with open(filepath, "r") as f:
            return json.load(f)

    def list_sessions(self) -> list[dict]:
        sessions = []
        for file in SESSION_DIR.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                    sessions.append({
                        "id": data["session_id"],
                        "timestamp": data["timestamp"],
                        "summary": data.get("metadata", {}).get("summary", "No summary")
                    })
            except Exception:
                pass
        return sorted(sessions, key=lambda x: x["timestamp"], reverse=True)

def generate_session_id() -> str:
    return time.strftime("%Y%m%d_%H%M%S")
