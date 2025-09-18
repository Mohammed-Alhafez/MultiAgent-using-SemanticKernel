

from semantic_kernel.agents.runtime import InProcessRuntime
import asyncio
from orchestrator import handoff_orchestration
from db import init_db, init_chat_history_table

async def main():

    # Initialize DB tables
    init_db()
    init_chat_history_table()

    runtime = InProcessRuntime()
    runtime.start()

    print("Enter your request (type 'exit' to quit):")
    while True:
        user_input = input("\nUser > ")
        
        # Check for exit command before processing
        if user_input.lower().strip() == "exit":
            print("Goodbye! Thank you .")
            break
        
        # Skip empty inputs
        if not user_input.strip():
            continue

        try:
            result = await handoff_orchestration.invoke(
                task=user_input,
                runtime=runtime,
            )

            final_output = await result.get()
            print(f"\n[Final Output] {final_output}")
        except Exception as e:
            print(f"Error processing request: {e}")
            continue

if __name__ == "__main__":
    asyncio.run(main())
