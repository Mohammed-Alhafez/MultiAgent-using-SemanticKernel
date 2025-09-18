# SMNT-KRNL Quick Reference Guide

## System Overview
**SMNT-KRNL** is an AI-powered task management and information retrieval system using Microsoft Semantic Kernel with multi-agent architecture.

## Key Components
- **4 Specialized Agents**: TriageAgent, DBAgent, InformativeAgent, MCPAgent
- **Database**: SQLite for task storage
- **Email Service**: SMTP via Gmail for notifications
- **Search Engine**: Azure Cognitive Search for knowledge base
- **AI Engine**: Azure OpenAI GPT-4 for natural language processing

## Main Use Cases

### 1. Task Assignment
```
Input: "assign task to [employee] to [description]"
Flow: User → TriageAgent → DBAgent → Database → MCPAgent → Email
Output: Task created + Email notification sent
```

### 2. Task Management
```
Input: "list tasks for [employee]" / "mark task [id] complete" / "delete task [id]"
Flow: User → TriageAgent → DBAgent → Database operations
Output: Task list / Status update / Deletion confirmation
```

### 3. Information Retrieval
```
Input: "What is [policy/guideline question]?"
Flow: User → TriageAgent → InformativeAgent → Azure Search
Output: Relevant policy information from knowledge base
```

## Agent Responsibilities

| Agent | Primary Function | Key Operations |
|-------|------------------|----------------|
| **TriageAgent** | Request routing | Analyzes input, routes to appropriate agent |
| **DBAgent** | Task management | Add, list, complete, delete tasks |
| **InformativeAgent** | Information retrieval | Search company knowledge base |
| **MCPAgent** | Email notifications | Send task assignment/completion emails |

## Database Schema
```sql
tasks (id, employee, description, due_date, status)
```

## Configuration Files
- `config.env`: Environment variables (API keys, endpoints)
- `orchestrator.py`: Agent handoff configuration
- `Agents/agent_set.py`: Agent definitions and instructions
- `plugins/`: Agent-specific functionality

## Handoff Mechanism
- Agents automatically transfer control using `Handoff-transfer_to_[AgentName]` functions
- No parameters required (empty JSON: `{}`)
- Orchestrated by Semantic Kernel's handoff system

## Error Handling
- Database connection failures: Graceful error messages
- Email delivery failures: Error logging and user notification
- Agent handoff failures: Fallback to TriageAgent
- Invalid inputs: Input validation and sanitization

## Performance
- Task assignment: < 3 seconds end-to-end
- Information retrieval: < 2 seconds
- Email notifications: < 5 seconds
- Database operations: < 1 second

## Security
- Environment variables for sensitive data
- Parameterized SQL queries (SQL injection prevention)
- App password authentication for email
- Agent-based access control

## Files Structure
```
smnt-krnl/
├── main.py                 # Application entry point
├── orchestrator.py         # Handoff orchestration
├── db.py                   # Database operations
├── config.env              # Configuration
├── Agents/
│   └── agent_set.py        # Agent definitions
├── plugins/
│   ├── DBAgentPlugin.py    # Task management functions
│   ├── MCPPlugin.py        # Email functions
│   └── InformativeAgentPlugin.py # Search functions
└── tasks.db                # SQLite database
```

## Demo Commands
```bash
# Start the system
python main.py

# Example interactions:
"assign a new task to jamil to close the project"
"list all pending tasks for jamil"
"what is the company vacation policy?"
"mark task 1 as complete"
```

## Troubleshooting
- **Handoff errors**: Check orchestrator.py handoff configuration
- **Email failures**: Verify SMTP credentials in config.env
- **Database errors**: Check SQLite file permissions
- **Search errors**: Verify Azure Search configuration

## Future Enhancements
- User authentication and role-based access
- Advanced analytics and reporting
- Mobile interface
- REST API for external integration
- Multi-tenant support
