from crewai import Task
from agents import market_researcher, review_analyst, strategy_analyst, report_writer

research_task = Task(
    description=(
        "Research the market for this business idea:\n"
        "- Business idea: {business_idea}\n"
        "- City: {city}\n"
        "- Target customer: {target_customer}\n"
        "- Competitors the founder already knows: {known_competitors}\n\n"
        "Method:\n"
        "1. Run at least 6 different searches, including millet-specific ones "
        "(e.g. 'millet meals delivery {city}', 'millet tiffin subscription {city}'), "
        "Swiggy/Zomato-style searches, and Instagram/WhatsApp-based home "
        "kitchens in {city}.\n"
        "2. Pick 3 to 5 REAL businesses that deliver in {city}. Directories, "
        "listing sites and aggregators are NOT competitors: use them only to "
        "discover businesses.\n"
        "3. Open each competitor's own website with the scrape tool to find "
        "plan prices and offers. If the page cannot be scraped, use the price "
        "shown in a search result and say so.\n"
        "4. List a sales channel ONLY if you saw evidence for it (a link, a "
        "WhatsApp number, an Instagram page, an app listing).\n"
        "Never guess. Prefer 'not found' over an assumption."
    ),
    expected_output=(
        "A markdown list of 3 to 5 competitors. For each: Name, Website, "
        "City coverage, Is it millet-focused (yes/no/partly), Products, "
        "Prices (with plan names), Offers, Sales channels, and the Source URL "
        "next to EVERY price, offer or channel. Write 'not found' for any "
        "missing detail."
    ),
    agent=market_researcher,
)

review_task = Task(
    description=(
        "Using the competitors from the previous task, find out what "
        "customers say about each one. Business idea: {business_idea} in "
        "{city}, aimed at {target_customer}.\n\n"
        "Strict evidence rules:\n"
        "- Only report a like or complaint if you read it in a review, "
        "comment or thread. Do not infer or generalise.\n"
        "- The source must be about THIS business in {city}/India. Check the "
        "domain and location. Ignore same-name businesses elsewhere "
        "(e.g. a Dutch or US company with a similar name).\n"
        "- Use the scrape tool on review pages (Justdial, Reddit threads, "
        "Google or Zomato listings) where possible. If a page can't be read, "
        "use only what the search snippet actually says.\n"
        "- Record the star rating and number of reviews when shown.\n"
        "- If you find a rating but no review text, report just the rating "
        "and write 'No review text found'. 'Insufficient evidence' is an "
        "acceptable answer."
    ),
    expected_output=(
        "For each competitor: Rating (stars, number of reviews, platform), "
        "Likes (each with a short evidence note and URL), Complaints (each "
        "with a short evidence note and URL), and Confidence "
        "(high / medium / low). Never list a complaint without a source URL."
    ),
    agent=review_analyst,
    context=[research_task],
)
strategy_task = Task(
    description=(
        "You are advising a founder who wants to launch: {business_idea} "
        "in {city}, for {target_customer}.\n\n"
        "Using ONLY the competitor research and customer review findings "
        "from the previous tasks:\n"
        "1. Build a comparison matrix of the competitors (price, millet "
        "focus, sales channels, rating, main complaint).\n"
        "2. Identify the market gap: what customers want that nobody serves "
        "well, especially around millet, price, convenience and variety.\n"
        "3. Recommend a price range per meal and per month. Anchor it to the "
        "competitor prices that were actually found, and explain the logic. "
        "If few prices were found, say so and give a range to validate.\n"
        "4. Recommend positioning: who to target, the one-line promise, "
        "and 3 differentiators.\n\n"
        "Rules: do not add facts or numbers that are not in the earlier "
        "outputs. Label every recommendation as 'Recommendation' and every "
        "data point as 'Data'. Flag weak evidence."
    ),
    expected_output=(
        "A markdown document with these sections:\n"
        "1. Comparison matrix (a markdown table, with source links kept)\n"
        "2. Market gap (3 to 5 bullets, each tied to evidence)\n"
        "3. Pricing recommendation (range + reasoning + what to validate)\n"
        "4. Positioning (target, one-line promise, 3 differentiators)\n"
        "5. Evidence gaps (what was missing or weak, and how to check it)"
    ),
    agent=strategy_analyst,
    context=[research_task, review_task],
)
report_task = Task(
    description=(
        "Write the final report for a founder who wants to launch: "
        "{business_idea} in {city}, for {target_customer}.\n\n"
        "Use ONLY information from the previous tasks. Never invent a "
        "competitor, price, rating or review. If something was not found, "
        "write 'not found'.\n\n"
        "Number every source you use as [1], [2], [3]... and put the matching "
        "number right after each price or claim. Keep the report short and "
        "scannable, about one page.\n\n"
        "Then save the complete report with the file writer tool using "
        "filename 'report.md', directory 'output' and overwrite set to true. "
        "After saving, reply with the full report text as your final answer."
    ),
    expected_output=(
        "A markdown report in EXACTLY this structure:\n\n"
        "# Competitor Report: <business idea>, <city>\n\n"
        "## 1. Key Competitors\n"
        "A markdown table with exactly these columns: Competitor | "
        "Price / meal | Channel | Customer rating | Strength | Weakness. "
        "One row per real competitor (3 to 5 rows).\n"
        "- Price / meal: in Rs, with a source number like [1]. If only a "
        "monthly plan price was found, show 'Rs X / month' instead of "
        "guessing a per-meal price.\n"
        "- Channel: only the channels with evidence, such as own website, "
        "WhatsApp, Instagram, Swiggy or Zomato.\n"
        "- Customer rating: the star rating exactly as found, with the review "
        "count and platform, like '4.5 ★ (28 reviews, Justdial) [3]'. If no "
        "rating was found, write 'not found'. Never average or estimate a "
        "rating.\n"
        "- Strength: a short phrase (max 8 words) based on what customers "
        "like or what the competitor clearly does well.\n"
        "- Weakness: a short phrase (max 8 words) based on a customer "
        "complaint or a clear gap. If there is no evidence, write 'not "
        "found'.\n"
        "Put a source number after each price, rating and weakness.\n\n"
        "## 2. What Customers Complain About\n"
        "3 to 5 bullets. Each bullet is one recurring complaint with the "
        "competitor names in brackets, e.g. (CompetitorA, CompetitorB), and a "
        "source number. Only complaints backed by a source.\n\n"
        "## 3. Market Gap\n"
        "2 to 3 sentences: what nobody offers well, tied to the complaints "
        "and prices above.\n\n"
        "## 4. Recommended Positioning\n"
        "One line in quotes with the promise and a suggested price, then 2 to "
        "3 short bullets explaining the price logic and what to validate "
        "first. Base the price on the competitor prices found.\n\n"
        "## 5. 30-Day Launch Plan\n"
        "Four bullets: '**Week 1:**', '**Week 2:**', '**Week 3:**', "
        "'**Week 4:**'. Each has 1 to 2 concrete actions that follow from "
        "the market gap.\n\n"
        "## Sources\n"
        "A bullet list, one per line: '- [1] full URL', '- [2] full URL'... "
        "Every number used above must appear here."
    ),
    agent=report_writer,
    context=[research_task, review_task, strategy_task],
)