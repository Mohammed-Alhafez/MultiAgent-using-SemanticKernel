import asyncio
import os
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from semantic_kernel.functions.kernel_arguments import KernelArguments

load_dotenv("config.env")

async def main():
    async with MCPStdioPlugin(
        name="EmailMCP",
        description="Email notification plugin",
        command="python",
        args=["MCPServer.py"],
        env={
            "SENDER_EMAIL": os.getenv("SENDER_EMAIL"),
            "APP_PASSWORD": os.getenv("APP_PASSWORD"),
        },
    ) as email_plugin:
        print("Connected to EmailMCP")

        kernel = Kernel()
        kernel.add_plugin(email_plugin)

        # wrap arguments correctly
        args = KernelArguments(
            recipient_email="your-test-email@example.com",
            subject="Test MCP Notification",
            body="This is a test message sent through MCP."
        )

        result = await kernel.invoke(
            function_name="send_task_notification",
            plugin_name="EmailMCP",
            arguments=args
        )
        print("Result:", result)

if __name__ == "__main__":
    asyncio.run(main())
