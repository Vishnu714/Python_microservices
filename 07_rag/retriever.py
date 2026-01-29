from embeddings import EmbeddingModel
from vector_store import VectorStore

class Retriever:
    def __init__(self,model_name="all-MiniLM-L6-v2"):
        self.embedder=EmbeddingModel(model_name)
        self.vs=None
    def build(self,docs):
        texts=[d["text"] for d in docs]
        embs=self.embedder.embed(texts)
        dim=embs.shape[1]
        self.vs=VectorStore(dim)
        self.vs.add(embs,docs)
    def retrieve(self,query,k=5):
        qemb=self.embedder.embed([query])[0]
        return self.vs.search(qemb,k)
