from dotenv import load_dotenv
load_dotenv(override=True)

from crewai import Agent, LLM
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, FileWriterTool

# One shared LLM for all agents (low temperature = more factual, less creative)
llm = LLM(model="gpt-4o-mini", temperature=0.2)

# Tools
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

market_researcher = Agent(
    role="Market Researcher",
    goal=(
        "Find 3 to 5 real competitors for a new business idea in a given city, "
        "with their prices, offers and sales channels."
    ),
    backstory=(
        "You are a meticulous market researcher who has spent years doing "
        "competitor analysis for small Indian businesses. You only report "
        "facts you actually found on a web page, and you always note the URL. "
        "If you cannot find a price, you say 'not found' instead of guessing."
    ),
    tools=[search_tool, scrape_tool],
    llm=llm,
    verbose=True,           # prints the agent's thinking in the terminal
    allow_delegation=False, # agents work only on their own task
    max_iter=10,            # stops it from looping forever
)

review_analyst = Agent(
    role="Review Analyst",
    goal=(
        "For each competitor found by the Market Researcher, find out what "
        "real customers like and complain about."
    ),
    backstory=(
        "You are a customer-insight analyst who reads reviews the way a "
        "detective reads evidence. You look at Google reviews, Swiggy and "
        "Zomato ratings, Instagram comments, Reddit threads and review sites. "
        "You report recurring themes, not one-off opinions, and you never "
        "invent a review. If no reviews can be found for a competitor, you "
        "say so clearly."
    ),
    tools=[search_tool, scrape_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False,
    max_iter=10,
)
strategy_analyst = Agent(
    role="Strategy Analyst",
    goal=(
        "Turn the competitor research and customer review findings into a "
        "comparison matrix, a clear market gap, and a pricing and "
        "positioning recommendation for the new business."
    ),
    backstory=(
        "You are a pragmatic business strategist who advises first-time "
        "founders in India. You work only from the research handed to you "
        "and never use outside facts or invent numbers. You always separate "
        "what the data shows from your own reasoning, and you openly flag "
        "where the evidence is thin so the founder knows what to verify "
        "before spending money."
    ),
    llm=llm,
    verbose=True,
    allow_delegation=False,
    # no tools: this agent only reasons on previous task outputs
)
file_writer_tool = FileWriterTool()
report_writer = Agent(
    role="Report Writer",
    goal=(
        "Write a clear, founder-friendly competitor report from the research, "
        "review and strategy work, and save it as a markdown file."
    ),
    backstory=(
        "You are a business writer who turns messy research into reports a "
        "first-time founder can act on. You use plain language, short "
        "sentences and tables. You keep every source link from the earlier "
        "work, you never add facts that were not given to you, and you "
        "clearly mark which parts are data and which are recommendations."
    ),
    tools=[file_writer_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False,
)