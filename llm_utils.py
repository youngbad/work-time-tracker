import streamlit as st
import requests
from typing import Optional

def query_llm_agent_openrouter(prompt: str, model: str = "tngtech/deepseek-r1t2-chimera:free") -> str:
    """Query a free LLM agent via OpenRouter API."""
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    if "openrouter_token" not in st.secrets:
        return "Error: OpenRouter API token not found in secrets. Please add 'openrouter_token' to .streamlit/secrets.toml."
    headers = {
        "Authorization": f"Bearer {st.secrets['openrouter_token']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return str(result)
    except Exception as e:
        return f"Error querying LLM agent: {e}"
