import json

import requests
import urllib3

from llm.config import API_KEY 


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MODEL_NAME = "claude-sonnet-4.5"
BASE_URL_IP = "https://63.186.26.61/api/v2"


def chat(prompt: str, system: str = "You are a helpful assistant.") -> str:
    url = f"{BASE_URL_IP}/chat/completions"

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "Host": "chat.int.bayer.com",
            },
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.0,
            },
            timeout=60,
            verify=False,
        )

        response.raise_for_status()

        response_data = response.json()

        content = response_data["choices"][0]["message"]["content"]

        if not isinstance(content, str) or not content.strip():
            raise RuntimeError(
                "LLM zwrócił pustą odpowiedź lub odpowiedź w nieoczekiwanym formacie. "
                f"Odpowiedź API: {response_data}"
            )

        return content

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"Błąd połączenia z LLM: {error}"
        ) from error

    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise RuntimeError(
            "Nieoczekiwany format odpowiedzi API LLM."
        ) from error

def chat_json(prompt: str, system: str) -> dict:
    """
    Wywołuje LLM i wymaga odpowiedzi wyłącznie w formacie JSON.
    """
    raw_response = chat(prompt=prompt, system=system)

    # Czasami model zwraca JSON w bloku Markdown: ```json ... ```
    clean_response = raw_response.strip()

    if clean_response.startswith("```"):
        clean_response = clean_response.removeprefix("```json")
        clean_response = clean_response.removeprefix("```")
        clean_response = clean_response.removesuffix("```")
        clean_response = clean_response.strip()

    try:
        return json.loads(clean_response)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "LLM nie zwrócił poprawnego JSON-a.\n"
            f"Odpowiedź modelu:\n{raw_response}"
        ) from error
