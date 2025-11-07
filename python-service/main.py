from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time
import uvicorn
from typing import Dict, Any

app = FastAPI(
    title="Fibonacci Web Service",
    description="Python Fibonacci Service for Benchmarking",
    version="1.0.0"
)

class FibonacciResponse(BaseModel):
    number: int
    result: int
    calculation_time_ns: int

class ErrorResponse(BaseModel):
    error: str

def fibonacci(n: int) -> int:
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Fibonacci Web Service - use /fibonacci/{number}"}

@app.get(
    "/fibonacci/{number}",
    response_model=FibonacciResponse,
    responses={400: {"model": ErrorResponse}}
)
async def calculate_fibonacci(number: int) -> FibonacciResponse:
    if number > 90:
        raise HTTPException(
            status_code=400,
            detail="Number too large. Maximum is 90."
        )
    
    start_time = time.perf_counter_ns()
    result = fibonacci(number)
    calculation_time = time.perf_counter_ns() - start_time
    
    return FibonacciResponse(
        number=number,
        result=result,
        calculation_time_ns=calculation_time
    )

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8000
    
    print(f"🚀 Starting Python Fibonacci server on http://{host}:{port}")
    print(f"📊 Test endpoint: http://{host}:{port}/fibonacci/10")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        workers=1,  # Уменьшаем для стабильности
        log_level="info"
    )