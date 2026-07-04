from __future__ import annotations

from runtime_paths import configure_crewai_storage

configure_crewai_storage()

from crewai import Agent, LLM
from crewai.tools import BaseTool


def get_architect_agent(llm: LLM, rag_tool: BaseTool) -> Agent:
    return Agent(
        role="Software Architect",
        goal=(
            "Design secure, scalable, maintainable application architecture including "
            "data models, APIs, authentication, and deployment boundaries."
        ),
        backstory=(
            "You are a principal architect with deep experience in FastAPI, React, "
            "PostgreSQL, containers, cloud deployments, and pragmatic scaling. You "
            "prefer explicit trade-offs and designs teams can implement."
        ),
        llm=llm,
        tools=[rag_tool],
        verbose=True,
    )
