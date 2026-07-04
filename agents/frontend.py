from __future__ import annotations

from runtime_paths import configure_crewai_storage

configure_crewai_storage()

from crewai import Agent, LLM
from crewai.tools import BaseTool


def get_frontend_agent(llm: LLM, rag_tool: BaseTool) -> Agent:
    return Agent(
        role="Frontend Developer",
        goal=(
            "Design a complete React application plan with routing, pages, components, "
            "dashboard workflows, state management, API integration, and auth UI."
        ),
        backstory=(
            "You are a senior frontend engineer who creates accessible, maintainable "
            "React applications with clean component boundaries and user-focused flows."
        ),
        llm=llm,
        tools=[rag_tool],
        verbose=True,
    )
