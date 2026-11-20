from dotenv import load_dotenv
load_dotenv(override=True)

import os
from crewai import LLM
from crewai_tools import SerperDevTool

# 1. Keys present?
for key in ["OPENAI_API_KEY", "SERPER_API_KEY"]:
    print(key, "OK" if os.getenv(key) else "MISSING")

# 2. LLM works?
llm = LLM(model="gpt-4o-mini")
print("LLM says:", llm.call("Reply with one short line: setup works."))

# 3. Serper works?
search = SerperDevTool()
result = search.run(search_query="millet meal box delivery Coimbatore")
print("Search result (first 500 chars):\n", str(result)[:500])