# MCP Email Integration Guide

This guide explains how the MCP (Model Context Protocol) email integration works in your Semantic Kernel application.

## Overview

The system now uses a proper MCP server for sending email notifications when tasks are created or updated. This replaces the previous kernel function approach with a more robust, standalone MCP server.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCPAgent      │    │  MCPStdioPlugin  │    │ MCP Email Server│
│                 │◄──►│                  │◄──►│                 │
│ (ChatCompletion │    │ (Communication   │    │ (FastMCP Server)│
│  Agent)         │    │  Bridge)         │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Components

### 1. MCP Email Server (`plugins/mcp_email_server.py`)

A standalone FastMCP server that provides email functionality:

- **send_task_notification**: Send custom email notifications
- **send_task_assignment_notification**: Send notifications for new task assignments
- **send_task_completion_notification**: Send notifications for completed tasks

### 2. MCPStdioPlugin Integration (`Agents/agent_set.py`)

The MCPStdioPlugin connects your Semantic Kernel application to the MCP email server via STDIO communication.

### 3. Updated MCPAgent

The MCPAgent now uses the MCP email server instead of direct kernel functions.

## Configuration

### Environment Variables

Make sure your `config.env` file contains:

```env
SENDER_EMAIL=your-email@gmail.com
APP_PASSWORD=your-app-password
```

### Gmail App Password Setup

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
   - Use this password as `APP_PASSWORD`

## Usage

### Automatic Integration

The system automatically connects to the MCP email server when the application starts. The MCPAgent will use the email functions when:

1. A task is assigned (triggers `send_task_assignment_notification`)
2. A task is completed (triggers `send_task_completion_notification`)
3. Custom notifications are needed (uses `send_task_notification`)

### Manual Testing

You can test the MCP email server independently:

```bash
python test_mcp_email.py
```

### Running the MCP Server Standalone

To run the MCP email server as a standalone process:

```bash
python plugins/mcp_email_server.py
```

## Email Functions

### send_task_assignment_notification

```python
{
    "recipient_email": "employee@company.com",
    "task_description": "Review project documentation",
    "assigned_by": "John Doe",
    "due_date": "2024-01-15"  # Optional
}
```

### send_task_completion_notification

```python
{
    "recipient_email": "employee@company.com",
    "task_description": "Review project documentation",
    "completed_by": "Jane Smith"
}
```

### send_task_notification

```python
{
    "recipient_email": "employee@company.com",
    "subject": "Custom Subject",
    "body": "Custom email body content"
}
```

## Workflow

1. **User Request**: User asks to assign a task
2. **DBAgent**: Processes the task assignment
3. **Handoff**: DBAgent hands off to MCPAgent
4. **Email Notification**: MCPAgent uses MCP email server to send notification
5. **Confirmation**: MCPAgent confirms email sent and hands back to TriageAgent

## Error Handling

The MCP email server includes comprehensive error handling:

- **Authentication errors**: Invalid email credentials
- **Recipient errors**: Invalid email addresses
- **Connection errors**: SMTP server issues
- **Configuration errors**: Missing environment variables

## Benefits of MCP Integration

1. **Separation of Concerns**: Email functionality is isolated in its own server
2. **Scalability**: MCP server can be deployed independently
3. **Reusability**: Other applications can use the same MCP email server
4. **Maintainability**: Email logic is centralized and easier to update
5. **Testing**: Email functionality can be tested independently

## Troubleshooting

### Common Issues

1. **"MCP email plugin not connected"**
   - Check that `plugins/mcp_email_server.py` exists
   - Verify Python path is correct
   - Check for syntax errors in the MCP server

2. **"Authentication failed"**
   - Verify `SENDER_EMAIL` and `APP_PASSWORD` in config.env
   - Ensure 2FA is enabled and app password is generated
   - Check that the app password is for "Mail" service

3. **"Recipient email was refused"**
   - Verify the recipient email address is valid
   - Check for typos in email addresses

### Debug Mode

To see detailed MCP communication, you can add logging to the MCPStdioPlugin connection in `Agents/agent_set.py`.

## Future Enhancements

- Add email templates
- Support for HTML emails
- Email scheduling
- Multiple email providers (Outlook, etc.)
- Email tracking and delivery status
- Bulk email notifications

## Files Modified

- `plugins/mcp_email_server.py` - New MCP email server
- `plugins/MCPPlugin.py` - Updated to be a fallback client
- `Agents/agent_set.py` - Added MCPStdioPlugin integration
- `main.py` - Added MCP plugin connection on startup
- `test_mcp_email.py` - Test script for MCP email functionality




