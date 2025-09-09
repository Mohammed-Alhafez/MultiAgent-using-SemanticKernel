# import asyncio
# import logging
# from semantic_kernel import Kernel
# from semantic_kernel.utils.logging import setup_logging
# from semantic_kernel.functions import kernel_function
# from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
# from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
# from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
# from semantic_kernel.contents.chat_history import ChatHistory
# from semantic_kernel.functions.kernel_arguments import KernelArguments


# from db import init_db
# from plugins.DBAgentPlugin import DBAgent
# from plugins.InformativeAgentPlugin import InformativeAgent
# from orchestrator import Orchestrator

# from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
#     AzureChatPromptExecutionSettings,
# )

# async def main():
#     # Initialize the kernel and DB 
#     kernel = Kernel()

#     init_db()

#     # Add Azure OpenAI chat completion
#     chat_completion = AzureChatCompletion(
#         deployment_name="gpt-4",
#         api_key="BJ4W6pnGXVOoIBhNFCpiRAMHLQZCjtmSCRPjNzNohtim0pV7ygBiJQQJ99BIACHYHv6XJ3w3AAABACOGOaey",
#         endpoint="https://chatcompletionchat.openai.azure.com/",
#         api_version = "2024-12-01-preview",
#     )
#     kernel.add_service(chat_completion)


#     # Set the logging level for  semantic_kernel.kernel to DEBUG.
#     setup_logging()
#     logging.getLogger("kernel").setLevel(logging.DEBUG)

#     kernel.add_plugin(
#         DBAgent(),
#         plugin_name="DBAgent",
#     )    

#     kernel.add_plugin(
#         InformativeAgent(),
#         plugin_name="InformativeAgent",
#     )


#     # Enable planning
#     execution_settings = AzureChatPromptExecutionSettings()
#     execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto() 
#     # this method let gpt4 to call invoke the required fun in a certain plugin based on the functions names/dscr/args
#     # and also based on user query and chat history

#     # Create a history of the conversation
#     history = ChatHistory()

#     # Initiate a back-and-forth chat
#     # userInput = None
#     while True:
#         # Collect user input
#         userInput = input("User > ")

#         # Terminate the loop if the user says "exit"
#         if userInput == "exit":
#             break

#         # Add user input to the history
#         history.add_user_message(userInput)

#         # Get the response from the AI
#         result = await chat_completion.get_chat_message_content(
#             chat_history=history,
#             settings=execution_settings,
#             kernel=kernel,
#         )

#         # Print the results
#         print("Assistant > " + str(result))

#         # Add the message from the agent to the chat history
#         history.add_message(result)


# # Run the main function
# if __name__ == "__main__":
#     asyncio.run(main())


















# import asyncio
# import logging
# from semantic_kernel import Kernel
# from semantic_kernel.utils.logging import setup_logging
# from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
# from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
# from semantic_kernel.contents.chat_history import ChatHistory

# from db import init_db
# from plugins.DBAgent import DBAgent
# from plugins.InformativeAgent import InformativeAgent
# from orchestrator import Orchestrator

# from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
#     AzureChatPromptExecutionSettings,
# )


# async def main():
#     # Initialize kernel and DB
#     kernel = Kernel()
#     init_db()

#     # Add Azure OpenAI chat completion
#     chat_completion = AzureChatCompletion(
#         deployment_name="gpt-4",
#         api_key="BJ4W6pnGXVOoIBhNFCpiRAMHLQZCjtmSCRPjNzNohtim0pV7ygBiJQQJ99BIACHYHv6XJ3w3AAABACOGOaey",
#         endpoint="https://chatcompletionchat.openai.azure.com/",
#         api_version="2024-12-01-preview",
#     )
#     kernel.add_service(chat_completion)

#     # Logging
#     setup_logging()
#     logging.getLogger("kernel").setLevel(logging.DEBUG)

#     # Register plugins
#     kernel.add_plugin(DBAgent(), plugin_name="DBAgent")
#     kernel.add_plugin(InformativeAgent(), plugin_name="InformativeAgent")

#     # Orchestrator for intent classification
#     orchestrator = Orchestrator(chat_completion)

#     # Start interactive chat loop
#     await run_chat(kernel, orchestrator)


# async def run_chat(kernel, orchestrator):
#     while True:
#         user_input = input("User > ")

#         if user_input.lower() == "exit":
#             break

#         # Step 1: Classify the user's intent
#         intent = await orchestrator.classify_intent(user_input)

#         # Step 2: Use GPT-4 with Auto() to pick function and parse args
#         if intent in ["task_operation", "policy_inquiry"]:
#             history = ChatHistory()
#             history.add_user_message(user_input)

#             execution_settings = AzureChatPromptExecutionSettings()
#             execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

#             result = await orchestrator.chat_service.get_chat_message_content(
#                 chat_history=history,
#                 settings=execution_settings,
#                 kernel=kernel,
#             )

#             print("Assistant > " + str(result))

#             # Step 3: Conditional follow-up (e.g., MCPAgent)
#             if intent == "task_operation" and "task added" in str(result).lower():
#                 print("📢 MCPAgent would be triggered here to send an email notification.")

#         else:
#             print("Assistant > Sorry, I couldn't understand your request.")


# # Entry point
# if __name__ == "__main__":
#     asyncio.run(main())





import asyncio
from semantic_kernel.contents.chat_history import ChatHistory
from db import init_db
from Agents.DBAgent import DBAgent
from Agents.informativeAgent import InformativeAgent
from orchestrator import Orchestrator

async def main():
    init_db()

    db_agent = DBAgent()
    informative_agent = InformativeAgent()
    orchestrator = Orchestrator(db_agent, informative_agent)

    history = ChatHistory()

    while True:
        user_input = input("User > ")

        if user_input.lower() == "exit":
            break

        history.add_user_message(user_input)

        agent = await orchestrator.route(user_input)
        result = await agent.run(user_input, history)

        print("Assistant >", str(result))
        history.add_message(result)

if __name__ == "__main__":
    asyncio.run(main())
