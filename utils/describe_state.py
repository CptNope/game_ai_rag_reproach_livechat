
from retroarch_interface.read_megaman_ram import read_ram_state

def describe_state():
    state = read_ram_state()
    if not state:
        return "Unable to read game state."

    phrases = []

    # Interpret player's position
    if state["player_x"] < 50:
        phrases.append("Player is on the left side of the screen.")
    elif state["player_x"] > 200:
        phrases.append("Player is on the right side of the screen.")
    else:
        phrases.append("Player is near the center of the screen.")

    # Health interpretation
    if state["health"] > 10:
        phrases.append("Player has high health.")
    elif state["health"] > 5:
        phrases.append("Player has moderate health.")
    else:
        phrases.append("Player has low health.")

    # Enemy proximity
    distance = abs(state["enemy_x"] - state["player_x"])
    if distance < 20:
        phrases.append("Enemy is very close.")
    elif distance < 50:
        phrases.append("Enemy is nearby.")
    else:
        phrases.append("Enemy is far away.")

    # Weapon energy
    if state["weapon_energy"] < 5:
        phrases.append("Weapon energy is low.")
    else:
        phrases.append("Weapon energy is sufficient.")

    return " ".join(phrases)

if __name__ == "__main__":
    print(describe_state())
