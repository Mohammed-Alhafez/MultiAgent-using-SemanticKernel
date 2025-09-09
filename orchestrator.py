# class Orchestrator:
#     def __init__(self, db_agent, informative_agent):
#         self.db_agent = db_agent
#         self.informative_agent = informative_agent

#     def route(self, user_input: str):
#         """Very basic routing logic. Can be replaced with intent classification."""
#         if any(keyword in user_input.lower() for keyword in ["task", "todo", "assign", "complete", "pending"]):
#             return self.db_agent
#         elif any(keyword in user_input.lower() for keyword in ["policy", "guideline", "rules", "search", "information"]):
#             return self.informative_agent
#         else:
#             return self.informative_agent  # Default fallback



import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import AzureChatPromptExecutionSettings
from semantic_kernel.contents.chat_history import ChatHistory

class Orchestrator:
    def __init__(self, db_agent, informative_agent):
        self.db_agent = db_agent
        self.informative_agent = informative_agent

        # Setup Azure OpenAI for routing
        api_key = os.getenv("AZURE_OPENAI_API_KEY", "BJ4W6pnGXVOoIBhNFCpiRAMHLQZCjtmSCRPjNzNohtim0pV7ygBiJQQJ99BIACHYHv6XJ3w3AAABACOGOaey")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://chatcompletionchat.openai.azure.com/")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")

        self.kernel = Kernel()
        self.chat_completion = AzureChatCompletion(
            deployment_name=deployment_name,
            api_key=api_key,
            endpoint=endpoint,
            api_version="2024-12-01-preview",
        )
        self.kernel.add_service(self.chat_completion)

        self.settings = AzureChatPromptExecutionSettings()



    async def route(self, user_input: str):
        system_prompt = (
            "You are a routing assistant. Given a user's input, decide which agent should handle it:\n"
            "- 'DBAgent' if the user input relates to tasks, todos, assignments, completion, or pending items.\n"
            "- 'InformativeAgent' if it relates to policy, guidelines, rules, or general information.\n"
            "Respond ONLY with 'DBAgent' or 'InformativeAgent'.\n\n"
            f"User Input: {user_input}\n"
            "Which agent should handle this?"
        )

        # Use ChatHistory instead of a raw list
        chat_history = ChatHistory()
        chat_history.add_system_message(system_prompt)

        try:
            result = await self.chat_completion.get_chat_message_content(
                kernel=self.kernel,
                chat_history=chat_history,
                settings=self.settings
            )

            content = result.content.strip().lower()

            if "dbagent" in content:
                return self.db_agent
            else:
                return self.informative_agent
        except Exception as e:
            print(f"Routing failed, using fallback logic. Error: {e}")
            return self.informative_agent  # fallback default
