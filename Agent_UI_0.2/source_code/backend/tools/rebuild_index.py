import os
import argparse
import faiss
import pickle
from vectorstore.embedder import embed
from chunking.chunker import chunk_text
from ingestion import pdf, docx, pptx, text as text_ingest, json_file, image_ocr


def extract_text(path):
    if path.lower().endswith('.pdf'):
        return pdf.load_pdf(path)
    if path.lower().endswith('.docx'):
        return docx.load_docx(path)
    if path.lower().endswith('.pptx'):
        return pptx.load_pptx(path)
    if path.lower().endswith('.txt'):
        return text_ingest.load_txt(path)
    if path.lower().endswith('.json'):
        return json_file.load_json(path)
    # fall back to OCR for images
    if any(path.lower().endswith(ext) for ext in ('.png', '.jpg', '.jpeg')):
        return image_ocr.load_image(path)
    return ''


def main(source_dir, out_dir):
    docs = []
    for root, dirs, files in os.walk(source_dir):
        for f in files:
            fp = os.path.join(root, f)
            if f.startswith('.'):
                continue
            txt = extract_text(fp)
            if not txt or not txt.strip():
                continue
            chunks = chunk_text(txt)
            for c in chunks:
                docs.append({'source': fp, 'text': c})

    if not docs:
        print('No documents found to index')
        return

    texts = [d['text'] for d in docs]
    emb = embed(texts)

    # normalize embeddings for cosine via inner product
    import numpy as np
    emb = np.array(emb).astype('float32')
    faiss.normalize_L2(emb)

    dim = emb.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(emb)

    os.makedirs(os.path.join(out_dir), exist_ok=True)
    index_path = os.path.join(out_dir, 'index.faiss')
    meta_path = os.path.join(out_dir, 'meta.pkl')

    faiss.write_index(index, index_path)
    with open(meta_path, 'wb') as f:
        pickle.dump(docs, f)

    print('Wrote', index_path, 'and', meta_path)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--source', required=True, help='Folder with source files to index')
    p.add_argument('--out', default='backend/data', help='Output data folder')
    args = p.parse_args()
    main(args.source, args.out)
