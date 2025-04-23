
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

# Load base model and LoRA weights
base_model_id = "deepseek-ai/deepseek-coder-1.3b-base"
lora_model_path = "megaman-deepseek-lora"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(base_model_id)

print("Loading base model...")
model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    load_in_4bit=True,
    device_map="auto"
)

print("Loading LoRA adapter...")
model = PeftModel.from_pretrained(model, lora_model_path)
model.eval()

def generate_response(prompt, max_tokens=128):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=0.8,
            top_p=0.95,
            eos_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

if __name__ == "__main__":
    test_prompt = "Game state: Player is near the right edge. Low health. Enemy is very close. What should the player do?"
    print(generate_response(test_prompt))
