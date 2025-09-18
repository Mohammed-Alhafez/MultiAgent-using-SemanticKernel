#!/usr/bin/env python3
"""
Test script for MCP Email Server
This script tests the MCP email server functionality independently.
"""

import asyncio
import sys
from pathlib import Path
from semantic_kernel.plugins.mcp_plugin import MCPStdioPlugin

async def test_mcp_email_server():
    """Test the MCP email server functionality."""
    
    # Create MCP plugin
    mcp_plugin = MCPStdioPlugin(
        name="EmailNotificationServer",
        command="python",
        args=[str(Path("plugins/mcp_email_server.py"))],
    )
    
    try:
        print("🔌 Connecting to MCP email server...")
        await mcp_plugin.connect()
        print("✅ Connected successfully!")
        
        # Test the available functions
        print("\n📋 Available functions:")
        for function in mcp_plugin.functions:
            print(f"  - {function.name}: {function.description}")
        
        # Test sending a task assignment notification
        print("\n📧 Testing task assignment notification...")
        result = await mcp_plugin.invoke_function(
            "send_task_assignment_notification",
            {
                "recipient_email": "test@example.com",
                "task_description": "Review project documentation",
                "assigned_by": "John Doe",
                "due_date": "2024-01-15"
            }
        )
        print(f"Result: {result}")
        
        # Test sending a task completion notification
        print("\n✅ Testing task completion notification...")
        result = await mcp_plugin.invoke_function(
            "send_task_completion_notification",
            {
                "recipient_email": "test@example.com",
                "task_description": "Review project documentation",
                "completed_by": "Jane Smith"
            }
        )
        print(f"Result: {result}")
        
        # Test sending a custom notification
        print("\n📨 Testing custom notification...")
        result = await mcp_plugin.invoke_function(
            "send_task_notification",
            {
                "recipient_email": "test@example.com",
                "subject": "Test Email",
                "body": "This is a test email from the MCP server."
            }
        )
        print(f"Result: {result}")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False
    finally:
        try:
            await mcp_plugin.close()
            print("🔌 MCP plugin connection closed.")
        except:
            pass
    
    return True

if __name__ == "__main__":
    print("🧪 Testing MCP Email Server Integration")
    print("=" * 50)
    
    # Check if config.env exists
    if not Path("config.env").exists():
        print("⚠️  Warning: config.env file not found. Email functionality may not work without proper configuration.")
        print("Please ensure you have SENDER_EMAIL and APP_PASSWORD set in your config.env file.")
    
    # Run the test
    success = asyncio.run(test_mcp_email_server())
    
    if success:
        print("\n✅ MCP Email Server test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ MCP Email Server test failed!")
        sys.exit(1)




