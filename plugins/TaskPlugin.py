from typing import List,Dict
from semantic_kernel.functions import kernel_function

class TaskPlugin:
    tasks: List[Dict] = [
        {"id": 1, "title": "Prepare report", "done": False},
        {"id": 2, "title": "Email client", "done": True},
    ]

    @kernel_function(name="list_tasks", description="List all tasks")
    def list_tasks(self) -> str:
        return str(self.tasks)

    @kernel_function(name="add_task", description="Add a new task")
    def add_task(self, title: str) -> str:
        new_id = max(task["id"] for task in self.tasks) + 1 if self.tasks else 1
        task = {"id": new_id, "title": title, "done": False}
        self.tasks.append(task)
        return f"Added task: {task}"

    @kernel_function(name="complete_task", description="Mark a task as complete")
    def complete_task(self, id: int) -> str:
        for task in self.tasks:
            if task["id"] == id:
                task["done"] = True
                return f"Task {id} marked as complete."
        return f"Task {id} not found."