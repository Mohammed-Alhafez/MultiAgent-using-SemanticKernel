from semantic_kernel.functions import kernel_function
from db import execute_query
from typing import Optional

class DBAgent:

    @kernel_function(name="add_task", description="Add a new task to the database.")
    def add_task(self, employee: str, description: str, due_date: Optional[str] = None) -> str:
        execute_query(
            "INSERT INTO tasks (employee, description, due_date) VALUES (?, ?, ?)",
            (employee, description, due_date)
        )
        return f"Task added for {employee}: {description}"

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
        return f"Task {id} marked as completed."

    @kernel_function(name="delete_task", description="Delete a task by ID.")
    def delete_task(self, id: int) -> str:
        execute_query("DELETE FROM tasks WHERE id = ?", (id,))
        return f"Task {id} deleted."
