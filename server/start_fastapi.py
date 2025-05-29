#!/usr/bin/env python3
"""
Startup script for MayaCode FastAPI Backend
"""

import os
import uvicorn
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 3001))
    reload = os.getenv("NODE_ENV") != "production"
    
    print("🚀 Starting MayaCode FastAPI Backend...")
    print(f"📊 Health check: http://localhost:{port}/health")
    print(f"🌐 API Base URL: http://localhost:{port}/api/v1")
    print(f"📝 Environment: {os.getenv('NODE_ENV', 'development')}")
    print(f"🔄 Auto-reload: {reload}")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    main() 