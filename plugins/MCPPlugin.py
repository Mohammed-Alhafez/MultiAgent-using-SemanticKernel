import smtplib
from email.mime.text import MIMEText
from typing import Optional
from semantic_kernel.functions import kernel_function

import os

class MCPPlugin:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = ("team.9b79@gmail.com")  # e.g., "yourname@gmail.com"
        self.app_password = ("mazn robv xhfj jvcl")  # The 16-char App password

    @kernel_function(name="send_task_notification", description="Send email when a task is created or updated.")
    def send_task_notification(self, recipient_email: str, subject: str, body: str) -> str:
        try:
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = recipient_email

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.app_password)
                server.send_message(msg)

            return f"Notification sent to {recipient_email}"
        except Exception as e:
            import traceback
            traceback.print_exc()  # This prints to console
            return f"Failed to send notification: {str(e)}"

