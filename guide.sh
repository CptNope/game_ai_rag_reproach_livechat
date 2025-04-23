
#!/bin/bash

while true; do
  echo "=== MegaMan AI Companion ==="
  echo "1. Launch RetroArch with Save State"
  echo "2. Start AI Game Loop"
  echo "3. Log and Embed Game Data"
  echo "4. Export Fine-tuning JSONL"
  echo "5. Train with Axolotl + LoRA"
  echo "6. Run Fine-Tuned Model"
  echo "7. Exit"
  read -p "Choose an option: " opt

  case $opt in
    1) python3 retroarch_interface/launch_with_state.py ;;
    2) python3 main.py ;;
    3) python3 utils/log_and_embed_pairs.py ;;
    4) python3 utils/export_finetune_jsonl.py ;;
    5) axolotl axolotl_deepseek_lora.yml ;;
    6) python3 ollama_agent/run_lora_model.py ;;
    7) break ;;
    *) echo "Invalid option!" ;;
  esac
done
