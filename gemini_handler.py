"""
Gemini API Handler v4 - Auto-discovers model via ListModels.
Uses gemini-2.5-flash from config.yaml directly (confirmed working).
"""

import time
import requests

from src.utils.config import get_api_key, load_config
from src.utils.logger import setup_logger
from src.prompts.career_prompts import build_system_prompt

logger = setup_logger(__name__)
_config = load_config()
_gemini_cfg = _config["gemini"]

BASE = "https://generativelanguage.googleapis.com/v1beta"


class GeminiClient:
    def __init__(self, api_key, model_name, system_prompt, gen_config):
        self.api_key = api_key
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.gen_config = gen_config

    def chat(self, user_message, history):
        contents = []
        for msg in history:
            role = msg.get("role", "user")
            parts = msg.get("parts", [])
            text = parts[0].get("text", "") if parts and isinstance(parts[0], dict) else str(parts)
            contents.append({"role": role, "parts": [{"text": text}]})
        contents.append({"role": "user", "parts": [{"text": user_message}]})

        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": self.system_prompt}]},
            "generationConfig": self.gen_config,
        }

        url = f"{BASE}/models/{self.model_name}:generateContent?key={self.api_key}"
        resp = requests.post(url, json=payload, timeout=30)

        if resp.status_code != 200:
            err = resp.json().get("error", {}).get("message", resp.text)
            raise RuntimeError(f"HTTP {resp.status_code}: {err}")

        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        tokens = data.get("usageMetadata", {}).get("totalTokenCount", 0)
        return {"text": text, "tokens": tokens}


def get_model():
    """Use the model from config.yaml directly - no probing needed."""
    api_key = get_api_key()
    model_name = _gemini_cfg["model"]   # reads "gemini-2.5-flash" from config.yaml

    gen_config = {
        "maxOutputTokens": _gemini_cfg["max_output_tokens"],
        "temperature": _gemini_cfg["temperature"],
        "topP": _gemini_cfg["top_p"],
        "topK": _gemini_cfg["top_k"],
    }

    logger.info(f"GeminiClient ready | model={model_name}")
    return GeminiClient(api_key, model_name, build_system_prompt(), gen_config)


def send_message(model, user_message, chat_history, max_retries=2):
    for attempt in range(max_retries + 1):
        try:
            t0 = time.time()
            result = model.chat(user_message, chat_history)
            logger.info(f"OK | tokens={result['tokens']} | {round(time.time()-t0, 2)}s")
            return {
                "text": result["text"],
                "tokens_used": result["tokens"],
                "success": True,
                "error": None,
            }
        except Exception as e:
            err = str(e)
            logger.error(f"Attempt {attempt+1} failed: {err[:120]}")
            if attempt < max_retries and ("429" in err or "503" in err):
                time.sleep(2 ** attempt)
                continue
            return {"text": None, "tokens_used": 0, "success": False, "error": err}
    return {"text": None, "tokens_used": 0, "success": False, "error": "Max retries exceeded."}


def validate_api_connection():
    try:
        m = get_model()
        r = m.chat("Say OK", [])
        return (True, f"Connected - model: {m.model_name}") if r["text"] else (False, "Empty response")
    except Exception as e:
        return False, str(e)