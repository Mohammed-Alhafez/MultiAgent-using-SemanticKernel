import os
import asyncio
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior

from plugins.DBAgentPlugin import DBAgentPlugin

class DBAgent:
    def __init__(self):
        self.kernel = Kernel()
        
        # Get API credentials from environment variables
        api_key = os.getenv("AZURE_OPENAI_API_KEY", "BJ4W6pnGXVOoIBhNFCpiRAMHLQZCjtmSCRPjNzNohtim0pV7ygBiJQQJ99BIACHYHv6XJ3w3AAABACOGOaey")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://chatcompletionchat.openai.azure.com/")
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
        
        try:
            self.chat_completion = AzureChatCompletion(
                deployment_name=deployment_name,
                api_key=api_key,
                endpoint=endpoint,
                api_version="2024-12-01-preview",
            )

            self.kernel.add_service(self.chat_completion)
            self.kernel.add_plugin(DBAgentPlugin(), plugin_name="DBAgent")

            self.settings = AzureChatPromptExecutionSettings()
            self.settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
            self.initialized = True
        except Exception as e:
            print(f"Warning: Failed to initialize Azure OpenAI service: {e}")
            self.initialized = False

    async def run(self, user_input, history):
        if not self.initialized:
            return "Database agent is not properly initialized. Please check your Azure OpenAI configuration."
        
        try:
            # Add timeout to prevent hanging
            return await asyncio.wait_for(
                self.chat_completion.get_chat_message_content(
                    kernel=self.kernel,
                    chat_history=history,
                    settings=self.settings
                ),
                timeout=30.0  # 30 second timeout
            )
        except asyncio.TimeoutError:
            return "Request timed out. Please try again."
        except Exception as e:
            return f"Error processing request: {str(e)}"
