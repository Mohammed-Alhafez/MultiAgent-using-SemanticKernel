import os
from semantic_kernel.functions import kernel_function
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding
from azure.search.documents.models import VectorizableTextQuery, QueryType, QueryCaptionType, QueryAnswerType

class InformativeAgentPlugin:
    def __init__(self):
        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.index_name = os.getenv("AZURE_SEARCH_INDEX")
        self.api_key = os.getenv("AZURE_SEARCH_API_KEY")
        try:
            self.search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=self.index_name,
                credential=AzureKeyCredential(self.api_key)
            )
            self.initialized = True
        except Exception as e:
            print(f"Warning: Failed to initialize Azure Search client: {e}")
            self.initialized = False

    async def _get_embedding(self, text: str) -> list[float]:
        embedding_service = AzureTextEmbedding(
            deployment_name="text-embedding-3-small",
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version="2024-12-01-preview"
        )
        response = await embedding_service.generate_embeddings([text])
        return response[0]

    @kernel_function(
        name="hybrid_search_knowledge_base",
        description="Performs hybrid semantic search (keyword + vector + captions + answers) on company knowledge base"
    )
    async def hybrid_search_knowledge_base(self, query: str) -> str:
        if not self.initialized:
            return "Azure Search client not initialized."

        try:
            query_vector = await self._get_embedding(query)
            vector_query = VectorizableTextQuery(
                text=query,
                fields="text_vector",
                k_nearest_neighbors=3,
                exhaustive=True
            )
            results = self.search_client.search(
                search_text=query,
                vector_queries=[vector_query],
                query_type=QueryType.SEMANTIC,
                semantic_configuration_name="rag-1756823952605-semantic-configuration",
                query_caption="extractive",        # Use string for maximum compatibility
                query_answer="extractive",         # THIS IS THE IMPORTANT FIX
                query_answer_count=3,
                top=3,
                include_total_count=True,
                select=["parent_id", "chunk_id", "chunk"]
            )

            # Try to use semantic answers first
            semantic_answers = results.get_answers() if hasattr(results, "get_answers") else []
            if semantic_answers:
                for answer in semantic_answers:
                    if answer.highlights:
                        return answer.highlights
                    elif answer.text:
                        return answer.text

            # Otherwise, use captions or chunks from the top results
            for result in results:
                captions = result.get("@search.captions", [])
                if captions and isinstance(captions, list) and len(captions) > 0:
                    caption = captions[0]
                    if hasattr(caption, "highlights") and caption.highlights:
                        return caption.highlights
                    elif hasattr(caption, "text"):
                        return caption.text
                # Fallback to chunk field
                if result.get("chunk"):
                    return result["chunk"]

            return "No relevant info found."

        except Exception as e:
            return f"Error during hybrid search: {str(e)}"


    # @kernel_function(name="search_knowledge_base", description="Search company knowledge base for policies or guidelines.")
    # def search_knowledge_base(self, query: str) -> str:
    #     if not self.initialized:
    #         return "Azure Search is not properly initialized. Please check your configuration."
        
    #     try:
    #         results = self.search_client.search(query, top=3)

    #         hits = []
    #         for result in results:  
    #             content = result.get("chunk", "")
    #             if content:
    #                 hits.append(content)

    #         if not hits:
    #             return "No relevant information found in the company knowledge base."
    #         return "\n---\n".join(hits)
    #     except Exception as e:
    #         return f"Error searching knowledge base: {str(e)}"
