from fastapi import FastAPI
from routers.upload_router import router as upload_router

app = FastAPI()

app.include_router(upload_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}
