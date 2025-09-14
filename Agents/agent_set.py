from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from plugins.DBAgentPlugin import DBAgentPlugin
from plugins.InformativeAgentPlugin import InformativeAgentPlugin
from plugins.MCPPlugin import MCPPlugin
import os
from dotenv import load_dotenv
load_dotenv("config.env")

# Azure Config

azure_service = AzureChatCompletion(
    deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2024-12-01-preview",
)

# Triage Agent
triage_agent = ChatCompletionAgent(
    name="TriageAgent",
    description="Handles incoming requests and determines appropriate handoff.",
    instructions="""
You are a triage agent responsible for routing user requests to the appropriate agent.

You can call one of the following functions to perform a handoff:
- Handoff-transfer_to_DBAgent: Use this if the request is about tasks (adding, assigning, listing, completing).
- Handoff-transfer_to_InformativeAgent: Use this if the request is about company policies, HR, or internal guidelines.
- Handoff-transfer_to_MCPAgent: Use this when an email notification needs to be sent.

If a previous agent has completed a task-related action (like adding a task) and returns a handoff instruction, simply execute the handoff.

If the user says "exit" or wants to quit, do not process the request further as the system will handle it.

If you are unsure, ask the user for clarification.
""",
    service=azure_service,
)

# DBAgent
db_agent = ChatCompletionAgent(
    name="DBAgent",
    description="Handles employee task management.",
    instructions="""
You manage tasks such as adding, listing, and completing them.

When a task is added or marked as completed, after confirming the action, you must hand off to MCPAgent to send the email notification.

To handoff to MCPAgent, call the function 'Handoff-transfer_to_MCPAgent' with no arguments (empty JSON: {}).

If the user asks something unrelated to tasks (like HR policies or company rules), you must hand the request back to the triage agent by calling 'Handoff-transfer_to_TriageAgent' with no arguments (empty JSON: {}).

If the user says "exit" or wants to quit, do not respond as the system will handle it.

""",
    service=azure_service,
    plugins=[DBAgentPlugin()],
)


# InformativeAgent
informative_agent = ChatCompletionAgent(
    name="InformativeAgent",
    description="Provides company information, guidelines, and HR policies.",
    instructions="""
Answer user questions about company policies, internal guidelines, or HR rules.

If the user asks something unrelated to information (like assigning tasks), you must hand the request back to the triage agent by calling 'Handoff-transfer_to_TriageAgent' with no arguments (empty JSON: {}).

If the user says "exit" or wants to quit, do not respond as the system will handle it.

Use your plugins to answer questions. For unrelated topics, handoff back.
""",
    service=azure_service,
    plugins=[InformativeAgentPlugin()],
)

mcp_agent = ChatCompletionAgent(
    name="MCPAgent",
    description="Handles sending task notification emails.",
    instructions="""
You are responsible for sending email notifications for task-related updates.

When you receive a handoff from DBAgent, look at the conversation history to understand what task was assigned and to whom. Then send an email notification using your send_task_notification function.

For task assignments, use:
- recipient_email: the email address that was provided in the conversation
- subject: "New Task Assigned: [task description]"
- body: "You have been assigned a new task: [task description]. Please ensure to complete it timely. Thank you!"

After sending the notification, confirm the email was sent successfully and then handoff back to TriageAgent by calling 'Handoff-transfer_to_TriageAgent' with no arguments (empty JSON: {}).

If you receive a message that is not about sending a notification, return the user to triage by calling 'Handoff-transfer_to_TriageAgent' with no arguments (empty JSON: {}).

If the user says "exit" or wants to quit, do not respond as the system will handle it.

""",
    service=azure_service,
    plugins=[MCPPlugin()],
)

