from semantic_kernel.functions import kernel_function
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

class InformativeAgent:
    def __init__(self):
        # Replace these with your actual Azure AI Search details
        self.endpoint = "https://company-policies-search.search.windows.net"
        self.index_name = "rag-1756823952605"
        self.api_key = "OMUHJTN8j7xvqG69hchBeWIGK3toXS8h1KSQoERR7OAzSeDkiN8t"

        self.search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=AzureKeyCredential(self.api_key)
        )

    @kernel_function(name="search_knowledge_base", description="Search company knowledge base for policies or guidelines.")
    def search_knowledge_base(self, query: str) -> str:
        results = self.search_client.search(query, top=3)

        hits = []
        for result in results:
            content = result.get("chunk", "")
            if content:
                hits.append(content)

        if not hits:
            return "No relevant information found in the company knowledge base."
        return "\n---\n".join(hits)
