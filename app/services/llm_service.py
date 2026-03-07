import os
import re
import logging
from langchain_xai import ChatXAI
from langchain.agents import create_agent
from langchain_tavily import TavilySearch
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import settings
from app.services.news_service import fetch_news

logger = logging.getLogger(__name__)

# ---------------- Grok LLM Initialization ----------------
XAI_API_KEY = os.getenv("XAI_API_KEY")

if not XAI_API_KEY:
    logger.critical("XAI_API_KEY environment variable not set.")
    # We won't raise ValueError immediately to allow the app to boot if only other endpoints are used,
    # but the endpoints using the LLM will fail.
    llm_model = None
else:
    llm_model = ChatXAI(
        api_key=XAI_API_KEY,
        model="grok-4-fast-reasoning",          # or grok-2-mini for cheaper/faster
        temperature=0,
        max_retries=3,
        timeout=120,
    )


def clean_text(text: str) -> str:
    """
    Fix broken spacing like: 8 0 M i l l i o n -> 80 Million
    """
    text = re.sub(r'(?<=\b\w)\s(?=\w\b)', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def run_agent(topic: str):
    """
    Runs the langchain agent to find news and summarize. 
    (Refactored from src/agent.py)
    """
    if not llm_model:
        raise ValueError("XAI_API_KEY is not configured.")

    # 1. Fetch fresh news from RapidAPI
    news_data = fetch_news(query=topic, limit=3)
    news_context = ""
    if news_data and "data" in news_data:
        for article in news_data["data"]:
            news_context += f"- {article.get('title')}: {article.get('link')}\n"

    search = TavilySearch(max_results=2)

    agent_executor = create_agent(
        model=llm_model,
        tools=[search],
    )

    task_input = (
        f"Find the latest news about {topic}. "
        f"Here is some initial news context to consider:\n{news_context}\n"
        "Summarize the most important findings in clear bullet points."
    )

    response = agent_executor.invoke(
        {"messages": [("user", task_input)]}
    )

    final_text = None

    for msg in reversed(response["messages"]):
        if msg.type == "ai" and msg.content:
            if isinstance(msg.content, list):
                for block in msg.content:
                    if block.get("type") == "text":
                        final_text = block.get("text")
                        break
            elif isinstance(msg.content, str):
                final_text = msg.content

        if final_text:
            break

    if not final_text:
        return "No summary generated."

    return clean_text(final_text)


def summarize_news(topic: str, articles: list[dict]) -> str:
    """
    Takes a list of raw article dicts and returns a polished, 
    broadcast-style news summary produced by the LLM.
    (Refactored from main.py)
    """
    if not llm_model:
        raise ValueError("XAI_API_KEY is not configured.")

    if not articles:
        return "No articles found for this topic."

    article_lines = []
    for i, art in enumerate(articles, 1):
        title     = art.get("title", "(no title)")
        snippet   = art.get("snippet", art.get("description", ""))
        published = art.get("published_datetime", art.get("date", ""))
        link      = art.get("link", art.get("url", ""))
        article_lines.append(
            f"[{i}] TITLE: {title}\n"
            f"    DATE: {published}\n"
            f"    SNIPPET: {snippet}\n"
            f"    URL: {link}"
        )
    raw_context = "\n\n".join(article_lines)

    system_prompt = (
        "You are IndustryEar, a professional AI news anchor. "
        "Your job is to transform raw news headlines into a polished, "
        "engaging audio-ready news brief that is easy and pleasant to hear. "
        "Rules:\n"
        "  1. Open with a warm, one-sentence welcome that names the topic.\n"
        "  2. Present each story in order of importance (most significant first). "
        "     For each story:\n"
        "       a. State the headline clearly.\n"
        "       b. Explain what happened in 2-3 concise sentences.\n"
        "       c. Add one sentence on why it matters to the listener.\n"
        "  3. Separate stories with a transition phrase (e.g., 'Moving on...', 'Next up...').\n"
        "  4. Close with a brief, upbeat sign-off (one sentence).\n"
        "  5. Use plain, conversational English — no bullet points, no markdown.\n"
        "  6. Do NOT invent facts; only use what is in the provided articles."
    )

    human_prompt = (
        f"Topic: {topic}\n\n"
        f"Here are today's articles:\n\n{raw_context}\n\n"
        "Please produce the news summary now, following your anchor guidelines."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt),
    ]

    response = llm_model.invoke(messages)
    return response.content.strip()
