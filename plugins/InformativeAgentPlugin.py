import os
from semantic_kernel.functions import kernel_function
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

class InformativeAgent:
    def __init__(self):
        # Get Azure Search credentials from environment variables
        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT", "https://company-policies-search.search.windows.net")
        self.index_name = os.getenv("AZURE_SEARCH_INDEX", "rag-1756823952605")
        self.api_key = os.getenv("AZURE_SEARCH_API_KEY", "OMUHJTN8j7xvqG69hchBeWIGK3toXS8h1KSQoERR7OAzSeDkiN8t")

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

    @kernel_function(name="search_knowledge_base", description="Search company knowledge base for policies or guidelines.")
    def search_knowledge_base(self, query: str) -> str:
        if not self.initialized:
            return "Azure Search is not properly initialized. Please check your configuration."
        
        try:
            results = self.search_client.search(query, top=3)

            hits = []
            for result in results:  
                content = result.get("chunk", "")
                if content:
                    hits.append(content)

            if not hits:
                return "No relevant information found in the company knowledge base."
            return "\n---\n".join(hits)
        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"
