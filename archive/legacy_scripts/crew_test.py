from crewai import Agent, Task, Crew

researcher = Agent(
    role="Researcher",
    goal="Find information",
    backstory="Expert researcher",
    verbose=True
)

task = Task(
    description="Tell me about AI assistants",
    agent=researcher,
    expected_output="A short explanation"
)

crew = Crew(
    agents=[researcher],
    tasks=[task],
    verbose=True
)

result = crew.kickoff()
print(result)