# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Prompt Management System built with a Python FastAPI backend, a React frontend, and a Python-based MCP (Model Context Protocol) Server. It allows users to manage prompts, optimize them using LLMs, and synchronize active prompts with an MCP Server. The system also includes user authentication.

## High-Level Architecture

The system is composed of three main parts:

1.  **Backend (Python/FastAPI):** Located in the `backend/` directory.
    *   Serves REST APIs for managing prompts, LLM interactions, and user authentication.
    *   Uses Pydantic models (`backend/models.py`) for data validation and serialization.
    *   Business logic is separated into services (`backend/services/`):
        *   `prompt_service.py`: Manages prompt CRUD operations and interacts with YAML files in `prompt-template/` or the database.
        *   `user_service.py`: Manages user registration and retrieval, storing data in `backend/data/users.json` or the database.
        *   `llm_service.py`: Handles interactions with external LLM providers (Gemini, Qwen, DeepSeek).
    *   Authentication is handled via JWTs, with utilities in `backend/utils/security.py` (password hashing) and `backend/utils/jwt_helpers.py` (JWT creation/decoding). Auth routes are in `backend/api/auth.py`.
    *   Configuration is managed via `backend/config.py` and a `.env` file. The `USE_DATABASE` flag in `.env` toggles between file-based and PostgreSQL storage.
    *   The main application entry point is `backend/main.py`.

2.  **Frontend (React):** Located in the `frontend/` directory.
    *   Provides the user interface for prompt management, LLM optimization, user signup, and login.
    *   Built with React 18 and uses Ant Design 5 for UI components.
    *   Routing is handled by `react-router-dom` v6, configured in `frontend/src/App.jsx`.
    *   API interactions are managed through `frontend/src/services/api.js`, which uses `axios`. An interceptor automatically attaches JWTs to requests.
    *   Authentication state (user, token) is managed globally via `AuthContext` (`frontend/src/context/AuthContext.jsx`).
    *   Page components are in `frontend/src/pages/` and reusable UI components in `frontend/src/components/`.
    *   The `proxy` setting in `frontend/package.json` directs API requests to the backend at `http://localhost:8010` during development.

3.  **MCP Server (Python):** Located in the `mcp_server/` directory.
    *   A Python-based server implementing the Model Context Protocol.
    *   Handles prompt retrieval based on priority for MCP clients.
    *   Key files: `mcp_server/server.py` (main server), `mcp_server/search_service.py`.

## Common Commands

For detailed setup, see `README.md`.

### Environment Setup

1.  **Backend Setup (from project root):**
    *   Ensure Python 3.11+ and `uv` are installed.
    *   Create/activate a virtual environment: `uv venv` then `source .venv/bin/activate`.
    *   Install dependencies: `uv pip install -e .` (or `uv pip install -e ".[dev]"` for dev tools).
    *   Copy `.env.example` to `.env` and configure variables, especially `SECRET_KEY`.

2.  **Frontend Setup (from project root):**
    *   Ensure Node.js and npm are installed.
    *   Install dependencies: `cd frontend && npm install && cd ..`.

### Running the Application

1.  **Start Backend Server (from project root):**
    ```bash
    uvicorn backend.main:app --host 0.0.0.0 --port 8010 --reload
    ```

2.  **Start Frontend Development Server (from project root):**
    ```bash
    cd frontend && npm start
    ```

3.  **Start MCP Server (from project root, if needed):**
    ```bash
    python mcp_server/server.py
    ```

### Linting & Formatting

*   **Backend (from project root):**
    ```bash
    black backend/
    isort backend/
    flake8 backend/
    ```
*   **Frontend (from `frontend/` directory):**
    ```bash
    npm run lint
    ```

### Testing

*   **Backend (from project root):**
    ```bash
    pytest
    ```
*   **Frontend (from `frontend/` directory):**
    ```bash
    npm test
    ```

## Key File Locations

*   **Backend Configuration:** `backend/config.py`, `.env` (root)
*   **Backend Models:** `backend/models.py`, `backend/db_models.py`
*   **Backend API Routes:** `backend/api/` (e.g., `auth.py`, `prompts.py`)
*   **Backend Services (Business Logic):** `backend/services/` (e.g., `user_service.py`, `prompt_service.py`)
*   **Frontend API Service Calls:** `frontend/src/services/api.js`
*   **Frontend Routing:** `frontend/src/App.jsx`
*   **Frontend Auth Context:** `frontend/src/context/AuthContext.jsx`
*   **Frontend Page Components:** `frontend/src/pages/`
*   **Prompt YAML Files (if not using DB):** `prompt-template/`
*   **User Data (JSON, if not using DB):** `backend/data/users.json`

## Important Notes for Development

*   The backend uses `uv` for dependency management. Ensure `uv` is installed and used as per `pyproject.toml`.
*   The `SECRET_KEY` environment variable in the `.env` file is critical for JWT authentication security.
*   The system can switch between file-based storage and a PostgreSQL database via the `USE_DATABASE` setting in `.env`. See `MIGRATION_GUIDE.md` for details on setting up and migrating to the database.
*   The frontend relies on the `proxy` setting in `package.json` to route API calls to the backend at `http://localhost:8010`.