from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

import os
from dotenv import load_dotenv
load_dotenv()

llm_small = None
llm_large = None
GROQ_MODEL_llama3_1 = None
GROQ_MODEL_GUARD_22 = None
GROQ_MODEL_GUARD_86 = None
GROQ_MODEL_llama3_3 = None
if os.getenv("USE_LOCAL") == 'true':
    print('local model')
    GROQ_MODEL_llama3_1 = ChatOllama(model="llama3.2:3b", temperature=0, max_tokens=4096)
    GROQ_MODEL_GUARD_22 = ChatOllama(model="llama3.2:3b", temperature=0, max_tokens=4096)
    GROQ_MODEL_GUARD_86 = ChatOllama(model="llama3.2:3b", temperature=0, max_tokens=4096)
    GROQ_MODEL_llama3_3 = ChatOllama(model="llama3.2:3b", temperature=0, max_tokens=4096)
else:
    print('cloud model')
    GROQ_MODEL_llama3_1 = ChatGroq(model=os.getenv("GROQ_MODEL_llama3_1"), temperature=0, max_tokens=4096)
    GROQ_MODEL_GUARD_22 = ChatGroq(model=os.getenv("GROQ_MODEL_GUARD_22"), temperature=0, max_tokens=4096)
    GROQ_MODEL_GUARD_86 = ChatGroq(model=os.getenv("GROQ_MODEL_GUARD_86"), temperature=0, max_tokens=4096)
    GROQ_MODEL_llama3_3 = ChatGroq(model=os.getenv("GROQ_MODEL_llama3_3"), temperature=0, max_tokens=4096)