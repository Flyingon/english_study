import requests
import time
import json

BASE_URL = "http://localhost:8091/api"

def wait_for_server():
    print("Waiting for server to start...")
    for _ in range(10):
        try:
            response = requests.get("http://localhost:8091/")
            if response.status_code == 200:
                print("Server is up!")
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    print("Server failed to start.")
    return False

def add_memory():
    print("\n[1] Adding a new word memory...")
    payload = {
        "word": "ambiguous",
        "meaning_you_learned": "模糊的、模棱两可的",
        "learn_scene": "Reading a tech article",
        "usage_old": "The instructions were ambiguous.",
        "your_note": "Confused with ambivalent (mixed feelings)",
        "reference_snippet": "The requirements for the new feature were ambiguous, leading to confusion."
    }
    
    try:
        response = requests.post(f"{BASE_URL}/word/add", json=payload)
        if response.status_code == 200:
            print("✅ Success:", response.json())
        else:
            print("❌ Failed:", response.text)
    except Exception as e:
        print(f"❌ Error: {e}")

def retrieve_memory():
    print("\n[2] Retrieving memory (simulating conversation)...")
    query = "那个表示模糊不清的词是什么？"
    print(f"User Query: {query}")
    
    payload = {
        "query": query,
        "top_k": 3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/word/retrieve", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("\n--- AI Response ---")
            print(data['ai_summary'])
            print("\n--- Retrieved Memory ---")
            print(json.dumps(data['matches'], indent=2, ensure_ascii=False))
        else:
            print("❌ Failed:", response.text)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if wait_for_server():
        add_memory()
        retrieve_memory()
