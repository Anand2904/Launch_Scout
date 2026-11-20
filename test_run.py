from crewai import Crew, Process
from agents import market_researcher, review_analyst, strategy_analyst, report_writer
from tasks import research_task, review_task, strategy_task, report_task

crew = Crew(
    agents=[market_researcher, review_analyst, strategy_analyst, report_writer],
    tasks=[research_task, review_task, strategy_task, report_task],
    process=Process.sequential,
    verbose=True,
)

inputs = {
    "business_idea": "Healthy millet meal box subscription service",
    "city": "Coimbatore",
    "target_customer": "Working professionals aged 25-40",
    "known_competitors": "None",
}

result = crew.kickoff(inputs=inputs)

print("\n\n===== FINAL REPORT =====\n")
print(result.raw)
