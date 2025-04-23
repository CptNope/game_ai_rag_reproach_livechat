
import subprocess

def generate_action(prompt):
    command = ["ollama", "run", "deepseek-coder", "--prompt", prompt]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout.strip()

if __name__ == "__main__":
    output = generate_action("Game state: enemy on left, platform ahead. What should I do?")
    print("Action:", output)
