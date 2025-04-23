
from retroarch_interface.read_mario_ram import read_ram_state

def describe_state():
    state = read_ram_state()
    if not state:
        return "Unable to read game state."

    phrases = []

    if state["player_x"] < 100:
        phrases.append("Mario is near the start of the level.")
    elif state["player_x"] > 200:
        phrases.append("Mario is near the end of the screen.")
    else:
        phrases.append("Mario is in the middle of the screen.")

    if state["powerup_state"] == 0:
        phrases.append("Mario is small.")
    elif state["powerup_state"] == 1:
        phrases.append("Mario has a mushroom.")
    elif state["powerup_state"] == 2:
        phrases.append("Mario has a fire flower.")

    dy = abs(state["enemy1_x"] - state["player_x"])
    if dy < 15:
        phrases.append("An enemy is very close!")
    elif dy < 50:
        phrases.append("An enemy is nearby.")
    else:
        phrases.append("No enemy in close range.")

    return " ".join(phrases)

if __name__ == "__main__":
    print(describe_state())
