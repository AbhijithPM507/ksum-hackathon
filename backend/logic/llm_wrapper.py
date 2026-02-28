import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_response(prompt: str) -> str:
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

        if "response" in data:
            return data["response"]

        elif "error" in data:
            print("Ollama Error:", data["error"])
            return "Error generating response."

        else:
            print("Unexpected LLM format:", data)
            return "Unable to generate response."

    except requests.exceptions.RequestException as e:
        print("LLM Connection Error:", e)
        return "LLM service unavailable."