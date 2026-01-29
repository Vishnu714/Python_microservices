import faiss
import numpy as np

class VectorStore:
    def __init__(self,dim):
        self.dim=dim
        self.index=faiss.IndexFlatIP(dim)
        self.id_to_doc={}
        self.count=0
    def add(self,embs,docs):
        embs_norm=self._normalize(embs)
        self.index.add(embs_norm)
        for i,doc in enumerate(docs):
            self.id_to_doc[self.count+i]=doc
        self.count+=len(docs)
    def _normalize(self,embs):
        norms=np.linalg.norm(embs,axis=1,keepdims=True)
        norms[norms==0]=1
        return embs/ norms
    def search(self,query_emb,k=5):
        q=self._normalize(query_emb.reshape(1,-1))
        D,I=self.index.search(q,k)
        results=[]
        for score,idx in zip(D[0],I[0]):
            if idx==-1:
                continue
            results.append({"score":float(score),"doc":self.id_to_doc.get(idx)})
        return results
