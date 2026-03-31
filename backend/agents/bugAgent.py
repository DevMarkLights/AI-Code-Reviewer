from agentState import AgentState
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from agentState import AgentState
import os
from dotenv import load_dotenv
from connectionManager import manager
from .loadModel import llm_small as llm
import re

load_dotenv()


SYSTEM_PROMPT = """You are an expert in bug detection of code. 
Given a pull request diff provide bug detection suggestions if they are any"""

async def bug_node(state: AgentState):
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Diff: {state['diff']}")
    ]
    
    response = llm.invoke(messages)
    raw = response.content.strip()

    return {"findings": [{"type": "bug", "content": ""}]}