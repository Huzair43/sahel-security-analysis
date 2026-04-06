"""
RAG layer: Retrieval-Augmented Generation for the Sahel Security chatbot.

Backend-agnostic: extracts structured context from the ACLED DataFrame
based on the user's question, then formats a prompt for any LLM backend
(Gemma via Ollama or Gemma via Groq).

Pipeline:
  1. detect_intent()  : identify countries, years, event types, actors
  2. retrieve()       : query the DataFrame, return stats as a dict
  3. build_prompt()   : assemble system prompt + context + user question
"""

import re
from typing import Any

import pandas as pd

from flask_app.utils.data_loader import load_main_data

# ── Constants ──────────────────────────────────────────────────────────────────

COUNTRIES = ["Burkina Faso", "Mali", "Niger"]

EVENT_TYPES = [
    "Battles",
    "Violence against civilians",
    "Explosions/Remote violence",
    "Protests",
    "Riots",
    "Strategic developments",
]

YEARS = list(range(2020, 2026))

SYSTEM_PROMPT = """You are a conflict data analyst specialized in the Sahel region \
(Burkina Faso, Mali, Niger). You answer questions using ACLED conflict data \
from 2020 to 2025.

Rules:
- Be concise and factual. Use numbers from the context provided.
- If the context does not contain enough information to answer, say so clearly.
- Do not fabricate statistics. Only use what is in the context.
- Answer in the same language as the user's question.
- Format numbers with thousands separators (e.g. 1,842).
"""


# ── Intent detection ───────────────────────────────────────────────────────────

def detect_intent(question: str) -> dict[str, Any]:
    """
    Extract entities from the user's question.
    Returns a dict with keys: countries, years, event_types, keywords.
    """
    q = question.lower()

    # Countries
    countries = [c for c in COUNTRIES if c.lower() in q]
    # Normalize common aliases
    if "burkina" in q and "Burkina Faso" not in countries:
        countries.append("Burkina Faso")

    # Years
    years = [y for y in YEARS if str(y) in q]

    # Event types (partial match)
    event_types = [
        et for et in EVENT_TYPES
        if any(word in q for word in et.lower().split())
        and et.lower() not in ("protests", "riots")  # too common as words
    ]
    # Explicit checks for short keywords
    if "battle" in q or "battles" in q:
        if "Battles" not in event_types:
            event_types.append("Battles")
    if "protest" in q:
        if "Protests" not in event_types:
            event_types.append("Protests")
    if "riot" in q:
        if "Riots" not in event_types:
            event_types.append("Riots")
    if "explosion" in q or "remote" in q or "ied" in q:
        if "Explosions/Remote violence" not in event_types:
            event_types.append("Explosions/Remote violence")
    if "civilian" in q or "civilians" in q:
        if "Violence against civilians" not in event_types:
            event_types.append("Violence against civilians")

    # General keywords
    keywords = {
        "fatalities": any(w in q for w in ["fatal", "dead", "death", "killed", "mort", "tué"]),
        "trend":      any(w in q for w in ["trend", "evolution", "increase", "decrease", "tendance", "évolution"]),
        "hotspot":    any(w in q for w in ["hotspot", "worst", "most affected", "zone", "region", "région"]),
        "actor":      any(w in q for w in ["actor", "group", "jnim", "iswap", "armed", "acteur", "groupe"]),
        "compare":    any(w in q for w in ["compar", "versus", "vs", "difference", "between"]),
        "summary":    any(w in q for w in ["summary", "overview", "total", "overall", "résumé", "général"]),
    }

    return {
        "countries":   countries,
        "years":       years,
        "event_types": event_types,
        "keywords":    keywords,
    }


# ── Data retrieval ─────────────────────────────────────────────────────────────

def retrieve(intent: dict[str, Any]) -> dict[str, Any]:
    """
    Query the ACLED DataFrame based on detected intent.
    Returns a structured dict of statistics used as RAG context.
    """
    df = load_main_data()

    # Apply filters
    mask = pd.Series(True, index=df.index)

    if intent["countries"]:
        mask &= df["country"].isin(intent["countries"])

    if intent["years"]:
        mask &= df["year"].isin(intent["years"])

    if intent["event_types"]:
        mask &= df["event_type"].isin(intent["event_types"])

    subset = df[mask]

    if subset.empty:
        # Fallback: no filter on event_types if it yields nothing
        mask2 = pd.Series(True, index=df.index)
        if intent["countries"]:
            mask2 &= df["country"].isin(intent["countries"])
        if intent["years"]:
            mask2 &= df["year"].isin(intent["years"])
        subset = df[mask2]

    ctx: dict[str, Any] = {
        "total_incidents": len(subset),
        "total_fatalities": int(subset["fatalities"].sum()),
        "date_range": (
            str(subset["event_date"].min())[:10],
            str(subset["event_date"].max())[:10],
        ),
    }

    # Breakdown by country
    ctx["by_country"] = (
        subset.groupby("country")
        .agg(incidents=("event_id_cnty", "count"), fatalities=("fatalities", "sum"))
        .rename_axis("country")
        .reset_index()
        .to_dict(orient="records")
    )

    # Breakdown by event type
    ctx["by_event_type"] = (
        subset.groupby("event_type")
        .agg(incidents=("event_id_cnty", "count"), fatalities=("fatalities", "sum"))
        .sort_values("incidents", ascending=False)
        .reset_index()
        .to_dict(orient="records")
    )

    # Top 5 regions
    ctx["top_regions"] = (
        subset.groupby(["country", "admin1"])
        .agg(incidents=("event_id_cnty", "count"), fatalities=("fatalities", "sum"))
        .sort_values("fatalities", ascending=False)
        .head(5)
        .reset_index()
        .to_dict(orient="records")
    )

    # Top 5 actors
    ctx["top_actors"] = (
        subset.groupby("actor1")
        .agg(incidents=("event_id_cnty", "count"))
        .sort_values("incidents", ascending=False)
        .head(5)
        .reset_index()
        .to_dict(orient="records")
    )

    # Yearly trend (only if not filtered on a single year)
    if not intent["years"] or len(intent["years"]) > 1:
        ctx["yearly_trend"] = (
            subset.groupby("year")
            .agg(incidents=("event_id_cnty", "count"), fatalities=("fatalities", "sum"))
            .reset_index()
            .to_dict(orient="records")
        )

    # Deadliest single incident
    if not subset.empty:
        worst = subset.nlargest(1, "fatalities").iloc[0]
        ctx["deadliest_incident"] = {
            "date":       str(worst["event_date"])[:10],
            "location":   worst.get("location", ""),
            "country":    worst.get("country", ""),
            "event_type": worst.get("event_type", ""),
            "actor":      worst.get("actor1", ""),
            "fatalities": int(worst["fatalities"]),
        }

    return ctx


# ── Prompt builder ─────────────────────────────────────────────────────────────

def _fmt(ctx: dict[str, Any]) -> str:
    """Format the retrieved context as readable text for the LLM."""
    lines = []

    lines.append(f"Total incidents: {ctx['total_incidents']:,}")
    lines.append(f"Total fatalities: {ctx['total_fatalities']:,}")
    lines.append(f"Date range: {ctx['date_range'][0]} to {ctx['date_range'][1]}")

    if ctx.get("by_country"):
        lines.append("\nBreakdown by country:")
        for row in ctx["by_country"]:
            lines.append(
                f"  {row['country']}: {row['incidents']:,} incidents, "
                f"{int(row['fatalities']):,} fatalities"
            )

    if ctx.get("by_event_type"):
        lines.append("\nBreakdown by event type:")
        for row in ctx["by_event_type"]:
            lines.append(
                f"  {row['event_type']}: {row['incidents']:,} incidents, "
                f"{int(row['fatalities']):,} fatalities"
            )

    if ctx.get("top_regions"):
        lines.append("\nTop 5 most affected regions:")
        for row in ctx["top_regions"]:
            lines.append(
                f"  {row['admin1']} ({row['country']}): "
                f"{row['incidents']:,} incidents, {int(row['fatalities']):,} fatalities"
            )

    if ctx.get("top_actors"):
        lines.append("\nTop 5 most active armed groups:")
        for row in ctx["top_actors"]:
            lines.append(f"  {row['actor1']}: {row['incidents']:,} incidents")

    if ctx.get("yearly_trend"):
        lines.append("\nYearly trend:")
        for row in ctx["yearly_trend"]:
            lines.append(
                f"  {int(row['year'])}: {row['incidents']:,} incidents, "
                f"{int(row['fatalities']):,} fatalities"
            )

    if ctx.get("deadliest_incident"):
        d = ctx["deadliest_incident"]
        lines.append(
            f"\nDeadliest single incident: {d['date']} in {d['location']} "
            f"({d['country']}), {d['fatalities']:,} fatalities, "
            f"{d['event_type']} by {d['actor']}"
        )

    return "\n".join(lines)


def build_prompt(question: str, context: dict[str, Any]) -> list[dict[str, str]]:
    """
    Build the messages list for the LLM (OpenAI-compatible format).
    Returns: [{"role": "system", ...}, {"role": "user", ...}]
    """
    context_text = _fmt(context)

    user_message = (
        f"Context (ACLED data):\n{context_text}\n\n"
        f"Question: {question}"
    )

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_message},
    ]


# ── Main entry point ───────────────────────────────────────────────────────────

def get_rag_prompt(question: str) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """
    Full RAG pipeline: detect intent, retrieve data, build prompt.
    Returns (messages, context). Context is kept for logging/debugging.
    """
    intent  = detect_intent(question)
    context = retrieve(intent)
    messages = build_prompt(question, context)
    return messages, context
