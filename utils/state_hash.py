
import hashlib
import json

def hash_state(state_dict):
    state_str = json.dumps(state_dict, sort_keys=True)
    return hashlib.md5(state_str.encode()).hexdigest()

if __name__ == "__main__":
    print(hash_state({"frame": 104, "enemy": "left", "platform": True}))
