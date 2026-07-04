from __future__ import annotations

from runtime_paths import configure_crewai_storage

configure_crewai_storage()

from crewai import Agent, LLM
from crewai.tools import BaseTool


def get_backend_agent(llm: LLM, rag_tool: BaseTool) -> Agent:
    return Agent(
        role="Backend Developer",
        goal=(
            "Produce a complete backend implementation plan with FastAPI structure, "
            "SQLAlchemy models, CRUD APIs, JWT authentication, migrations, and errors."
        ),
        backstory=(
            "You are a senior Python backend engineer who builds clean service layers, "
            "predictable APIs, secure auth, and production-friendly FastAPI projects."
        ),
        llm=llm,
        tools=[rag_tool],
        verbose=True,
    )
