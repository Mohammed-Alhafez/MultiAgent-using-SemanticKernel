# Azure AI Search Architecture in SMNT-KRNL

## Overview

Your system uses **Azure AI Search** (formerly Azure Cognitive Search) with a **vector-based search architecture** for intelligent information retrieval from company policies stored in Azure Blob Storage.

## Architecture Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    AZURE AI SEARCH ARCHITECTURE                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │AZURE BLOB   │    │EMBEDDING    │    │AZURE AI     │         │
│  │STORAGE      │    │MODEL        │    │SEARCH       │         │
│  │             │    │             │    │             │         │
│  │• Company    │    │• Azure      │    │• Vector     │         │
│  │  Policies   │    │  OpenAI     │    │  Index      │         │
│  │• Documents  │    │  Embeddings │    │• Semantic   │         │
│  │• PDFs/TXT   │    │• Text-      │    │  Search     │         │
│  │             │    │  ada-002    │    │• Hybrid     │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                DATA PIPELINE                               │ │
│  │  1. Document Ingestion → 2. Chunking → 3. Embedding       │ │
│  │  4. Vector Storage → 5. Index Creation → 6. Search Ready  │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## How It Works in Your System

### 1. **Data Source: Azure Blob Storage**
```
┌─────────────────────────────────────────────────────────────┐
│                AZURE BLOB STORAGE                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📁 company-policies/                                       │
│  ├── 📄 vacation-policy.pdf                                │
│  ├── 📄 hr-guidelines.docx                                 │
│  ├── 📄 code-of-conduct.txt                                │
│  ├── 📄 remote-work-policy.pdf                             │
│  └── 📄 benefits-overview.docx                             │
│                                                             │
│  • Documents are stored as blobs                           │
│  • Various formats: PDF, DOCX, TXT                         │
│  • Organized in containers/folders                         │
└─────────────────────────────────────────────────────────────┘
```

### 2. **Embedding Process**
```
┌─────────────────────────────────────────────────────────────┐
│                EMBEDDING PIPELINE                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📄 Document → 🔪 Chunking → 🧠 Embedding → 💾 Storage     │
│                                                             │
│  1. DOCUMENT INGESTION:                                    │
│     • Azure Search Indexer pulls documents from Blob       │
│     • Extracts text content from PDFs, DOCX, TXT           │
│     • Handles different file formats automatically         │
│                                                             │
│  2. CHUNKING STRATEGY:                                     │
│     • Documents split into smaller chunks (512-1024 tokens)│
│     • Overlapping chunks for context preservation          │
│     • Metadata attached (source, page, section)            │
│                                                             │
│  3. EMBEDDING GENERATION:                                  │
│     • Uses Azure OpenAI text-embedding-ada-002 model       │
│     • Each chunk converted to 1536-dimensional vector      │
│     • Semantic meaning captured in vector space            │
│                                                             │
│  4. VECTOR STORAGE:                                        │
│     • Vectors stored in Azure AI Search index              │
│     • Hybrid search capability (vector + keyword)          │
│     • Fast similarity search using cosine similarity       │
└─────────────────────────────────────────────────────────────┘
```

### 3. **Search Index Structure**
```json
{
  "name": "rag-1756823952605",
  "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "key": true
    },
    {
      "name": "chunk",
      "type": "Edm.String",
      "searchable": true,
      "retrievable": true
    },
    {
      "name": "content_vector",
      "type": "Collection(Edm.Single)",
      "dimensions": 1536,
      "vectorSearchProfile": "default-vector-profile"
    },
    {
      "name": "source",
      "type": "Edm.String",
      "filterable": true
    },
    {
      "name": "page",
      "type": "Edm.Int32",
      "filterable": true
    }
  ],
  "vectorSearch": {
    "profiles": [
      {
        "name": "default-vector-profile",
        "algorithm": "hnsw"
      }
    ]
  }
}
```

## Search Process in Your System

### 1. **User Query Processing**
```python
# In InformativeAgentPlugin.py
def search_knowledge_base(self, query: str) -> str:
    # Simple text search (can be enhanced to vector search)
    results = self.search_client.search(query, top=3)
    
    hits = []
    for result in results:  
        content = result.get("chunk", "")
        if content:
            hits.append(content)
    
    return "\n---\n".join(hits)
```

### 2. **Current Implementation Analysis**
Your current implementation uses **keyword-based search**, not vector search. Here's what's happening:

```python
# Current: Keyword Search
results = self.search_client.search(query, top=3)
```

**This searches for exact keyword matches in the "chunk" field.**

### 3. **Enhanced Vector Search Implementation**
To enable true vector-based semantic search, you would need:

```python
def search_knowledge_base_vector(self, query: str) -> str:
    # 1. Generate embedding for user query
    query_embedding = self.generate_embedding(query)
    
    # 2. Perform vector similarity search
    vector_search = {
        "vector": {
            "value": query_embedding,
            "k": 3
        },
        "fields": "content_vector"
    }
    
    # 3. Hybrid search (vector + keyword)
    results = self.search_client.search(
        search_text=query,  # Keyword search
        vector_queries=[vector_search],  # Vector search
        top=3
    )
    
    return self.format_results(results)
```

## Vector Search vs Keyword Search

### **Current: Keyword Search**
```
User Query: "What is the vacation policy?"
Search Process: Looks for documents containing "vacation" AND "policy"
Results: Only exact keyword matches
Limitations: Misses semantic variations like "annual leave", "time off"
```

### **Enhanced: Vector Search**
```
User Query: "What is the vacation policy?"
Search Process: 
1. Converts query to vector: [0.1, -0.3, 0.8, ...]
2. Finds similar vectors in embedding space
3. Returns semantically similar content
Results: Finds "annual leave", "time off", "holiday policy", etc.
```

## Configuration Details

### **Your Current Setup:**
```env
AZURE_SEARCH_ENDPOINT=https://company-policies-search.search.windows.net
AZURE_SEARCH_INDEX=rag-1756823952605
AZURE_SEARCH_API_KEY=OMUHJTN8j7xvqG69hchBeWIGK3toXS8h1KSQoERR7OAzSeDkiN8t
```

### **Index Configuration:**
- **Index Name**: `rag-1756823952605`
- **Search Service**: `company-policies-search`
- **Region**: Likely in Azure region where your search service is deployed

## Data Flow in Your System

```
┌─────────────────────────────────────────────────────────────┐
│                SEARCH FLOW IN SMNT-KRNL                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. USER QUERY: "What is the vacation policy?"             │
│     │                                                       │
│     ▼                                                       │
│  2. TRIAGE AGENT: Routes to InformativeAgent               │
│     │                                                       │
│     ▼                                                       │
│  3. INFORMATIVE AGENT: Calls search_knowledge_base()       │
│     │                                                       │
│     ▼                                                       │
│  4. AZURE SEARCH: Searches index "rag-1756823952605"       │
│     │                                                       │
│     ▼                                                       │
│  5. RESULTS: Returns top 3 matching chunks                 │
│     │                                                       │
│     ▼                                                       │
│  6. RESPONSE: Formatted policy information                 │
└─────────────────────────────────────────────────────────────┘
```

## Performance Characteristics

### **Current Keyword Search:**
- ⚡ **Speed**: Very fast (< 100ms)
- 🎯 **Precision**: High for exact matches
- 📈 **Recall**: Low for semantic variations
- 💰 **Cost**: Low (no embedding generation)

### **Vector Search (if implemented):**
- ⚡ **Speed**: Fast (200-500ms)
- 🎯 **Precision**: High for semantic matches
- 📈 **Recall**: High for concept variations
- 💰 **Cost**: Higher (embedding generation)

## Recommendations for Enhancement

### 1. **Enable Vector Search**
```python
# Add to InformativeAgentPlugin
def generate_embedding(self, text: str) -> list:
    # Use Azure OpenAI embedding model
    response = self.openai_client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding
```

### 2. **Hybrid Search Implementation**
```python
def search_knowledge_base_hybrid(self, query: str) -> str:
    # Combine keyword and vector search
    vector_query = {
        "vector": {
            "value": self.generate_embedding(query),
            "k": 3
        },
        "fields": "content_vector"
    }
    
    results = self.search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        top=3
    )
    
    return self.format_results(results)
```

### 3. **Enhanced Result Formatting**
```python
def format_results(self, results) -> str:
    formatted_results = []
    for result in results:
        content = result.get("chunk", "")
        source = result.get("source", "Unknown")
        score = result.get("@search.score", 0)
        
        formatted_results.append(
            f"📄 Source: {source}\n"
            f"📊 Relevance: {score:.2f}\n"
            f"📝 Content: {content}\n"
            f"{'─' * 50}"
        )
    
    return "\n".join(formatted_results)
```

## Summary

**Your current system uses Azure AI Search with keyword-based search**, not vector search. The documents are stored in Azure Blob Storage and indexed in Azure AI Search, but the search is currently based on text matching rather than semantic similarity.

**To enable true vector-based search**, you would need to:
1. Ensure your search index has vector fields
2. Generate embeddings for user queries
3. Use vector search queries in your search calls
4. Implement hybrid search for best results

The infrastructure is there (Azure AI Search supports vector search), but the implementation in your code is currently using traditional keyword search.



