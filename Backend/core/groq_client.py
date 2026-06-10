import json
import os
import re
import urllib.error
import urllib.request



class GroqAPIError(Exception):
    pass


def get_groq_api_url() -> str:
    api_url = os.getenv("GROQ_API_URL") or os.getenv("DEFAULT_GROQ_API_URL")
    if not api_url:
        raise GroqAPIError(
            "GROQ_API_URL veya DEFAULT_GROQ_API_URL ortam değişkeni tanımlı değil."
        )
    return api_url


def get_groq_model() -> str:
    model = os.getenv("GROQ_MODEL") or os.getenv("DEFAULT_GROQ_MODEL")
    if not model:
        raise GroqAPIError(
            "GROQ_MODEL veya DEFAULT_GROQ_MODEL ortam değişkeni tanımlı değil."
        )
    return model


def chat_completion(messages, *, model=None, temperature=0.2, timeout=120) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise GroqAPIError("GROQ_API_KEY ortam değişkeni tanımlı değil.")

    payload = json.dumps(
        {
            "model": model or get_groq_model(),
            "messages": messages,
            "temperature": temperature,
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        get_groq_api_url(),
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "QRmenu-Backend/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise GroqAPIError(f"Groq API hatası ({exc.code}): {body}") from exc
    except urllib.error.URLError as exc:
        raise GroqAPIError(f"Groq API bağlantı hatası: {exc.reason}") from exc

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise GroqAPIError("Groq API yanıtı beklenen formatta değil.") from exc


def parse_json_response(content: str):
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)
