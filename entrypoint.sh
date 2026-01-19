#!/bin/bash
# Entrypoint script for Railway Streamlit deployment
# Handles environment variable expansion correctly

set -e

# Set default port if not provided
PORT=${PORT:-8501}

# Export environment variables for Streamlit
export STREAMLIT_SERVER_PORT=$PORT
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_LOGGER_LEVEL=info

# Run Streamlit
exec streamlit run NEWS.py
