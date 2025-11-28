
import json

def save(path, collection):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(collection, file, indent=4, ensure_ascii=False)

def load(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)