import os
from dotenv import load_dotenv
from semantic_kernel.connectors.mcp import MCPSsePlugin
from semantic_kernel.functions import KernelFunctionMetadata
from semantic_kernel import Kernel
import asyncio
load_dotenv("config.env")

kernel = Kernel()

async def create_email_mcp_plugin():
    plugin = MCPSsePlugin(
        name="EmailMCP",
        description="Email notification plugin",
        url="http://127.0.0.1:8080/sse",
        load_tools=True,   
        load_prompts=False
    )

    await plugin.connect()
    await plugin.load_tools()
    kernel.add_plugin(plugin)
    
    def _no_deepcopy(self, memo):
        return self
    plugin.__deepcopy__ = _no_deepcopy.__get__(plugin, type(plugin))

    
    # Introspect the plugin directly
    print("[DEBUG] Plugin functions ready:")
    for attr in dir(plugin):
        if not attr.startswith("_"):
            if callable(getattr(plugin, attr)):
                print("  -", attr)
    
    return plugin





# import os
# import asyncio
# from dotenv import load_dotenv
# from semantic_kernel import Kernel
# from semantic_kernel.connectors.mcp import MCPStdioPlugin

# load_dotenv("config.env")

# async def create_email_mcp_plugin():
#     # MCPStdio launches your EmailMCP server (the FastMCP you wrote)
#     plugin = MCPStdioPlugin(
#         name="EmailMCP",
#         description="Email notification plugin",
#         command="python",
#         args=["MCPServer.py"],  # path to your FastMCP server file
#         env={
#             "SENDER_EMAIL": os.getenv("SENDER_EMAIL"),
#             "APP_PASSWORD": os.getenv("APP_PASSWORD"),
#         },
#     )
#     await plugin.connect()
    
#     await plugin.load_tools()
#     def _no_deepcopy(self, memo):
#         return self
#     plugin.__deepcopy__ = _no_deepcopy.__get__(plugin, type(plugin))

#     # Use async context manager for lifecycle management
#     async with plugin:
#         kernel = Kernel()
#         kernel.add_plugin(plugin)


#         return plugin

