class Orchestrator:
    def __init__(self, db_agent, informative_agent):
        self.db_agent = db_agent
        self.informative_agent = informative_agent

    def route(self, user_input: str):
        """Very basic routing logic. Can be replaced with intent classification."""
        if any(keyword in user_input.lower() for keyword in ["task", "todo", "assign", "complete", "pending"]):
            return self.db_agent
        elif any(keyword in user_input.lower() for keyword in ["policy", "guideline", "rules", "search", "information"]):
            return self.informative_agent
        else:
            return self.informative_agent  # Default fallback
