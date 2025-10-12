import requests, time

def wait_for_ollama(max_retries=10, delay=2):
    for i in range(max_retries):
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=2)
            if r.status_code == 200:
                print("Ollama disponible.")
                return True
        except Exception:
            print(f"Esperando que Ollama esté disponible... ({i+1}/{max_retries})")
            time.sleep(delay)
    raise ConnectionError("Ollama no responde en localhost:11434")
