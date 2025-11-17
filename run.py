#!/usr/bin/env python3
"""
Backend server runner script
Starts the FastAPI application with uvicorn
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.config import settings


def run_server():
    """Run the FastAPI server"""
    print(f"🏥 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug mode: {settings.DEBUG}")
    print(f"🌐 CORS Origins: {settings.CORS_ORIGINS}")
    print()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)
