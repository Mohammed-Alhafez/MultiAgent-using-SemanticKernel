from semantic_kernel.functions import kernel_function
from db import execute_query
from typing import Optional

class DBAgentPlugin:

    @kernel_function(name="add_task", description="Add a new task to the database.")
    def add_task(self, employee: str, description: str, due_date: Optional[str] = None) -> str:
        execute_query(
            "INSERT INTO tasks (employee, description, due_date) VALUES (?, ?, ?)",
            (employee, description, due_date)
        )
        # Send email via MCP plugin
        from plugins.MCPPlugin import MCPPlugin
        mcp = MCPPlugin()
        subject = f"New Task Assigned: {description}"
        body = f"A new task has been assigned to {employee}.\n\nDescription: {description}\nDue Date: {due_date or 'N/A'}"
        result = mcp.send_task_notification("mhd.alhafez9@gmail.com", subject, body)

        return f"Task added for {employee}: {description}\n{result}"

    @kernel_function(name="list_pending_tasks", description="List all pending tasks for a person.")
    def list_pending_tasks(self, employee: str) -> str:
        rows = execute_query(
            "SELECT id, description, due_date FROM tasks WHERE employee = ? AND status = 'pending'",
            (employee,),
            fetch=True
        )
        if not rows:
            return f"No pending tasks for {employee}."
        return "\n".join([f"[{id}] {desc} (Due: {due or 'N/A'})" for id, desc, due in rows])

    @kernel_function(name="mark_task_done", description="Mark a task as completed by ID.")
    def mark_task_done(self, id: int) -> str:
        execute_query("UPDATE tasks SET status = 'done' WHERE id = ?", (id,))
        from plugins.MCPPlugin import MCPPlugin
        mcp = MCPPlugin()
        subject = f"Task {id} Completed"
        body = f"The task with ID {id} has been marked as completed."
        result = mcp.send_task_notification("mhd.alhafez9@gmail.com", subject, body)

        return f"Task {id} marked as completed.\n{result}"

    @kernel_function(name="delete_task", description="Delete a task by ID.")
    def delete_task(self, id: int) -> str:
        execute_query("DELETE FROM tasks WHERE id = ?", (id,))
        return f"Task {id} deleted."
