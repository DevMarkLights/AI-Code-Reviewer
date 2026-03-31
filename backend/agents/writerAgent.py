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

SYSTEM_PROMPT = """You are an expert github comment writer of code. Given a results from bug, security, and performance Agent request diff provide bug detection suggestions if they are any"""

async def writer_node(state: AgentState):
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Diff: {state['results']}")
    ]
    
    response = llm.invoke(messages)
    raw = response.content.strip()