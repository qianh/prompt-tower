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
        *   `prompt_service.py`: Manages prompt CRUD operations and interacts with YAML files in `prompt-template/`.
        *   `llm_service.py`: Handles interactions with external LLM providers (Gemini, Qwen, DeepSeek).
        *   `file_service.py`: General file operations for prompts.
        *   `user_service.py`: Manages user registration and retrieval, storing data in `backend/data/users.json`.
    *   Authentication is handled via JWTs, with utilities in `backend/utils/security.py` (password hashing) and `backend/utils/jwt_helpers.py` (JWT creation/decoding). Auth routes are in `backend/api/auth.py`.
    *   Configuration is managed via `backend/config.py` and a `.env` file.
    *   The main application entry point is `backend/main.py`.

2.  **Frontend (React):** Located in the `frontend/` directory.
    *   Provides the user interface for prompt management, LLM optimization, user signup, and login.
    *   Built with React 18 and uses Ant Design 5 for UI components.
    *   Routing is handled by `react-router-dom` v6, configured in `frontend/src/App.jsx`.
    *   API interactions are managed through `frontend/src/services/api.js`, which uses `axios`. An interceptor automatically attaches JWTs to requests.
    *   Authentication state (user, token) is managed globally via `AuthContext` (`frontend/src/context/AuthContext.jsx`).
    *   Page components are in `frontend/src/pages/` and reusable UI components in `frontend/src/components/`.
    *   The `proxy` setting in `frontend/package.json` directs API requests to the backend at `http://localhost:8010` during development (note: backend runs on 8010, `start.sh` script has a typo for backend port 8010).

3.  **MCP Server (Python):** Located in the `mcp_server/` directory.
    *   A Python-based server implementing the Model Context Protocol.
    *   Handles prompt retrieval based on priority for MCP clients.
    *   Key files: `mcp_server/server.py` (main server), `mcp_server/search_service.py`.

## Common Commands

### Environment Setup

1.  **Clone Repository:**
    ```bash
    git clone https://github.com/your-repo/prompt-management-system.git
    cd prompt-management-system
    ```

2.  **Backend Setup (from project root):**
    *   Ensure Python 3.11+ and `uv` are installed.
    *   Create/activate a virtual environment (recommended):
        ```bash
        uv venv
        source .venv/bin/activate  # macOS/Linux
        # .venv\Scripts\activate    # Windows
        ```
    *   Install dependencies:
        ```bash
        uv pip install -e . # Preferred method for development
        # or directly: uv pip install fastapi uvicorn pydantic pyyaml httpx google-generativeai openai aiofiles python-multipart python-dotenv sse-starlette pydantic-settings passlib[bcrypt] python-jose[cryptography]
        ```
    *   Copy `.env.example` to `.env` and configure variables, especially `SECRET_KEY` for JWTs and any LLM API keys.
        ```bash
        cp .env.example .env
        ```

3.  **Frontend Setup (from project root):**
    *   Ensure Node.js and npm (or yarn) are installed.
    *   Install dependencies:
        ```bash
        cd frontend
        npm install
        cd ..
        ```

### Running the Application

1.  **Start Backend Server (from project root):**
    ```bash
    uvicorn backend.main:app --host 0.0.0.0 --port 8010 --reload
    ```
    (Note: `scripts/start.sh` uses `uv run python -m backend.main` which might also work but the `uvicorn` command is more standard for FastAPI development.)

2.  **Start Frontend Development Server (from project root):**
    ```bash
    cd frontend
    npm start
    ```
    The frontend will be accessible at `http://localhost:3000`.

3.  **Start MCP Server (from project root, if needed):**
    ```bash
    python mcp_server/server.py
    ```
    The MCP Server will run on `http://localhost:8011`.

(Alternatively, `scripts/start.sh` attempts to run all three services.)

### Linting & Formatting

*   **Backend:**
    *   Tools: `black` (formatter), `isort` (import sorter), `flake8` (linter).
    *   Commands (run from project root, assuming virtual environment is active):
        ```bash
        black backend/
        isort backend/
        flake8 backend/
        ```
*   **Frontend:**
    *   Uses ESLint configured via `react-scripts` (`"extends": ["react-app", "react-app/jest"]` in `package.json`).
    *   To lint:
        ```bash
        cd frontend
        npm run lint
        # (If not explicitly defined, ESLint might run as part of 'npm test' or via IDE integrations)
        # Verify if 'npm run lint' needs to be added to package.json scripts if not present
        ```

### Testing

*   **Backend (from project root, assuming virtual environment is active):**
    *   Tools: `pytest`, `pytest-asyncio`.
    *   Run tests:
        ```bash
        pytest
        # or specific file, e.g.: pytest tests/test_backend.py
        ```
*   **Frontend (from `frontend/` directory):**
    *   Uses `react-scripts test`.
    *   Run tests:
        ```bash
        npm test
        ```

## Key File Locations

*   **Backend Configuration:** `backend/config.py`, `.env` (root)
*   **Backend Models:** `backend/models.py`
*   **Backend API Routes:** `backend/api/` (e.g., `auth.py`, `prompts.py`)
*   **Backend Services (Business Logic):** `backend/services/` (e.g., `user_service.py`, `prompt_service.py`)
*   **Frontend API Service Calls:** `frontend/src/services/api.js`
*   **Frontend Routing:** `frontend/src/App.jsx`
*   **Frontend Auth Context:** `frontend/src/context/AuthContext.jsx`
*   **Frontend Page Components:** `frontend/src/pages/`
*   **Prompt YAML Files:** `prompt-template/`
*   **User Data (JSON):** `backend/data/users.json` (created at runtime)

## Important Notes for Development

*   The backend uses `uv` for dependency management. Ensure `uv` is installed and used as per `pyproject.toml`.
*   The `SECRET_KEY` environment variable in the `.env` file is critical for JWT authentication security. Ensure it is strong and kept secret.
*   The frontend relies on the `proxy` setting in `package.json` to route API calls to the backend during development. The default backend port is 8010.
*   When adding new backend dependencies, update `pyproject.toml`.
*   When adding new frontend dependencies, update `frontend/package.json`.
*   The `scripts/install.sh` and `scripts/start.sh` provide a way to set up and run the full application stack.
