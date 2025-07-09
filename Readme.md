I'll create a comprehensive markdown documentation with diagrams explaining the Stock Control Management System's RAG integration:
Ran tool

# Stock Control Management System - RAG Integration Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [Data Flow](#data-flow)
5. [Implementation Details](#implementation-details)
6. [Setup and Configuration](#setup-and-configuration)
7. [API Endpoints](#api-endpoints)
8. [Usage Examples](#usage-examples)

## Overview

The Stock Control Management System has been enhanced with a Retrieval Augmented Generation (RAG) capability, allowing users to interact with the system using natural language queries. This integration enables users to ask questions about inventory, sales, customers, and other aspects of the business, receiving contextually relevant answers based on the actual data in the system.

## Architecture

The system consists of three main parts:

1. **Frontend Layer**: PHP-based web interface with a new chat component
2. **Backend Layer**: Original PHP application with MySQL database
3. **RAG Service Layer**: New Python-based service handling AI interactions

### System Components Diagram

[See diagram above]

## Components

### 1. Frontend Components

- **Web Interface**: Traditional PHP-based CRUD interface
- **Chat Interface**: New AI-powered chat component
  ```php
  // Key files:
  pages/chat.php          # Chat interface
  includes/sidebar.php    # Navigation integration
  ```

### 2. Backend Components

- **PHP Application**: Handles traditional business logic
- **MySQL Database**: Stores all business data
  ```sql
  -- Key tables:
  product          # Product information
  customer         # Customer data
  transaction      # Sales transactions
  supplier         # Supplier information
  ```

### 3. RAG Service Components

- **FastAPI Service**: Main RAG service handler

  ```python
  # Key files:
  main.py          # API endpoints and core logic
  database.py      # Database connectivity
  embeddings.py    # Vector embeddings management
  cache_manager.py # Redis cache handling
  config.py        # Configuration management
  ```

- **ChromaDB**: Vector database for semantic search
- **Redis**: Caching layer for improved performance
- **Ollama**: Local LLM service
  - Embedding Model: `nomic-embed-text`
  - LLM Model: `smollm2:360m`

## Data Flow

Ran tool

## Implementation Details

### 1. Docker Configuration

```yaml
# Key services in docker-compose.yml
services:
  web: # PHP application
  db: # MySQL database
  rag_service: # RAG API service
  ollama: # LLM service
  redis: # Caching service
```

### 2. RAG Service Implementation

```python
# Main components:

# 1. Database Manager
class DatabaseManager:
    """Handles database operations and data extraction"""
    # Connects to MySQL
    # Extracts data for embedding
    # Formats data for vector store

# 2. Embedding Manager
class EmbeddingManager:
    """Manages vector embeddings and similarity search"""
    # Generates embeddings using Ollama
    # Stores embeddings in ChromaDB
    # Performs similarity search

# 3. Cache Manager
class CacheManager:
    """Handles Redis caching"""
    # Caches chat responses
    # Manages cache invalidation
    # Improves response time
```

### 3. Chat Interface Integration

```javascript
// Frontend chat functionality
async function sendMessage() {
  // Sends user message to RAG service
  // Handles response display
  // Manages chat UI
}
```

## Setup and Configuration

### Environment Variables

```python
# RAG Service Configuration
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "scmspassword")
DB_NAME = os.getenv("DB_NAME", "scms")

# Model Configuration
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "smollm2:360m"

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_CACHE_TTL = 3600  # 1 hour
```

## API Endpoints

### 1. Chat Endpoint

```http
POST /chat
Content-Type: application/json

{
    "question": "What are the most expensive products?",
    "n_results": 5
}
```

### 2. Refresh Embeddings Endpoint

```http
POST /refresh-embeddings
```

## Usage Examples

### 1. Product Queries

```json
// Question: "What are our best-selling products?"
{
    "question": "What are our best-selling products?",
    "n_results": 5
}

// Response:
{
    "answer": "Based on the transaction history, the best-selling products are...",
    "context": ["List of relevant transactions..."]
}
```

### 2. Customer Insights

```json
// Question: "Who are our most valuable customers?"
{
  "question": "Who are our most valuable customers?",
  "n_results": 5
}
```

### 3. Inventory Management

```json
// Question: "Which products are low in stock?"
{
  "question": "Which products are low in stock?",
  "n_results": 5
}
```

## Performance Optimizations

1. **Redis Caching**

   - Caches frequent queries
   - Reduces database load
   - Improves response time

2. **Batch Processing**

   - Processes embeddings in batches
   - Optimizes database queries
   - Efficient vector storage

3. **Health Checks**
   - Ensures service availability
   - Manages dependencies
   - Graceful error handling
     Ran tool
     This documentation provides a comprehensive overview of the RAG integration into the Stock Control Management System. The system combines traditional database operations with modern AI capabilities, enabling natural language interactions while maintaining performance through caching and optimized data processing.

Would you like me to expand on any particular section or add more specific examples?
