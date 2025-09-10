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
from semantic_kernel.agents.chat_completion.chat_completion_agent import ChatCompletionAgent, ChatHistoryAgentThread
from plugins.RoutingPlugin import RoutingPlugin 

class Orchestrator:
    def __init__(self, db_agent, informative_agent):
        self.db_agent = db_agent
        self.informative_agent = informative_agent


        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

        self.kernel = Kernel()
        self.chat_completion = AzureChatCompletion(
            deployment_name=deployment_name,
            api_key=api_key,
            endpoint=endpoint,
            api_version="2024-12-01-preview",
            service_id="service1"
        )
        self.kernel.add_service(self.chat_completion)
        self.kernel.add_plugin(RoutingPlugin(), plugin_name="Router")

        self.settings = AzureChatPromptExecutionSettings(service_id="service1")

        self.router_agent = ChatCompletionAgent(
            kernel=self.kernel,
            name="RouterAgent",
            instructions=(
                "You are a routing assistant. Given a user's input, decide which agent should handle it:\n"
                "- Use 'route_to_db' if the input is about tasks, assignments, or todos.\n"
                "- Use 'route_to_info' if it relates to company policies, guidelines, or rules.\n"
                "You must only reply with either 'DBAgent' or 'InformativeAgent'. Do not explain or add anything else."

            ),
        )



    async def route(self, user_input: str):
        thread = ChatHistoryAgentThread()

        # Stream the response from router agent
        async for response in self.router_agent.invoke(messages=user_input, thread=thread):
            message = response.message
            content = (message.content or "").lower()

            # check: did the agent say which agent to route to?
            if "dbagent" in content:
                return self.db_agent
            elif "informativeagent" in content:
                return self.informative_agent

        # fallback
        return self.informative_agent

