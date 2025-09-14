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



# import os
# from semantic_kernel import Kernel
# from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
# from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import AzureChatPromptExecutionSettings
# from semantic_kernel.agents.chat_completion.chat_completion_agent import ChatCompletionAgent, ChatHistoryAgentThread
# from plugins.RoutingPlugin import RoutingPlugin 

# class Orchestrator:
#     def __init__(self, db_agent, informative_agent):
#         self.db_agent = db_agent
#         self.informative_agent = informative_agent


#         api_key = os.getenv("AZURE_OPENAI_API_KEY")
#         endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
#         deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

#         self.kernel = Kernel()
#         self.chat_completion = AzureChatCompletion(
#             deployment_name=deployment_name,
#             api_key=api_key,
#             endpoint=endpoint,
#             api_version="2024-12-01-preview",
#             service_id="service1"
#         )
#         self.kernel.add_service(self.chat_completion)
#         self.kernel.add_plugin(RoutingPlugin(), plugin_name="Router")

#         self.settings = AzureChatPromptExecutionSettings(service_id="service1")

#         self.router_agent = ChatCompletionAgent(
#             kernel=self.kernel,
#             name="RouterAgent",
#             instructions=(
#                 "You are a routing assistant. Given a user's input, decide which agent should handle it:\n"
#                 "- Use 'route_to_db' if the input is about tasks, assignments, or todos.\n"
#                 "- Use 'route_to_info' if it relates to company policies, guidelines, or rules.\n"
#                 "You must only reply with either 'DBAgent' or 'InformativeAgent'. Do not explain or add anything else."

#             ),
#         )



#     async def route(self, user_input: str):
#         thread = ChatHistoryAgentThread()

#         # Stream the response from router agent
#         async for response in self.router_agent.invoke(messages=user_input, thread=thread):
#             message = response.message
#             content = (message.content or "").lower()

#             # check: did the agent say which agent to route to?
#             if "dbagent" in content:
#                 return self.db_agent
#             elif "informativeagent" in content:
#                 return self.informative_agent

#         # fallback
#         return self.informative_agent

from semantic_kernel.agents import OrchestrationHandoffs
from Agents.agent_set import triage_agent , db_agent , informative_agent, mcp_agent
from semantic_kernel.contents import AuthorRole, ChatMessageContent, FunctionCallContent, FunctionResultContent, StreamingChatMessageContent
from semantic_kernel.agents import HandoffOrchestration


from db import store_chat_message  # Add this
import uuid

handoffs = (
    OrchestrationHandoffs()
    .add_many(
        source_agent=triage_agent.name,
        target_agents={
            db_agent.name: "Transfer to this agent if the issue is related to tasks or assignments.",
            informative_agent.name: "Transfer to this agent if the issue is related to company policies or information.",
            mcp_agent.name: "Transfer to this agent if a task was added or completed and a notification must be sent."
        },
    )
    .add(
        source_agent=db_agent.name,
        target_agent=triage_agent.name,
        description="Transfer to this agent if the issue is not task-related.",
    )
    .add(
        source_agent=db_agent.name,
        target_agent=mcp_agent.name,
        description="Transfer to this agent when a task is added or completed and an email notification needs to be sent.",
    )
    .add(
        source_agent=informative_agent.name,
        target_agent=triage_agent.name,
        description="Transfer to this agent if the issue is not information-related.",
    )
    .add(
        source_agent=mcp_agent.name,
        target_agent=triage_agent.name,
        description="Transfer to this agent after the notification has been sent.",
    )
    
)





# define how to display or log each agent’s response
# async def agent_response_callback(message: ChatMessageContent) -> None:
#     if message.content:
#         print(f"{message.name}> {message.content}")


# Track whether this is a new message
is_new_message = True

# Generate session ID once
session_id = str(uuid.uuid4())

def streaming_agent_response_callback(message: StreamingChatMessageContent, is_final: bool) -> None:
    """Streaming callback for agent responses."""
    global is_new_message

    if is_new_message:
        print(f"{message.name}> ", end="", flush=True)
        is_new_message = False

    # Print the streamed content
    if message.content:
        print(message.content, end="", flush=True)
        store_chat_message(
            session_id=session_id,
            role="agent",
            agent_name=message.name,
            content=message.content
        )

    # Tool/function call debug output
    for item in message.items:
        if isinstance(item, FunctionCallContent):
            print(f"\nCalling '{item.name}' with arguments '{item.arguments}'", end="", flush=True)
            store_chat_message(session_id, "function", item.name, f"Called with: {item.arguments}")
        if isinstance(item, FunctionResultContent):
            print(f"\nResult from '{item.name}' is '{item.result}'", end="", flush=True)
            store_chat_message(session_id, "function", item.name, f"Result: {item.result}")

    # Final chunk → newline
    if is_final:
        print()
        is_new_message = True



async def human_response_function(prompt: str = "") -> ChatMessageContent:
    user_input = input(f"User > {prompt}")
    store_chat_message(session_id=session_id, role="user", agent_name=None, content=user_input)
    return ChatMessageContent(role=AuthorRole.USER, content=user_input)

# Handoff Orchestration setup
handoff_orchestration = HandoffOrchestration(
    members=[triage_agent, db_agent, informative_agent, mcp_agent],
    handoffs=handoffs,
    #agent_response_callback= agent_response_callback,
    streaming_agent_response_callback=streaming_agent_response_callback,
    human_response_function=human_response_function,
)
