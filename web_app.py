"""
FastAPI Web Application for SMNT-KRNL System
Main entry point for the web interface
"""

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

# Import our MVC components
from models.request_models import QueryRequest, TaskRequest, SearchRequest
from models.response_models import QueryResponse, TaskResponse, SearchResponse
from controllers.api_controller import APIController
from controllers.web_controller import WebController
from services.agent_service import AgentService

# Initialize FastAPI app
app = FastAPI(
    title="SMNT-KRNL Web Interface",
    description="Web interface for the SMNT-KRNL agent system",
    version="1.0.0"
)

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize services
agent_service = AgentService()
api_controller = APIController(agent_service)
web_controller = WebController(agent_service, templates)

# ==================== WEB ROUTES ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main web interface"""
    return await web_controller.home(request)

@app.post("/query", response_class=HTMLResponse)
async def process_query(
    request: Request,
    user_query: str = Form(...)
):
    """Process user query and return HTML response"""
    return await web_controller.process_query(request, user_query)

# ==================== API ROUTES ====================

@app.post("/api/query", response_model=QueryResponse)
async def api_query(query_request: QueryRequest):
    """API endpoint for processing queries"""
    return await api_controller.process_query(query_request)

@app.get("/api/tasks", response_model=TaskResponse)
async def get_tasks(employee: Optional[str] = None):
    """Get tasks for an employee or all tasks"""
    return await api_controller.get_tasks(employee)

@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(task_request: TaskRequest):
    """Create a new task"""
    return await api_controller.create_task(task_request)

@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_request: TaskRequest):
    """Update an existing task"""
    return await api_controller.update_task(task_id, task_request)

@app.delete("/api/tasks/{task_id}", response_model=TaskResponse)
async def delete_task(task_id: int):
    """Delete a task"""
    return await api_controller.delete_task(task_id)

@app.post("/api/search", response_model=SearchResponse)
async def search_knowledge(search_request: SearchRequest):
    """Search company knowledge base"""
    return await api_controller.search_knowledge(search_request)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "SMNT-KRNL Web Interface is running"}

# ==================== ERROR HANDLERS ====================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)

# ==================== STARTUP/SHUTDOWN ====================

@app.on_event("startup")
async def startup_event():
    """Initialize the agent system on startup"""
    await agent_service.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await agent_service.cleanup()

if __name__ == "__main__":
    uvicorn.run(
        "web_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )



