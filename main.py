# Need to install FastAPI, Uvicorn, Jinja2, SQLAlchemy (Maybe psycopg2 for PostgreSQL)
# Type "pip install -r requirements.txt" in terminal to download all dependencies
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # This file uses Jinja2 to send data to the frontend
    return templates.TemplateResponse("index.html", {"request": request})

print("Hello, World!")
