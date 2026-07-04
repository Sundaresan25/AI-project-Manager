from crewai import Task, Crew, LLM
from dotenv import load_dotenv
from agents.business import get_business_agent
from agents.architect import get_architect_agent
import os
from rag import rag_tool
load_dotenv()


# =========================
# LLM (IMPORTANT FIX)
# =========================
llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)

project_name = input("Enter Project Name: ")

# =========================
# AGENTS
# =========================
business_agent = get_business_agent(llm, rag_tool)
architect_agent = get_architect_agent(llm, rag_tool)

# =========================
# TASKS
# =========================
business_task = Task(
    description=f"""
You are a Business Analyst.

Project: {project_name}

Generate:
1. Overview
2. Features
3. Users
4. MVP Plan
""",
    expected_output="A comprehensive business analysis document with overview, key features, target users, and MVP plan",
    agent=business_agent
)

architect_task = Task(
    description=f"""
You are a Software Architect.

Project: {project_name}

Use knowledge base if needed.

Generate:
1. Tech Stack
2. Database Design
3. API Design
4. System Architecture
5. Deployment Plan
""",
    expected_output="A detailed technical architecture document with tech stack, database schema, API specifications, system design, and deployment strategy",
    agent=architect_agent
)

# =========================
# CREW
# =========================
crew = Crew(
    agents=[business_agent, architect_agent],
    tasks=[business_task, architect_task],
    verbose=True
)

result = crew.kickoff()

print("\n===== FINAL OUTPUT =====\n")
print(result)

with open("project_report.md", "w", encoding="utf-8") as f:
    f.write(str(result))

print("\nSaved: project_report.md")