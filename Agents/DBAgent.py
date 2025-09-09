import os
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior

from plugins.DBAgentPlugin import DBAgentPlugin
from plugins.MCPPlugin import MCPPlugin


class DBAgent(ChatCompletionAgent):
    def __init__(self):
        try:
            # ✅ 1. Initialize kernel
            kernel = Kernel()

            # ✅ 2. Create and add AzureChatCompletion service to kernel
            chat_completion = AzureChatCompletion(
                deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY", "BJ4W6pnGXVOoIBhNFCpiRAMHLQZCjtmSCRPjNzNohtim0pV7ygBiJQQJ99BIACHYHv6XJ3w3AAABACOGOaey"),
                endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://chatcompletionchat.openai.azure.com/"),
                api_version="2024-12-01-preview",
                service_id="service1"
            )
            kernel.add_service(chat_completion)

            # ✅ 3. Add plugin to kernel
            kernel.add_plugin(DBAgentPlugin(), plugin_name="DBAgent")
            kernel.add_plugin(MCPPlugin(), plugin_name="MCP")

            # ✅ 4. Now call the parent constructor with the ready-to-use kernel
            super().__init__(
                kernel=kernel,
                name="DBAgent",
                instructions="You manage employee tasks. Handle tasks like adding, listing, or marking them complete using your tools.",
            )

            # ✅ 5. Set execution behavior
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
        print()
        return response
