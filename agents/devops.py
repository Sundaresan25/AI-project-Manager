from __future__ import annotations

from runtime_paths import configure_crewai_storage

configure_crewai_storage()

from crewai import Agent, LLM
from crewai.tools import BaseTool


def get_devops_agent(llm: LLM, rag_tool: BaseTool) -> Agent:
    return Agent(
        role="DevOps Engineer",
        goal=(
            "Create deployment-ready infrastructure guidance with Docker, Compose, "
            "nginx, environment management, CI/CD, observability, and runbooks."
        ),
        backstory=(
            "You are a platform engineer who ships reliable Python and React systems. "
            "You emphasize repeatable builds, secrets hygiene, health checks, backups, "
            "and simple deployment operations."
        ),
        llm=llm,
        tools=[rag_tool],
        verbose=True,
    )
