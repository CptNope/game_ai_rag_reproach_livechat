
import json
import matplotlib.pyplot as plt
import os

LOG_PATH = "game_memory/logs/reinforce_log.jsonl"

def load_reward_episodes():
    episodes = []
    current_episode = []
    last_frame = -100
    death_trigger_threshold = 50  # frames of inactivity or reset = new episode

    if not os.path.exists(LOG_PATH):
        print("No reward log found.")
        return []

    with open(LOG_PATH, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                frame = entry.get("frame", 0)
                reward = entry.get("reward", 0)
                description = entry["state"].get("description", "").lower()

                if frame - last_frame > death_trigger_threshold:
                    if current_episode:
                        episodes.append(current_episode)
                    current_episode = []

                current_episode.append({
                    "frame": frame,
                    "reward": reward,
                    "description": description
                })

                last_frame = frame
            except Exception as e:
                continue

    if current_episode:
        episodes.append(current_episode)

    return episodes

def analyze_episodes(episodes):
    episode_stats = []
    for i, ep in enumerate(episodes):
        frames = [step["frame"] for step in ep]
        rewards = [step["reward"] for step in ep]
        if not frames or not rewards:
            continue
        survival_time = frames[-1] - frames[0]
        total_reward = rewards[-1] - rewards[0]
        avg_reward = total_reward / max(1, len(rewards))
        episode_stats.append({
            "episode": i + 1,
            "survival_time": survival_time,
            "total_reward": total_reward,
            "avg_reward": avg_reward
        })
    return episode_stats

def plot_episodes(episodes, stats):
    plt.figure(figsize=(10, 6))
    for i, ep in enumerate(episodes):
        x = [step["frame"] for step in ep]
        y = [step["reward"] for step in ep]
        plt.plot(x, y, label=f"Ep {i+1} (Survived: {stats[i]['survival_time']} frames)")

    plt.title("Mario AI - Reward Curves per Episode")
    plt.xlabel("Frame")
    plt.ylabel("Score Reward")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("game_memory/logs/reward_episodes_plot.png")
    plt.show()

    # Summary printout
    print("\n=== Episode Summary ===")
    for stat in stats:
        print(f"Episode {stat['episode']}: Survival = {stat['survival_time']} frames | "
              f"Total Reward = {stat['total_reward']} | Avg Reward/frame = {stat['avg_reward']:.2f}")

if __name__ == "__main__":
    episodes = load_reward_episodes()
    if episodes:
        stats = analyze_episodes(episodes)
        plot_episodes(episodes, stats)
