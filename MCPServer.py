from fastmcp import FastMCP
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
load_dotenv("config.env")

mcp = FastMCP("EmailMCP", instructions="Send task notifications via Gmail")

@mcp.tool(name="send_task_notification")
def send_task_notification(recipient_email: str, subject: str, body: str) -> str:
    """Send email when a task is created or updated."""
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.getenv("SENDER_EMAIL")
        app_password = os.getenv("APP_PASSWORD")

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = recipient_email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)

        return f"Notification sent to {recipient_email}"
    except Exception as e:
        import traceback
        traceback.print_exc()   # <-- prints full error stack to console
        return f"Failed to send notification: {str(e)}"

if __name__ == "__main__":
    mcp.run("sse", host="127.0.0.1", port=8080)  
