from __future__ import annotations

import os
from pathlib import Path

from runtime_paths import configure_crewai_storage

configure_crewai_storage()

from crewai import Crew, LLM, Process, Task
from dotenv import load_dotenv

from agents import (
    get_architect_agent,
    get_backend_agent,
    get_business_agent,
    get_devops_agent,
    get_frontend_agent,
)
from tools import RagTool

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"


def build_llm() -> LLM:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing GEMINI_API_KEY or GOOGLE_API_KEY. Copy .env.example to .env and set a valid key."
        )

    return LLM(
        model=os.getenv("GEMINI_MODEL", "gemini/gemini-2.5-flash"),
        api_key=api_key,
        temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.2")),
    )


def write_static_output_files(project_name: str) -> None:
    """Create deterministic companion artifacts requested by the project prompt."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    database_schema = f"""-- Database schema draft for {project_name}
-- Generated as a baseline companion to the CrewAI architecture output.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(180) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'customer',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'planning',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    assignee_id UUID REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(240) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'todo',
    priority VARCHAR(30) NOT NULL DEFAULT 'medium',
    due_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_projects_owner_id ON projects(owner_id);
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_assignee_id ON tasks(assignee_id);
CREATE INDEX idx_tasks_status ON tasks(status);
"""

    docker_compose = """services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    env_file:
      - .env
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "8000:8000"
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

  web:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    depends_on:
      - api
    ports:
      - "3000:80"

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app_password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 10s
      timeout: 5s
      retries: 5
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
"""

    output_readme = f"""# {project_name} Generated Project Plan

This folder contains generated planning and implementation artifacts from the AI Project Manager crew.

## Files

- `requirements.md`: product overview, roles, stories, requirements, and MVP scope.
- `architecture.md`: architecture, API, authentication, security, and scaling plan.
- `backend.md`: FastAPI backend implementation plan.
- `frontend.md`: React frontend implementation plan.
- `deployment.md`: Docker, nginx, deployment, and CI/CD plan.
- `database_schema.sql`: baseline relational schema draft.
- `docker-compose.yml`: baseline local deployment composition.

Run `python main.py` again to regenerate the agent-authored Markdown files for a new project idea.
"""

    (OUTPUT_DIR / "database_schema.sql").write_text(database_schema, encoding="utf-8")
    (OUTPUT_DIR / "docker-compose.yml").write_text(docker_compose, encoding="utf-8")
    (OUTPUT_DIR / "README.md").write_text(output_readme, encoding="utf-8")


def create_tasks(project_name: str, agents: dict[str, object]) -> list[Task]:
    business_task = Task(
        description=f"""
Project idea: {project_name}

Use the Local RAG Knowledge Search tool when more implementation context is useful.
Generate a production-quality requirements document containing:
- Project overview
- User roles
- User stories grouped by role
- Functional requirements
- Non-functional requirements
- MVP scope
- Out-of-scope items
- Acceptance criteria
""",
        expected_output="A complete requirements.md document in Markdown.",
        agent=agents["business"],
        output_file=str(OUTPUT_DIR / "requirements.md"),
    )

    architect_task = Task(
        description=f"""
Project idea: {project_name}

Use the requirements context and the RAG tool. Generate:
- High-level architecture
- Logical services and boundaries
- Database design
- API design
- Authentication and authorization
- Security controls
- Scaling strategy
- Operational concerns
- A Mermaid architecture diagram
""",
        expected_output="A complete architecture.md document in Markdown.",
        agent=agents["architect"],
        context=[business_task],
        output_file=str(OUTPUT_DIR / "architecture.md"),
    )

    backend_task = Task(
        description=f"""
Project idea: {project_name}

Use prior context and the RAG tool. Generate:
- FastAPI project folder structure
- Core dependencies
- SQLAlchemy models
- Pydantic schemas
- CRUD API design
- JWT authentication flow
- Alembic migration plan
- Error handling strategy
- Example code snippets for critical files
- Backend test plan
""",
        expected_output="A complete backend.md document in Markdown.",
        agent=agents["backend"],
        context=[business_task, architect_task],
        output_file=str(OUTPUT_DIR / "backend.md"),
    )

    frontend_task = Task(
        description=f"""
Project idea: {project_name}

Use prior context and the RAG tool. Generate:
- React project folder structure
- Routing map
- Pages
- Components
- Dashboard behavior
- Authentication UI
- API client structure
- State management plan
- Accessibility and responsive design guidance
- Frontend test plan
""",
        expected_output="A complete frontend.md document in Markdown.",
        agent=agents["frontend"],
        context=[business_task, architect_task, backend_task],
        output_file=str(OUTPUT_DIR / "frontend.md"),
    )

    devops_task = Task(
        description=f"""
Project idea: {project_name}

Use all prior context and the RAG tool. Generate:
- Dockerfile recommendations for backend and frontend
- docker-compose.yml explanation
- nginx reverse proxy configuration
- Deployment steps
- Environment variable management
- Database migration and backup process
- Monitoring and logging
- CI/CD recommendation
- Production readiness checklist
""",
        expected_output="A complete deployment.md document in Markdown.",
        agent=agents["devops"],
        context=[business_task, architect_task, backend_task, frontend_task],
        output_file=str(OUTPUT_DIR / "deployment.md"),
    )

    return [business_task, architect_task, backend_task, frontend_task, devops_task]


def run_project_manager(project_name: str) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rag_tool = RagTool()
    llm = build_llm()

    agents = {
        "business": get_business_agent(llm, rag_tool),
        "architect": get_architect_agent(llm, rag_tool),
        "backend": get_backend_agent(llm, rag_tool),
        "frontend": get_frontend_agent(llm, rag_tool),
        "devops": get_devops_agent(llm, rag_tool),
    }

    tasks = create_tasks(project_name, agents)
    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff(inputs={"project_name": project_name})
    write_static_output_files(project_name)
    return str(result)


def main() -> None:
    load_dotenv()
    project_name = input("Enter Project Name [Build a Food Delivery App]: ").strip()
    project_name = project_name or "Build a Food Delivery App"

    try:
        result = run_project_manager(project_name)
    except Exception as exc:
        raise SystemExit(f"AI Project Manager failed: {exc}") from exc

    print("\n===== FINAL OUTPUT =====\n")
    print(result)
    print(f"\nGenerated files saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
