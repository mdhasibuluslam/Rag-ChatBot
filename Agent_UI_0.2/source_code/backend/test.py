from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Model path ঠিক করো
BASE_MODEL_PATH = r"E:\Agent_model\New folder"

# Tokenizer load
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH)

# Model load
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_PATH,
    torch_dtype=torch.float16,   # GPU হলে float16 use করা memory কমানোর জন্য
    device_map="auto"            # GPU বা CPU automatically assign করে
)

# Test
prompt = "Hello, summarize this text for me."
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
