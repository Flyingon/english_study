from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sys
import os

# Ensure the parent directory is in the path to allow absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from agents.vocabulary_agent.api.routes import router
from agents.vocabulary_agent.config import settings
import uvicorn

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Serve static files (CSS, JS)
static_dir = os.path.join(os.path.dirname(__file__), "web/static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    # Serve the main HTML page
    index_path = os.path.join(os.path.dirname(__file__), "web/index.html")
    return FileResponse(index_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8091)
