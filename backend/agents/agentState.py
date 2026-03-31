from typing import TypedDict, List, Optional, Annotated
import operator

class AgentState(TypedDict):
    diff: str                               # pull request 
    findings: Annotated[list, operator.add] # findings from agents     
    finalReview: Optional[str]              # conclusion
    clientID: str                           # clientId for websocket
