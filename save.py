import json

def file_exists(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            pass
        return True
    except:
        return False


def save(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load(path):
    if not file_exists(path):
        return None
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_game(player, board, current_level, difficulty):
    save_data = {
        "difficulty": difficulty,
        "current_level": current_level,
        "player": player.to_dict(),
        "board": board.to_dict() if board else None
    }
    save("save.json", save_data)


def load_game():
    data = load("save.json")
    if data is None:
        return None, False
    return data, True


def save_record(max_level, coins):
    record = {
        "max_level": max_level,
        "coins": coins
    }
    save("record.json", record)


def load_record():
    data = load("record.json")
    if data and isinstance(data, dict) and "max_level" in data and "coins" in data:
        return data["max_level"], data["coins"]
    return 0, 0