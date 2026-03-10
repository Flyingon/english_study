import chromadb
from chromadb.utils import embedding_functions
from agents.vocabulary_agent.config import settings
from agents.vocabulary_agent.models import WordMemory
import uuid

class ChromaService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
        
        # Use multilingual sentence-transformer model for better Chinese-English retrieval
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="paraphrase-multilingual-MiniLM-L12-v2")
        
        self.collection = self.client.get_or_create_collection(
            name="english_memory",
            embedding_function=self.ef
        )

    def add_word(self, word_memory: WordMemory):
        record_id = str(uuid.uuid4())
        
        # Construct document for retrieval
        document = f"""
        Word: {word_memory.word}
        Meaning: {word_memory.meaning_you_learned}
        Scene: {word_memory.learn_scene}
        Source: {word_memory.learn_source}
        Usage: {word_memory.usage_old}
        Note: {word_memory.your_note}
        Snippet: {word_memory.reference_snippet}
        """
        
        # Filter out None values for metadata
        metadata = {k: v for k, v in word_memory.model_dump().items() if v is not None}
        
        # Chroma will automatically compute embeddings using the function provided
        self.collection.add(
            ids=[record_id],
            documents=[document],
            metadatas=[metadata]
        )
        return record_id

    def query_words(self, query_text: str, n_results: int = 3, where: dict = None):
        # Pass the query text directly; Chroma handles embedding
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
            include=['metadatas', 'distances']
        )
        return results

    def get_word(self, record_id: str):
        result = self.collection.get(ids=[record_id])
        if result['ids']:
            return result['metadatas'][0]
        return None

    def list_words(self, limit: int = 10, offset: int = 0, where: dict = None, where_document: dict = None):
        result = self.collection.get(
            limit=limit,
            offset=offset,
            where=where,
            where_document=where_document
        )
        return result

    def count_words(self, where: dict = None, where_document: dict = None):
        if where is None and where_document is None:
            return self.collection.count()

        result = self.collection.get(
            where=where,
            where_document=where_document
        )
        return len(result["ids"])

    def delete_word(self, record_id: str):
        self.collection.delete(ids=[record_id])
