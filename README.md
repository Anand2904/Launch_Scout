# 🔭 LaunchScout: Competitor Research Crew

A team of four AI agents that researches the market for a new business idea and delivers a short, sourced competitor report with prices, customer ratings, market gaps and a 30-day launch plan.

Built with **CrewAI** and **Streamlit** as part of an Agentic AI certification project.

> **Example:** a founder wants to launch a healthy millet meal box service in Coimbatore. Before spending money they need to know who the competitors are, what they charge, what customers complain about and where the gap is. This normally takes a marketing intern 2 to 3 days. LaunchScout does a first pass in a few minutes.

---

## What it does

1. The founder fills a form: business idea, city, target customer and optional known competitors.
2. Four agents work in sequence, each handing its output to the next.
3. The app shows a **live agent diagram and trace** while they work.
4. The final report is displayed in the app and can be downloaded as Markdown.

## The crew

| # | Agent | Goal | Tools |
|---|-------|------|-------|
| 1 | **Market Researcher** | Find 3 to 5 real competitors with prices, offers and sales channels | Serper web search, website scraper |
| 2 | **Review Analyst** | Find what customers like and complain about for each competitor | Serper web search, website scraper |
| 3 | **Strategy Analyst** | Build the comparison, find the market gap, suggest price and positioning | None (reasons on the first two agents' work) |
| 4 | **Report Writer** | Write the founder-friendly report and save it as `report.md` | File writer |

Tasks run with `Process.sequential`. Each task receives earlier outputs through CrewAI's `context`, so the Review Analyst works on the competitors the Researcher found, the Strategy Analyst reads both, and the Report Writer reads all three.

## The report

The report follows a fixed, scannable structure:

1. **Key Competitors**: table with price per meal, channel, customer rating (stars, review count, platform), strength and weakness
2. **What Customers Complain About**: recurring complaints, with competitor names
3. **Market Gap**
4. **Recommended Positioning**: one-line promise and a suggested price range
5. **30-Day Launch Plan**: week by week
6. **Sources**: numbered links; every price, rating and complaint carries a `[n]` reference

## Features

- Streamlit form with input validation
- Live agent diagram: each agent lights up while working, tool usage is counted, and handoffs between agents are animated
- Timestamped trace log of every tool call and handoff
- Report shown in the app and downloadable as Markdown
- Dark green theme

## How it avoids made-up data

LLM agents tend to sound confident even without evidence, so the prompts are strict:

- Agents may report only facts they actually read, and must write `not found` when a price or rating is missing
- Review claims need a source URL for the right business and city, and a rating is reported exactly as found, never averaged or estimated
- Directories and aggregators are used for discovery only, not listed as competitors
- The Strategy Analyst separates data from recommendations and flags thin evidence

## Tech stack

- Python 3.10 to 3.13 (developed on 3.12)
- [CrewAI](https://github.com/crewAIInc/crewAI) and `crewai-tools` (`SerperDevTool`, `ScrapeWebsiteTool`, `FileWriterTool`)
- [Streamlit](https://streamlit.io) for the UI
- OpenAI `gpt-4o-mini` as the LLM
- `python-dotenv` for configuration

## Project structure

```
launchscout/
├── app.py              # Streamlit UI: form, live diagram, report view
├── agents.py           # The four agents (role, goal, backstory, tools, llm)
├── tasks.py            # The four tasks (description, expected_output, context)
├── crew_builder.py     # Builds the sequential crew and runs it
├── crew_events.py      # Captures CrewAI events for the live trace
├── flow_view.py        # Agent diagram and trace rendering
├── report_style.py     # CSS for the report view
├── check_setup.py      # Smoke test for API keys, LLM and Serper
├── test_run.py         # Run the crew from the terminal
├── requirements.txt
├── .env.example        # Template for your API keys
└── .streamlit/config.toml   # Theme
```

## Setup

```bash
git clone https://github.com/Anand2904/Launch_Scout.git
cd Launch_Scout

python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then add your own keys
```

Edit `.env`:

```
OPENAI_API_KEY=your_openai_key_here
SERPER_API_KEY=your_serper_key_here
```

You need an OpenAI API key and a free Serper key from [serper.dev](https://serper.dev).

Check the setup:

```bash
python check_setup.py
```

## Run

```bash
streamlit run app.py
```

Open the local URL shown in the terminal, fill in the form and press **Run research**. A full run takes a few minutes and uses a few Serper searches and a small amount of OpenAI credit.

To run the crew without the UI, edit the inputs in `test_run.py` and run:

```bash
python test_run.py
```

## Limitations

- Small local businesses often have few online ratings, so some cells will say `not found`. That is intentional.
- Some sites (for example Justdial and Instagram) may block scraping, so the agents fall back to search snippets.
- Results come from an LLM plus live web search. Verify prices and ratings before making business decisions.

## Roadmap

- PDF export of the report
- Hierarchical process with a manager agent
- Caching research results between runs
- Automated tests

## Security

Never commit your `.env` file. It is listed in `.gitignore`. If a key is ever exposed, regenerate it in the provider's dashboard.

---

Built by [@Anand2904](https://github.com/Anand2904)
