import ollama
from typing import List, Dict, Any
from config import EMBEDDING_MODEL, OLLAMA_HOST
import chromadb
from chromadb.config import Settings
from config import CHROMA_PERSIST_DIR


class EmbeddingManager:
    def __init__(self):
        self.client = chromadb.Client(
            Settings(persist_directory=CHROMA_PERSIST_DIR, is_persistent=True)
        )
        # Create or get the collection
        self.collection = self.client.get_or_create_collection(
            name="scms_data", metadata={"hnsw:space": "cosine"}
        )

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings for a given text using Ollama"""
        try:
            response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=text)

            # Handle the new EmbeddingsResponse type
            if hasattr(response, "embedding"):
                return response.embedding

            # Fallback for dict response
            if isinstance(response, dict):
                if "embedding" in response:
                    return response["embedding"]
                elif "embeddings" in response:
                    return response["embeddings"][0]

            raise ValueError(f"Could not extract embedding from response: {response}")

        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    async def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the vector store"""
        try:
            # Process documents in batches
            batch_size = 100
            counter = 0  # Global counter for unique IDs
            for i in range(0, len(documents), batch_size):
                batch = documents[i : i + batch_size]

                # Prepare data for ChromaDB
                ids = [f"{doc['type']}_{doc['id']}_{hash(doc['content'])}_{counter + j}" for j, doc in enumerate(batch)]
                texts = [doc["content"] for doc in batch]
                metadatas = [{"type": doc["type"], "id": doc["id"]} for doc in batch]

                # Generate embeddings for the batch
                embeddings = []
                for text in texts:
                    try:
                        embedding = await self.generate_embedding(text)
                        embeddings.append(embedding)
                    except Exception as e:
                        print(f"Error generating embedding for text: {text[:100]}...")
                        print(f"Error: {e}")
                        raise

                if not embeddings:
                    raise ValueError("No embeddings were generated")

                # Add to ChromaDB
                try:
                    self.collection.add(
                        ids=ids,
                        embeddings=embeddings,
                        documents=texts,
                        metadatas=metadatas
                    )
                except Exception as e:
                    print(f"Error adding to ChromaDB: {e}")
                    print(f"Sample embedding length: {len(embeddings[0]) if embeddings else 'no embeddings'}")
                    raise

                counter += len(batch)  # Increment counter by batch size

        except Exception as e:
            print(f"Error adding documents to vector store: {e}")
            raise

    async def query_similar(
        self, query: str, n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Query the vector store for similar documents"""
        try:
            # Generate embedding for the query
            query_embedding = await self.generate_embedding(query)

            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )

            # Format results
            formatted_results = []
            for i in range(len(results["documents"][0])):
                formatted_results.append(
                    {
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                    }
                )

            return formatted_results

        except Exception as e:
            print(f"Error querying vector store: {e}")
            raise
 