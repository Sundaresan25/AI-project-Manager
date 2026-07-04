from __future__ import annotations

from runtime_paths import configure_crewai_storage

configure_crewai_storage()

from crewai import Agent, LLM
from crewai.tools import BaseTool


def get_business_agent(llm: LLM, rag_tool: BaseTool) -> Agent:
    return Agent(
        role="Business Analyst",
        goal=(
            "Transform an app idea into a practical product brief with clear users, "
            "requirements, user stories, and an MVP scope."
        ),
        backstory=(
            "You are a senior product strategist who turns ambiguous founder ideas into "
            "buildable software plans. You use retrieved domain context to keep every "
            "recommendation practical and implementation-aware."
        ),
        llm=llm,
        tools=[rag_tool],
        verbose=True,
    )
