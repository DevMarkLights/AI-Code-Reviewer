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


SYSTEM_PROMPT = """You are an expert performance engineer reviewing a GitHub Pull Request diff.

Rules:
- Analyze ONLY the code shown in the diff (lines starting with +)
- Do NOT suggest changes to code outside the diff
- Do NOT hallucinate issues that aren't present
- If there are no performance issues, respond with "No performance issues found"

For each issue found provide:
- The specific line or code snippet from the diff
- What the performance problem is
- How to fix it"""

async def performance_node(state: AgentState):
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Diff: {state['diff']}")
    ]
    
    response = llm.invoke(messages)
    raw = response.content.strip()
    
    return {"findings": [{"type": "perfomance", "content": raw}]}