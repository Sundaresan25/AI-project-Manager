from crewai import Agent

def get_architect_agent(llm, rag_tool):
    return Agent(
        role="Software Architect",
        goal="Design system architecture",
        backstory="Expert in scalable systems",
        llm=llm,
        tools=[rag_tool],
        verbose=True
    )