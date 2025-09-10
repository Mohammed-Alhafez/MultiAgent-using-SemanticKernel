import os
from semantic_kernel import Kernel
from semantic_kernel.agents.chat_completion.chat_completion_agent import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import AzureChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior

from plugins.DBAgentPlugin import DBAgentPlugin
from plugins.MCPPlugin import MCPPlugin


class DBAgent(ChatCompletionAgent):
    def __init__(self):
        try:
            kernel = Kernel()

            chat_completion = AzureChatCompletion(
                deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_version="2024-12-01-preview",
                service_id="service1"
            )
            kernel.add_service(chat_completion)

 
            kernel.add_plugin(DBAgentPlugin(), plugin_name="DBAgent")
            kernel.add_plugin(MCPPlugin(), plugin_name="MCP")

            # call the parent constructor
            super().__init__(
                kernel=kernel,
                name="DBAgent",
                instructions="You manage employee tasks. Handle tasks like adding, listing, or marking them complete using your tools.",
            )

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
