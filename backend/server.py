from asyncio import subprocess

from fastapi import FastAPI, File, HTTPException, Request, UploadFile, Body, Form, WebSocket, WebSocketDisconnect
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from connectionManager import manager
from fastapi.responses import FileResponse
import asyncio

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
import os
from dotenv import load_dotenv
load_dotenv()

DEPLOY_SECRET = os.getenv("USE_LOCAL")

import logging

logging.basicConfig(level=logging.ERROR)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)
logging.getLogger("uvicorn.error").setLevel(logging.INFO)

BASE_DIR = Path(__file__).parent


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://marks-pi.com/"],
    allow_credentials=False,   # MUST be FALSE
    allow_methods=["*"],
    allow_headers=["*"],
)

def fan_out(state: AgentState):
    return [
        Send("bug", state),
        Send("security", state),
        Send("performance", state),
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


@app.post('/ai-code-reviewer/getReview')
async def getReview(body: dict = Body(...)):
    
    url = ""
    client_id = ''
    diff = ''
    if 'url' in body and 'client_id' in body:
        url = body['url']
        diff = await fetch_diff(url)
        client_id = body['client_id'] 
        await manager.broadcast(message={'message':'Found pull request'}, client_id=client_id)
    else:
        return {'result', 'no url provided'}
    
    try:
        
        result : AgentState = await code_Reviewer.ainvoke({'diff':diff, 'findings': [], 'finalReview': '', 'clientID': client_id})
        
        await manager.broadcast(message={'message':'posting comment'}, client_id=client_id)
        
        await postComment(url=url,comment=result['finalReview'])
        
    except Exception as e:
        logging.error(msg=e)
        return {'result': 'Agents context/limits Exceeded. Please try again in few minutes.'}
        
    return {'result': result['finalReview']}

@app.websocket("/ai-code-reviewer/ws")
async def websocket_endpoint(websocket: WebSocket, client_id: str=None):
    await manager.connect(websocket,client_id=client_id)
    
    async def keepalive():
        while True:
            await asyncio.sleep(10)  # ping every 10 seconds for keep alive
            try:
                await websocket.send_json({"ping": True})
            except:
                break

    task = asyncio.create_task(keepalive())
    try:
        while True:
            await websocket.receive() # keep alive
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f'Websocket error {e}')
    
    finally:
        manager.disconnect(websocket=websocket,clientID=client_id)
        

@app.post("/ai-code-reviewer/deploy")
async def deploy(request: Request):
    body = await request.json()
    if body.get("secret") != DEPLOY_SECRET:
        raise HTTPException(status_code=401)
    
    
    subprocess.Popen(["bash", f"/mnt/nvme/AI-Code-Reviewer/deploy.sh"])
    return {"status": "deploying", "service": 'AI-Code-Reviewer'}
        

app.mount("/ai-code-reviewer", StaticFiles(directory="dist", html=True), name="static")

    

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