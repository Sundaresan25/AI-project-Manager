from __future__ import annotations

from typing import Type

from runtime_paths import configure_crewai_storage

configure_crewai_storage()

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from rag import get_relevant_context


class RagToolInput(BaseModel):
    query: str = Field(..., description="Search query for project-management technical context.")


class RagTool(BaseTool):
    name: str = "Local RAG Knowledge Search"
    description: str = (
        "Searches the local ChromaDB knowledge base for architecture, FastAPI, React, "
        "PostgreSQL, Docker, and deployment guidance."
    )
    args_schema: Type[BaseModel] = RagToolInput

    def _run(self, query: str) -> str:
        return get_relevant_context(query)
