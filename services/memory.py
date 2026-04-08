import json 
import os

MEMORY_FILE = "memory.json"


def load_memory()-> dict:

    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE,"r", encoding="utf-8") as f:
        return json.load(f)
    



def save_memory(memory: dict):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)
        

def get_user_history(user_id: str) -> list:
    memory=load_memory()
    return memory.get(user_id,[])

def add_to_history(user_id: str,role: str, content: str):
    memory=load_memory()
    if user_id not in memory:
        memory[user_id]=[]
    memory[user_id].append({"role":role,"content":content})

    memory[user_id] = memory[user_id][-10:]
    save_memory(memory)