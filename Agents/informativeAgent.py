import os
import asyncio
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior

from plugins.InformativeAgentPlugin import InformativeAgentPlugin
from semantic_kernel.agents import ChatCompletionAgent

class InformativeAgent(ChatCompletionAgent):
    def __init__(self):
        kernel = Kernel()
        
        # Get API credentials from environment variables
        api_key = os.getenv("AZURE_OPENAI_API_KEY", "BJ4W6pnGXVOoIBhNFCpiRAMHLQZCjtmSCRPjNzNohtim0pV7ygBiJQQJ99BIACHYHv6XJ3w3AAABACOGOaey")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://chatcompletionchat.openai.azure.com/")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
        
        try:
            chat_completion = AzureChatCompletion(
                deployment_name=deployment_name,
                api_key=api_key,
                endpoint=endpoint,
                api_version="2024-12-01-preview",
            )

            kernel.add_service(chat_completion)
            kernel.add_plugin(InformativeAgentPlugin(), plugin_name="InformativeAgent")     

            super().__init__(
                kernel=kernel,
                name="InformativeAgent",
                instructions="You help users find information from the company knowledge base. Use your tools to search and retrieve information.",
            )

       

            # self.settings = AzureChatPromptExecutionSettings()
            # self.settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        except Exception as e:
            print(f"Warning: Failed to initialize Azure OpenAI service: {e}")


    async def run(self, user_input, history):
        response = ""
        async for message in self.invoke_stream(history):
            if message.content:
                print(message.content, end="", flush=True)
                response += str(message.content or "")
        print()  # Newline after full message
        return response

