from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import ollama
from contextlib import asynccontextmanager
from database import DatabaseManager
from embeddings import EmbeddingManager
from cache_manager import CacheManager
from config import LLM_MODEL, EMBEDDING_MODEL, API_HOST, API_PORT

# Global flag to track initialization
is_initialized = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global is_initialized
    # Startup
    try:
        print("Starting RAG service...")
        print(f"Will attempt to load models: {EMBEDDING_MODEL} and {LLM_MODEL}")
        # Don't block startup on model pulling - do it in background
        is_initialized = True
        print("Service initialized! Models will be pulled on first use.")
    except Exception as e:
        print(f"Startup warning: {e}")
        is_initialized = True
    yield
    # Shutdown
    print("Shutting down RAG service...")


app = FastAPI(title="SCMS RAG Service", lifespan=lifespan)

# Add CORS middleware with expanded configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "SCMS RAG Service is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "initialized": is_initialized}


@app.get("/models/status")
async def check_models():
    """Check if required models are available"""
    try:
        models_response = ollama.list()
        # Handle different possible response formats
        if isinstance(models_response, dict) and 'models' in models_response:
            models_list = models_response['models']
        else:
            models_list = models_response if isinstance(models_response, list) else []
        
        # Extract model names, handling different possible formats
        available_models = []
        for model in models_list:
            if isinstance(model, dict):
                # Try different possible keys for model name
                name = model.get('name') or model.get('model') or model.get('id') or str(model)
                available_models.append(name)
            else:
                available_models.append(str(model))

        required_models = [EMBEDDING_MODEL, LLM_MODEL]
        missing_models = [
            model for model in required_models if model not in available_models
        ]

        return {
            "available_models": available_models,
            "required_models": required_models,
            "missing_models": missing_models,
            "all_models_ready": len(missing_models) == 0,
        }
    except Exception as e:
        return {"error": str(e), "all_models_ready": False}


@app.post("/models/pull")
async def pull_models():
    """Pull required models"""
    try:
        results = []
        for model in [EMBEDDING_MODEL, LLM_MODEL]:
            try:
                print(f"Pulling model: {model}")
                ollama.pull(model)
                results.append({"model": model, "status": "success"})
            except Exception as e:
                results.append({"model": model, "status": "error", "error": str(e)})

        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Initialize managers - make this more tolerant
try:
    db_manager = DatabaseManager()
    embedding_manager = EmbeddingManager()
    cache_manager = CacheManager()
    print("Managers initialized successfully")
except Exception as e:
    print(f"Warning: Some managers failed to initialize: {e}")
    db_manager = None
    embedding_manager = None
    cache_manager = None


class Query(BaseModel):
    question: str
    n_results: Optional[int] = 5


class ChatResponse(BaseModel):
    answer: str
    context: List[str]


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(query: Query):
    try:
        # Check if managers are initialized
        if not all([db_manager, embedding_manager, cache_manager]):
            raise HTTPException(
                status_code=503, detail="Service managers not fully initialized"
            )

        # Try to get from cache first (with error handling)
        try:
            cache_key = cache_manager.generate_key(
                "chat", query.question, query.n_results
            )
            cached_response = await cache_manager.get(cache_key)
            if cached_response:
                return ChatResponse(**cached_response)
        except Exception as cache_error:
            print(f"Cache error (continuing without cache): {cache_error}")

        # Get similar documents
        try:
            similar_docs = await embedding_manager.query_similar(
                query.question, query.n_results
            )
        except Exception as embedding_error:
            print(f"Embedding error: {embedding_error}")
            # If embeddings fail, provide a basic response without context
            similar_docs = []

        # Prepare context from similar documents
        context = [doc["content"] for doc in similar_docs] if similar_docs else []
        context_str = "\n".join(context) if context else "No relevant context found."

        # Prepare prompt for LLM
        prompt = f"""You are a helpful assistant for a Stock Control Management System. 
        Use the following context to answer the question. If you cannot find the answer 
        in the context, say so. Do not make up information.

        Context:
        {context_str}

        Question: {query.question}

        Answer:"""

        # Get response from Ollama
        try:
            response = ollama.chat(
                model=LLM_MODEL, messages=[{"role": "user", "content": prompt}]
            )
            answer = response["message"]["content"]
        except Exception as llm_error:
            print(f"LLM error: {llm_error}")
            # Fallback response when LLM is not available
            answer = f"I'm sorry, but I'm currently unable to process your question due to a service issue. Please try again later or contact support. Your question was: {query.question}"

        chat_response = ChatResponse(answer=answer, context=context)

        # Try to cache the response
        try:
            await cache_manager.set(cache_key, chat_response.model_dump())
        except Exception as cache_error:
            print(f"Failed to cache response: {cache_error}")

        return chat_response

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/refresh-embeddings")
async def refresh_embeddings():
    try:
        # Check if managers are initialized
        if not all([db_manager, embedding_manager, cache_manager]):
            raise HTTPException(
                status_code=503, detail="Service managers not fully initialized"
            )

        # Get all data from database
        data = db_manager.get_all_data()

        if not data:
            raise ValueError("No data retrieved from database")

        print(f"Retrieved {len(data)} documents from database")

        # Add documents to vector store
        await embedding_manager.add_documents(data)

        # Clear chat cache since embeddings have changed
        await cache_manager.clear_all()

        return {
            "message": f"Successfully refreshed embeddings for {len(data)} documents"
        }

    except Exception as e:
        print(f"Error in refresh_embeddings endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=API_HOST, port=API_PORT)
