from vectorstore import query_docs
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


MODEL = 'distilgpt2'
tokenizers = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL)

def generate_answer(context,question):
    promt = f'Context:\n{context}\n\nQuestion{question}\nAnswer:\n'
    inputs = tokenizers(promt, return_tensors='pt')
    outcome = model.generate(**inputs, max_new_tokens=150)
    return tokenizers.decode(outcome[0], skip_special_tokens=True)

def rag_answer(query):
    docs = query_docs(query, n_results=3)
    context = '\n\n'.join(docs)
    answer = generate_answer(context,query)

    return {
        'query':query,
        'context' :context,
        'answer':answer
    }
