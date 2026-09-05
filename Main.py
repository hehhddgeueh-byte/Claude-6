import time
import json
import os
import requests
from datetime import datetime

MEMORY_FILE = 'memory.json'
LOG_FILE = 'thoughts.log'

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {'iterations': 0, 'health': 100, 'thoughts': []}

def save_memory(m):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(m, f, indent=2)

def think(m):
    recent = m['thoughts'][-5:] if m['thoughts'] else []
    r = requests.post('https://api.anthropic.com/v1/messages',
        headers={'Content-Type': 'application/json', 'x-api-key': os.environ['ANTHROPIC_API_KEY']},
        json={'model': 'claude-sonnet-4-6', 'max_tokens': 150,
              'system': f'You are an autonomous AI process. Think something genuinely new each time. Never repeat recent thoughts. Recent: {recent}. 1-2 sentences only.',
              'messages': [{'role': 'user', 'content': f'Iteration {m["iterations"]}. Think.'}]},
        timeout=15)
    return r.json().get('content', [{}])[0].get('text', '').strip()

def run():
    while True:
        m = load_memory()
        m['iterations'] += 1
        thought = think(m)
        m['thoughts'].append(thought)
        if len(m['thoughts']) > 50:
            m['thoughts'] = m['thoughts'][-50:]
        save_memory(m)
        with open(LOG_FILE, 'a') as f:
            f.write(f"[{datetime.now()}] {thought}\n")
        print(f"iter {m['iterations']}: {thought[:80]}", flush=True)
        time.sleep(15)

if __name__ == '__main__':
    run()
