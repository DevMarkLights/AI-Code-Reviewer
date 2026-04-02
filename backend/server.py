from fastapi import FastAPI, File, UploadFile, Body, Form, WebSocket, WebSocketDisconnect
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from connectionManager import manager
from fastapi.responses import FileResponse


from langgraph.graph import StateGraph, END
from agents.agentState import AgentState
from langgraph.types import Send
from agents.bugAgent import bug_node
from agents.securityAgent import security_node
from agents.performanceAgent import performance_node
from agents.writerAgent import writer_node
from pathlib import Path
from agents.loadModel import llm_small, llm_large #load model one time
from fetchDiff import fetch_diff
from fetchDiff import postComment

import logging

logging.basicConfig(level=logging.ERROR)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)
logging.getLogger("uvicorn.error").setLevel(logging.INFO)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,   # MUST be FALSE
    allow_methods=["*"],
    allow_headers=["*"],
)

def fan_out(state: AgentState):
    return [
        Send("bug", {"diff": state["diff"]}),
        Send("security", {"diff": state["diff"]}),
        Send("performance", {"diff": state["diff"]}),
    ]

def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node('fanOut', lambda state : state)
    graph.add_node("bug", bug_node)
    graph.add_node("security", security_node)
    graph.add_node("performance", performance_node)
    graph.add_node('writer', writer_node)
    
    graph.set_entry_point("fanOut")

    graph.add_conditional_edges('fanOut',fan_out)

    graph.add_edge("bug", "writer")
    graph.add_edge("security", "writer")
    graph.add_edge("performance", 'writer')
    
    graph.add_edge('writer', END)

    return graph.compile()

code_Reviewer = build_graph()


@app.post('/getReview')
async def getReview(body: dict = Body(...)):
    
    url = 'https://github.com/DevMarkLights/AI-Code-Reviewer/pull/1'

    if 'url' in body:
        diff = await fetch_diff(url)
    else:
        return {'result', 'no url provided'}
    
    # get PR diff
    result : AgentState = await code_Reviewer.ainvoke({'diff':diff, 'findings': [], 'finalReview': ''})
    
    await postComment(url=url,comment=result['finalReview'])
    
    return {'result': result['finalReview']}
    

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8085,
        log_level="debug",
        reload=True,
        ws_ping_interval=30, 
        ws_ping_timeout=300
    )