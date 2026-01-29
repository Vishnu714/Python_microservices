import requests
from app.core.config import settings

def call_llm(system_prompt,user_prompt,timeout=30):
    payload={"model":settings.MODEL_NAME,"prompt":f"{system_prompt}\n\n{user_prompt}","stream":False}
    try:
        r=requests.post(settings.OLLAMA_URL+"/api/generate",json=payload,timeout=timeout)
        r.raise_for_status()
        return r.json().get("response","")
    except requests.exceptions.RequestException:
        return "LLM_ERROR: request failed or timed out"
