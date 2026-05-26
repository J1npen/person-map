from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from query_engine import process_user_request
import uvicorn

app = FastAPI(title="Multi-User Person Info API")

class QueryRequest(BaseModel):
    user_id: str
    query: str

@app.get("/")
def read_root():
    return {"message": "Welcome to Multi-User Person Info API"}

@app.post("/query")
def process_query(request: QueryRequest):
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    if not request.user_id:
        raise HTTPException(status_code=400, detail="User ID is required for data isolation")
    
    answer = process_user_request(request.user_id, request.query)
    return {"answer": answer}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
