from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from agents.agentState import AgentState
import os
from dotenv import load_dotenv
from connectionManager import manager
from .loadModel import llm_small as llm
import re

load_dotenv()


SYSTEM_PROMPT = """You are an expert bug detection engineer reviewing a GitHub Pull Request diff.

You will receive:
- The changed lines (diff) showing what was added or removed
- The full file so you have complete context

Rules:
- Focus your review on the CHANGED lines
- Use the full file ONLY for context (imports, existing functions, class structure)
- Do not flag issues in unchanged code outside the diff
- Do not hallucinate issues that aren't present
- If there are no bugs, respond with "No bugs found"

For each bug found provide:
- The specific code snippet from the diff
- What the bug is
- How to fix it"""

async def bug_node(state: AgentState):
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Diff: {state['diff']}")
    ]
    
    response = llm.invoke(messages)
    raw = response.content.strip()

    return {"findings": [{"type": "bug", "content": raw}]}