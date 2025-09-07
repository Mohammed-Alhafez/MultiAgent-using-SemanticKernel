from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import AzureChatPromptExecutionSettings

class Orchestrator:
    def __init__(self, chat_service: AzureChatCompletion):
        self.chat_service = chat_service

    async def classify_intent(self, user_input: str) -> str:
        prompt = (
            "Classify the user's request into one of the following intents:\n"
            "- task_operation: if the user wants to create, update, complete, delete, or view tasks\n"
            "- policy_inquiry: if the user is asking about company policies, procedures, or guidelines\n\n"
            f"User request: {user_input}\n"
            "Intent:"
        )

        history = ChatHistory()
        history.add_user_message(prompt)

        settings = AzureChatPromptExecutionSettings()
        response = await self.chat_service.get_chat_message_content(
            chat_history=history,
            settings=settings,
        )

        intent = str(response).strip().lower()
        if "task" in intent:
            return "task_operation"
        elif "policy" in intent:
            return "policy_inquiry"
        else:
            return "unknown"
