from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from agents.agentState import AgentState
import os
from dotenv import load_dotenv
from connectionManager import manager
from .loadModel import llm_small as llm
import re
from connectionManager import manager

load_dotenv()

SYSTEM_PROMPT = """You are a GitHub code review comment writer. 
Given findings from bug, security, and performance agents, write a clean structured markdown comment.

Output format must be exactly:
## 🐛 Bug Detection
<bug findings or "No bugs found">

## 🔒 Security Review
<security findings or "No security issues found">

## ⚡ Performance Review
<performance findings or "No performance issues found">

Rules:
- Be concise and specific
- Only include what the agents found
- Do not reference specific line numbers, reference the code snippet instead
- Do not add suggestions beyond what the agents reported
- Do not recommend libraries or frameworks not already in the code"""

async def writer_node(state: AgentState):
    await manager.broadcast(message='writer agent has all findings', client_id=state['clientID'])
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Diff: {state['findings']}")
    ]
    
    response = llm.invoke(messages)
    raw = response.content.strip()
    
    await manager.broadcast(message='writer agent is finished', client_id=state['clientID'])
    
    return {"finalReview": raw}