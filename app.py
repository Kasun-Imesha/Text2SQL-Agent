"""
app.py  —  Text2SQL Agent
Runs the autogen agent group chat, extracts the final SQL result,
and displays it as a table / bar chart with an optional debug trace.
"""

import ast
import asyncio
import json
import re

import pandas as pd
import streamlit as st
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat

from agents import (
    get_retriever_agent,
    get_sql_executor_agent,
    get_sql_generator_agent,
    get_sql_validator_agent,
)

# Page config
st.set_page_config(
    page_title="Text2SQL Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS
with open("static/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Hero
st.markdown("""
<div class="hero">
  <h1>Text2SQL Agent</h1>
  <div class="sub">Natural Language → SQL → Results</div>
</div>
""", unsafe_allow_html=True)
st.markdown('<hr class="div">', unsafe_allow_html=True)


# Session state 
if "history" not in st.session_state:
    st.session_state.history = []
if "q" not in st.session_state:
    st.session_state.q = ""


# Agents
async def _run(query: str):
    termination = TextMentionTermination("DONE")
    group_chat = RoundRobinGroupChat(
        participants=[
            get_retriever_agent(),
            get_sql_generator_agent(),
            get_sql_validator_agent(),
            get_sql_executor_agent(),
        ],
        termination_condition=termination,
        max_turns=4,
    )
    return await group_chat.run(task=query)


# Parsers
def parse_result(content: str) -> pd.DataFrame | None:
    """Extract {'columns': [...], 'rows': [...]} dict from executor output."""
    # 1. JSON fenced block
    m = re.search(r"```json\s*([\s\S]+?)```", content)
    if m:
        try:
            data = json.loads(m.group(1).strip())
            if isinstance(data, dict) and "columns" in data and "rows" in data:
                return pd.DataFrame(data["rows"], columns=data["columns"])
        except Exception:
            pass

    # 2. Bare JSON / Python-repr dict
    m = re.search(r"(\{[\s\S]+\})", content)
    if m:
        for parser in (json.loads, ast.literal_eval):
            try:
                data = parser(m.group(1).strip())
                if isinstance(data, dict) and "columns" in data and "rows" in data:
                    return pd.DataFrame(data["rows"], columns=data["columns"])
            except Exception:
                pass

    # 3. JSON array of objects
    m = re.search(r"(\[[\s\S]+\])", content)
    if m:
        for parser in (json.loads, ast.literal_eval):
            try:
                data = parser(m.group(1).strip())
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    return pd.DataFrame(data)
            except Exception:
                pass

    return None


def extract_sql(messages) -> str | None:
    """Return the full SQL query, preferring generator/validator messages."""
    _SQL_RE = re.compile(r"(SELECT\b[\s\S]+?;|SELECT\b[\s\S]+)", re.IGNORECASE)

    for source_filter in (("sql_generator", "sql_validator"), None):
        for msg in messages:
            src = getattr(msg, "source", "").lower()
            if source_filter and src not in source_filter:
                continue
            content = getattr(msg, "content", "")
            if not isinstance(content, str):
                continue
            m = _SQL_RE.search(content)
            if m:
                return m.group(1).strip()
    return None


# Agent trace
_AGENT_COLOURS = {
    "retriever":     "#7ab8f5",
    "sql_generator": "#a78bfa",
    "sql_validator": "#fb923c",
    "sql_executor":  "#4ade80",
}
_AGENT_LABELS = {
    "retriever":     "Schema Retriever",
    "sql_generator": "SQL Generator",
    "sql_validator": "SQL Validator",
    "sql_executor":  "SQL Executor",
}


def _meta(source: str) -> tuple[str, str]:
    key = source.lower()
    for k in _AGENT_COLOURS:
        if k in key:
            return _AGENT_LABELS[k], _AGENT_COLOURS[k]
    return source.title(), "#94a3b8"


def build_trace(messages) -> list[dict]:
    """Filter messages to human-readable agent text turns only."""
    trace = []
    for msg in messages:
        src = getattr(msg, "source", "") or ""
        if src.lower() in ("user", ""):
            continue
        content = getattr(msg, "content", None)
        if not isinstance(content, str) or not content.strip():
            continue
        label, colour = _meta(src)
        trace.append({"label": label, "colour": colour, "content": content.strip()})
    return trace


# Example buttons
EXAMPLES = [
    "Which country has the most customers?",
    "Top 5 best selling products",
    "Total revenue by product category",
    "List customers with more than 3 orders",
]

st.markdown('<div class="ex-label">Try an example →</div>', unsafe_allow_html=True)
ex_cols = st.columns(len(EXAMPLES))
for i, (col, ex) in enumerate(zip(ex_cols, EXAMPLES)):
    with col:
        if st.button(ex, key=f"ex_{i}"):
            # Write directly into the text-area's session-state key so it
            # persists across the next re-render triggered by Run Query.
            st.session_state.q = ex


# Query input
# key="q" means Streamlit reads/writes st.session_state.q automatically.
# No `value=` needed — we manage state via session_state.q above.
st.text_area(
    label="",
    placeholder="Ask anything about your database in plain English…",
    height=88,
    key="q",
    label_visibility="collapsed",
)

run_col, _ = st.columns([1, 6])
with run_col:
    run_btn = st.button("▶  Run Query")

st.markdown('<hr class="div">', unsafe_allow_html=True)


# Execution
query = st.session_state.get("q", "").strip()

if run_btn and query:

    status = st.empty()
    status.markdown('<span class="badge-run">● Running agents…</span>', unsafe_allow_html=True)

    try:
        result = asyncio.run(_run(query))
    except Exception as e:
        status.empty()
        st.markdown(f'<div class="err-block">⚠ Agent error: {e}</div>', unsafe_allow_html=True)
        st.stop()

    messages = result.messages

    # Extract data
    executor_msgs = [
        m for m in messages
        if getattr(m, "source", "").lower() == "sql_executor"
        and isinstance(getattr(m, "content", None), str)
    ]
    df    = parse_result(executor_msgs[-1].content) if executor_msgs else None
    sql   = extract_sql(messages)
    trace = build_trace(messages)

    status.empty()

    # Results
    if df is not None and not df.empty:
        st.markdown("""
        <div class="result-header">
          <span class="result-title">Results</span>
          <span class="badge-done">✓ Complete</span>
        </div>""", unsafe_allow_html=True)

        st.dataframe(df, use_container_width=True, hide_index=True)

        # Auto bar chart for 2-column numeric results
        if len(df.columns) == 2 and pd.api.types.is_numeric_dtype(df.iloc[:, 1]):
            st.markdown('<hr class="div">', unsafe_allow_html=True)
            st.bar_chart(df.set_index(df.columns[0])[df.columns[1]])

    else:
        st.markdown("""
        <div class="result-header">
          <span class="result-title">Result</span>
          <span class="badge-done">✓ Complete</span>
        </div>""", unsafe_allow_html=True)
        raw = executor_msgs[-1].content if executor_msgs else "No output from executor."
        st.text(raw)

    # Generated SQL (always shown if found)
    if sql:
        with st.expander("Generated SQL", expanded=False):
            st.code(sql, language="sql")

    # Agent trace debug expander
    if trace:
        with st.expander("🔍  Agent Trace (debug)", expanded=False):
            for step in trace:
                st.markdown(
                    f'<span style="font-size:0.63rem;letter-spacing:0.14em;'
                    f'text-transform:uppercase;color:{step["colour"]};'
                    f'font-family:\'DM Mono\',monospace">{step["label"]}</span>',
                    unsafe_allow_html=True,
                )
                st.code(step["content"], language="text")

    # Save to history
    st.session_state.history.append({
        "query": query,
        "df":    df,
        "sql":   sql,
        "trace": trace,
    })

elif run_btn:
    st.warning("Please enter a question first.")


# History
if st.session_state.history:
    st.markdown('<hr class="div">', unsafe_allow_html=True)
    st.markdown("**Query History**")
    for item in reversed(st.session_state.history):
        with st.expander(f"⎯⎯  {item['query']}", expanded=False):
            if item["df"] is not None and not item["df"].empty:
                st.dataframe(item["df"], use_container_width=True, hide_index=True)
            if item["sql"]:
                st.code(item["sql"], language="sql")
            if item.get("trace"):
                st.markdown("---")
                st.caption("Agent Trace")
                for step in item["trace"]:
                    st.markdown(
                        f'<span style="font-size:0.63rem;letter-spacing:0.14em;'
                        f'text-transform:uppercase;color:{step["colour"]};'
                        f'font-family:\'DM Mono\',monospace">{step["label"]}</span>',
                        unsafe_allow_html=True,
                    )
                    st.code(step["content"], language="text")
