from pathlib import Path
from crewai import Crew, Process
from agents import market_researcher, review_analyst, strategy_analyst, report_writer
from tasks import research_task, review_task, strategy_task, report_task

REPORT_PATH = Path("output/report.md")


def build_crew() -> Crew:
    return Crew(
        agents=[market_researcher, review_analyst, strategy_analyst, report_writer],
        tasks=[research_task, review_task, strategy_task, report_task],
        process=Process.sequential,
        verbose=True,
    )


def run_launchscout(business_idea, city, target_customer, known_competitors=""):
    inputs = {
        "business_idea": business_idea.strip(),
        "city": city.strip(),
        "target_customer": target_customer.strip(),
        "known_competitors": known_competitors.strip() or "None",
    }
    REPORT_PATH.unlink(missing_ok=True)
    result = build_crew().kickoff(inputs=inputs)

    # Prefer the file the Report Writer saved; fall back to the final answer
    if REPORT_PATH.exists():
        return REPORT_PATH.read_text(encoding="utf-8")
    return result.raw