from fastapi import FastAPI
from pydantic import BaseModel

from graph import graph
from models import SupportResponse


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Zepto Support Assistant",
    description="Policy-aware customer support assistant",
    version="1.0.0"
)


# --------------------------------------------------
# Request model
# --------------------------------------------------

class AskRequest(BaseModel):
    query: str


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Zepto Support Assistant API is running"
    }


# --------------------------------------------------
# POST /ask
# --------------------------------------------------

@app.post(
    "/ask",
    response_model=SupportResponse
)
def ask(request: AskRequest):

    result = graph.invoke({
        "query": request.query
    })

    response = SupportResponse(
        answer=result["answer"],
        sources=result["sources"],
        confidence=result["confidence"]
    )

    return response