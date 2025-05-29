from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import uvicorn
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
import json
import base64
import openai
from openai import OpenAI
from data.user_data import DEFAULT_USER_PROFILE, SUGGESTED_ACTIONS_DATA, DOCUMENTS_DATA

# Load environment variables
load_dotenv()

# OpenAI client initialization
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None

# Configuration - Update these paths according to your file locations
USER_DATA_FILE = "user_data.json"  # Path to your JSON file
PDF_FILE_PATH = "document.pdf"     # Path to your PDF file

app = FastAPI(
    title="MayaCode Backend API",
    description="Backend API for MayaCode User Dashboard",
    version=os.getenv("API_VERSION", "v1")
)

# Pydantic models for chat
class ChatMessage(BaseModel):
    role: str  # "user", "assistant", or "system"
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "gpt-3.5-turbo"  # Default model
    max_tokens: int = 150
    temperature: float = 0.7

class ChatResponse(BaseModel):
    response: str
    usage: Dict[str, Any] = None

# CORS configuration
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Alternative React dev server
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    os.getenv("CORS_ORIGIN", "http://localhost:5173")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "success": True,
        "message": "MayaCode Backend API is running",
        "timestamp": datetime.now().isoformat(),
        "version": os.getenv("API_VERSION", "v1"),
        "user_data_exists": os.path.exists(USER_DATA_FILE),
        "pdf_exists": os.path.exists(PDF_FILE_PATH),
        "openai_configured": bool(openai_api_key)
    }

# Welcome route
@app.get("/")
async def welcome():
    return {
        "success": True,
        "message": "Welcome to MayaCode Backend API",
        "version": os.getenv("API_VERSION", "v1"),
        "endpoints": {
            "health": "/health",
            "userProfile": "/api/v1/user/profile",
            "userActions": "/api/v1/user/actions",
            "userDocuments": "/api/v1/user/documents",
            "dashboardSummary": "/api/v1/user/dashboard-summary",
            "userData": "/user",
            "pdfBase64": "/pdf",
            "openaiChat": "/chat"
        },
        "timestamp": datetime.now().isoformat()
    }

# User profile endpoint
@app.get("/api/v1/user/profile")
async def get_user_profile():
    try:
        return {
            "success": True,
            "data": DEFAULT_USER_PROFILE,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to fetch user profile",
                "message": str(e)
            }
        )

# User actions endpoint with progressive loading
@app.get("/api/v1/user/actions")
async def get_user_actions(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1),
    status: Optional[str] = None,
    loadMore: bool = Query(False)
):
    try:
        # Filter actions by status if provided
        filtered_actions = SUGGESTED_ACTIONS_DATA
        if status:
            filtered_actions = [
                action for action in SUGGESTED_ACTIONS_DATA 
                if action["status"].lower() == status.lower()
            ]

        # For initial load, show first 2-3 items
        # For subsequent loads, implement pagination
        start_index = (page - 1) * limit if loadMore else 0
        end_index = start_index + limit if loadMore else min(3, len(filtered_actions))
        
        paginated_actions = filtered_actions[start_index:end_index]
        
        total_items = len(filtered_actions)
        has_more = end_index < total_items
        next_page = page + 1 if has_more else None

        return {
            "success": True,
            "data": {
                "actions": paginated_actions,
                "pagination": {
                    "currentPage": page,
                    "totalItems": total_items,
                    "itemsPerPage": limit,
                    "totalPages": (total_items + limit - 1) // limit,
                    "hasMore": has_more,
                    "nextPage": next_page,
                    "isInitialLoad": not loadMore
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to fetch suggested actions",
                "message": str(e)
            }
        )

# Get specific action by ID
@app.get("/api/v1/user/actions/{action_id}")
async def get_action_by_id(action_id: str):
    try:
        action = next((action for action in SUGGESTED_ACTIONS_DATA if action["id"] == action_id), None)
        
        if not action:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": "Action not found",
                    "message": f"No action found with ID: {action_id}"
                }
            )

        return {
            "success": True,
            "data": action,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to fetch action details",
                "message": str(e)
            }
        )

# User documents endpoint with progressive loading
@app.get("/api/v1/user/documents")
async def get_user_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(3, ge=1),
    type: Optional[str] = None,
    loadMore: bool = Query(False)
):
    try:
        # Filter documents by type if provided
        filtered_documents = DOCUMENTS_DATA
        if type:
            filtered_documents = [
                doc for doc in DOCUMENTS_DATA 
                if doc["type"].lower() == type.lower()
            ]

        # For initial load, show first 2-3 items
        # For subsequent loads, implement pagination
        start_index = (page - 1) * limit if loadMore else 0
        end_index = start_index + limit if loadMore else min(3, len(filtered_documents))
        
        paginated_documents = filtered_documents[start_index:end_index]
        
        total_items = len(filtered_documents)
        has_more = end_index < total_items
        next_page = page + 1 if has_more else None

        return {
            "success": True,
            "data": {
                "documents": paginated_documents,
                "pagination": {
                    "currentPage": page,
                    "totalItems": total_items,
                    "itemsPerPage": limit,
                    "totalPages": (total_items + limit - 1) // limit,
                    "hasMore": has_more,
                    "nextPage": next_page,
                    "isInitialLoad": not loadMore
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to fetch documents",
                "message": str(e)
            }
        )

# Dashboard summary endpoint
@app.get("/api/v1/user/dashboard-summary")
async def get_dashboard_summary():
    try:
        total_actions = len(SUGGESTED_ACTIONS_DATA)
        completed_actions = len([action for action in SUGGESTED_ACTIONS_DATA if action["status"] == "Completed"])
        in_progress_actions = len([action for action in SUGGESTED_ACTIONS_DATA if action["status"] == "In Progress"])
        not_started_actions = len([action for action in SUGGESTED_ACTIONS_DATA if action["status"] == "Not Started"])
        
        # Calculate onboarding completion percentage
        completed_value = 0
        for action in SUGGESTED_ACTIONS_DATA:
            if action["status"] == "Completed":
                completed_value += 1
            elif action["status"] == "In Progress":
                completed_value += action.get("progressValue", 50) / 100
        
        onboarding_completion = (completed_value / total_actions) * 100

        return {
            "success": True,
            "data": {
                "user": DEFAULT_USER_PROFILE,
                "stats": {
                    "totalActions": total_actions,
                    "completedActions": completed_actions,
                    "inProgressActions": in_progress_actions,
                    "notStartedActions": not_started_actions,
                    "onboardingCompletion": round(onboarding_completion),
                    "totalDocuments": len(DOCUMENTS_DATA)
                },
                "recentActions": SUGGESTED_ACTIONS_DATA[:3],  # Show first 3 actions
                "recentDocuments": DOCUMENTS_DATA[:3]  # Show first 3 documents
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to fetch dashboard summary",
                "message": str(e)
            }
        )

# Custom exception handler for 404
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "Endpoint not found",
            "message": f"The requested endpoint was not found",
            "timestamp": datetime.now().isoformat()
        }
    )

# --- New endpoints from user-provided code ---

@app.get("/user", response_model=Dict[str, Any])
async def get_user_data():
    """
    Endpoint to fetch user data from a local JSON file
    """
    try:
        if not os.path.exists(USER_DATA_FILE):
            raise HTTPException(
                status_code=404, 
                detail=f"User data file '{USER_DATA_FILE}' not found"
            )
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as file:
            user_data = json.load(file)
        return {"success": True, "data": user_data}
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400, 
            detail="Invalid JSON format in user data file"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error reading user data: {str(e)}"
        )

@app.get("/pdf")
async def get_pdf_base64():
    """
    Endpoint to fetch a PDF file and return it as base64 encoded string
    """
    try:
        if not os.path.exists(PDF_FILE_PATH):
            raise HTTPException(
                status_code=404, 
                detail=f"PDF file '{PDF_FILE_PATH}' not found"
            )
        with open(PDF_FILE_PATH, 'rb') as pdf_file:
            pdf_content = pdf_file.read()
            pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
        return {
            "success": True,
            "filename": os.path.basename(PDF_FILE_PATH),
            "data": pdf_base64,
            "size": len(pdf_content)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing PDF file: {str(e)}"
        )

@app.post("/chat", response_model=ChatResponse)
async def chat_with_openai(chat_request: ChatRequest):
    """
    Endpoint to send messages to OpenAI and return the response
    """
    try:
        if not openai_api_key:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured"
            )
        messages = [{"role": msg.role, "content": msg.content} for msg in chat_request.messages]
        response = openai_client.chat.completions.create(
            model=chat_request.model,
            messages=messages,
            max_tokens=chat_request.max_tokens,
            temperature=chat_request.temperature
        )
        assistant_response = response.choices[0].message.content
        usage_info = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }
        return ChatResponse(
            response=assistant_response,
            usage=usage_info
        )
    except openai.AuthenticationError:
        raise HTTPException(
            status_code=401,
            detail="Invalid OpenAI API key"
        )
    except openai.RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="OpenAI API rate limit exceeded"
        )
    except openai.APIError as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI API error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3001))
    print(f"🚀 MayaCode Backend API running on port {port}")
    print(f"📊 Health check: http://localhost:{port}/health")
    print(f"🌐 API Base URL: http://localhost:{port}/api/v1")
    print(f"📝 Environment: {os.getenv('NODE_ENV', 'development')}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True if os.getenv("NODE_ENV") != "production" else False
    )