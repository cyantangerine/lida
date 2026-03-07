
import requests
print(requests.post("http://localhost:11434/api/generate", json={
    "model": "gemma3:1b",
    "prompt": "What is the capital of France?",
    "stream": False,
    "options": {
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "num_predict": 200
    }
}).text)