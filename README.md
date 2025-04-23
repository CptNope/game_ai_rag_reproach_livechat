
# MegaMan AI Fine-Tuning with Axolotl + DeepSeek

This project trains a custom MegaMan-playing AI using logged game states and actions from RAM + screenshots.

---

## Step-by-Step Fine-Tuning (6GB RAM Optimized)

### 1. Install Dependencies

```bash
sudo apt update && sudo apt install -y git python3 python3-pip
pip install -U pip
pip install axolotl[flash-attn] accelerate bitsandbytes
```

If that fails (e.g. Flash Attention incompatibility), fallback:
```bash
pip install axolotl accelerate bitsandbytes
```

> Make sure you’re using Python 3.9–3.11.

---

### 2. Prepare Your Data

Log gameplay using:

```bash
python utils/log_and_embed_pairs.py
```

Then generate training data:

```bash
python utils/export_finetune_jsonl.py
```

---

### 3. Run Training

Use the included Axolotl config:

```bash
axolotl axolotl_deepseek_lora.yml
```

This will:
- Load DeepSeek Coder 1.3B in 4-bit
- Apply LoRA adapters
- Fine-tune using your `game_memory/megaman_finetune.jsonl`

---

### 4. Model Output

Your LoRA-tuned model will be saved in:

```
megaman-deepseek-lora/
```

You can load this back into Ollama or HuggingFace transformers using PEFT.

---

### Optional Next Steps

- Add more diverse RAM/game states
- Include screenshots for OCR-enhanced prompts
- Merge LoRA into full model if needed (for local Ollama serving)

---

Built with love by SciStories + ChatGPT
