def main():
    import uvicorn
    uvicorn.run("h_world.fastapi_app:app", host="127.0.0.1", port=8000, reload=True)