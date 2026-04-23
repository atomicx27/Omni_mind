import chromadb
from sentence_transformers import SentenceTransformer
import hashlib

class FailureMemory:
    def __init__(self, db_path="./chroma_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(name="failures")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = 0.82

    def add_failure(self, error_message: str, stack_trace: str, resolution_note: str = ""):
        text = f"{error_message}\n{stack_trace}"
        embedding = self.model.encode(text).tolist()
        doc_id = hashlib.sha256(text.encode()).hexdigest()[:16]

        self.collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[{"resolution": resolution_note}],
            ids=[doc_id]
        )

    def check_failure(self, error_message: str, stack_trace: str) -> dict:
        text = f"{error_message}\n{stack_trace}"
        embedding = self.model.encode(text).tolist()

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=1,
            include=['distances', 'metadatas']
        )

        if results and results['distances'] and len(results['distances'][0]) > 0:
            dist = results['distances'][0][0]
            similarity = 1.0 - dist

            if similarity >= self.similarity_threshold:
                return {
                    "matched": True,
                    "similarity": similarity,
                    "resolution": results['metadatas'][0][0].get("resolution", "")
                }

        return {"matched": False}
