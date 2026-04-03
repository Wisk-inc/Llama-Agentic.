from config import settings
import os

def test_settings():
    settings.set_val("test_key", "test_value")
    assert settings.get("test_key") == "test_value"
    print("Settings test passed!")

if __name__ == "__main__":
    test_settings()
