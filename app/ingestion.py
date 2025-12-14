from app.vectorstore import add_docs
import os

def chunk_text(text,chunk_size=300):
    words = text.split()
    return [''.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def ingest_text_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    chunk = chunk_text(text)
    ids = [f'doc{i}' for i in range(len(chunk))]
    add_docs(ids,chunk)
    print('Ingested: ', len(chunk))