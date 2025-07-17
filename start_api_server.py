#!/usr/bin/env python3
"""
Startup script for the API server
Handles environment setup and launches the Flask API server
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import flask_cors
        import requests
        logger.info("✓ All dependencies are installed")
        return True
    except ImportError as e:
        logger.error(f"✗ Missing dependency: {e}")
        logger.info("Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "api_requirements.txt"])
        return True

def setup_environment():
    """Setup environment variables and directories"""
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    # Set default environment variables if not set
    if not os.getenv("GROQ_API_KEY"):
        logger.warning("GROQ_API_KEY not set - AI features will be disabled")
    
    logger.info("✓ Environment setup complete")

def main():
    """Main startup function"""
    logger.info("Starting API Server Setup...")
    
    # Check and install dependencies
    if not check_dependencies():
        logger.error("Failed to install dependencies")
        return
    
    # Setup environment
    setup_environment()
    
    # Start the API server
    logger.info("Starting API server...")
    try:
        from api_server import app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False
        )
    except KeyboardInterrupt:
        logger.info("API server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start API server: {e}")

if __name__ == "__main__":
    main() 