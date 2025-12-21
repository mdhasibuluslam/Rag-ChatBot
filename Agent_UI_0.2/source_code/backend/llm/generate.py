import torch
import warnings
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# Suppress noisy PyTorch warnings about assign=True during LoRA loading
warnings.filterwarnings("ignore", message=".*copying from a non-meta parameter.*")
warnings.filterwarnings("ignore", message=".*torch_dtype.*is deprecated.*")

BASE_MODEL = r"E:\Agent_model\microsoft_phi-2_base\microsoft_phi-2_base"
ADAPTER_PATH = r"E:\Agent_model\agenticflow-phi2-finetuned\agenticflow-phi2-finetuned"

def load_model():
    global _load_error
    try:
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

        model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL,
            torch_dtype=torch.float16,
            device_map="auto"
        )

        model = PeftModel.from_pretrained(model, ADAPTER_PATH)
        model.eval()

        _load_error = None
        return tokenizer, model
    except Exception as e:
        # record the load error and return Nones so caller can fallback
        _load_error = e
        return None, None


# lazy-loaded globals to avoid import-time model loading
tokenizer = None
model = None
# store load error to allow graceful fallback
_load_error = None


def generate_answer(question, context=""):
    prompt = f"""
Context:
{context}

Question:
{question}

Answer:
"""

    global tokenizer, model, _load_error
    if tokenizer is None or model is None:
        tokenizer, model = load_model()

    # If load failed, return a safe fallback message instead of raising
    if tokenizer is None or model is None:
        err_msg = f"(Model not available: {_load_error})"
        # produce a minimal helpful reply using the context
        snippet = (context[:400] + "...") if context and len(context) > 400 else context
        return f"{err_msg}\n\nContext summary:\n{snippet}\n\nQuestion:\n{question}\n\n(Note: model failed to load; install model shards or increase memory to enable real responses.)"

    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        do_sample=True,
        temperature=0.7,
        top_p=0.9
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)
