from semantic_kernel.functions import kernel_function
from db import execute_query
from typing import Optional

class DBAgentPlugin:

    @kernel_function(name="add_task", description="Add a new task to the database.")
    def add_task(self, employee: str, email: str, description: str, due_date: Optional[str] = None) -> str:
        if not email:
            return f"Email for {employee} is missing. Please provide an email address to send the task notification."
        
        execute_query(
            "INSERT INTO tasks (employee, description, due_date) VALUES (?, ?, ?)",
            (employee, description, due_date)
        )
        
        return f"Task '{description}' has been successfully added for {employee}. Please handoff to MCPAgent to send email notification to {email}."

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
    def mark_task_done(self, email: str, id: int) -> str:
        execute_query("UPDATE tasks SET status = 'done' WHERE id = ?", (id,))
        # Send email via MCP plugin
        # from plugins.MCPPlugin import MCPPlugin
        # mcp = MCPPlugin()
        # subject = f"Task {id} Completed"
        # body = f"The task with ID {id} has been marked as completed."
        # result = mcp.send_task_notification(email, subject, body)

        return f"Task {id} marked as completed."

    @kernel_function(name="delete_task", description="Delete a task by ID.")
    def delete_task(self, id: int) -> str:
        execute_query("DELETE FROM tasks WHERE id = ?", (id,))
        return f"Task {id} deleted."
