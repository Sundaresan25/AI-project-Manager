from crewai import Agent

def get_business_agent(llm, rag_tool):
    return Agent(
        role="Business Analyst",
        goal="Analyze project requirements",
        backstory="Expert in product planning",
        llm=llm,
        tools=[rag_tool],
        verbose=True
    )