import requests
import json
import sys

url = "http://127.0.0.1:8000/ask-stream"
data = {"question": "What is BOI?"}
try:
    response = requests.post(url, json=data, stream=True)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
    else:
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                print(chunk, end='', flush=True)
        print("\nSUCCESS")
except Exception as e:
    print(f"EXCEPTION: {e}")
