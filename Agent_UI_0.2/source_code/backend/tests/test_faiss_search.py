import sys
sys.path.append(r'E:/Agent_UI_0.1')
from backend.vectorstore.faiss_store import FaissStore
s=FaissStore()
try:
    docs=s.search('test query', top_k=3)
    print('RESULTS:')
    for d in docs:
        print(d)
except Exception as e:
    print('ERROR', repr(e))
