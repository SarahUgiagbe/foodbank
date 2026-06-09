# ==============================================================================
# 1. THE TOOLS (Loading the packages we need)
# ==============================================================================
import os  # PYTHON: Lets Python talk to your computer's operating system

from fastapi import FastAPI, Request, Depends  # FASTAPI: Web server and routing tools
from fastapi.responses import HTMLResponse  # FASTAPI: Tool to send back HTML web pages
from fastapi.templating import Jinja2Templates  # FASTAPI: Bridge to drop text into HTML
from fastapi.staticfiles import StaticFiles  # FASTAPI: Tool to automatically share CSS styles

from sqlalchemy import create_engine, Column, Integer, String, Boolean  # SQLALCHEMY: Database tools
from sqlalchemy.ext.declarative import declarative_base  # SQLALCHEMY: Table tracker
from sqlalchemy.orm import sessionmaker, Session  # SQLALCHEMY: Database pipeline tools

# ==============================================================================
# 2. STARTING THE APP ENGINE & STYLE SHARING
# ==============================================================================
app = FastAPI()  # Turn on the FastAPI engine (ONLY ONCE!)

# Tell FastAPI to look inside your CURRENT folder (.) for your Profile.html file
templates = Jinja2Templates(directory=".")

# Tell FastAPI: "If the browser asks for Profile.css from this folder, just hand it over!"
app.mount("/static", StaticFiles(directory="."), name="static")


# ==============================================================================
# 3. THE DATABASE CONNECTION (Setting up the pipe to PostgreSQL)
# ==============================================================================
# THE KEY: Change "password" to match your actual local PostgreSQL password!
DATABASE_URL = "postgresql://postgres:password@localhost:5432/foodbank_db"

# Create the engine manager that talks to the database
engine = create_engine(DATABASE_URL)

# Setup our temporary database workspace creator
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base template for our blueprint class
Base = declarative_base()

# Safety function to open a database connection per page load, and close it when done
def get_db():
    db = SessionLocal()  # Open the connection workspace
    try:
        yield db  # Hand it to the page function below
    finally:
        db.close()  # Close it up when the page finishes loading to save memory



#ALL BELOW CODE TO BE EDITED WHEN DATABASE IS READY! 

#Fake database for testing
fake_database = {
    1: {
        "full_name": "Sam",
        "email": "Sam@email.com",
        "phone_number": "+31 6 12345678",
        "age": 21,
        "role": "Volunteer",
        "is_manager": False
    }
}
# ==============================================================================
# 4. THE PROFILE WEB PAGE (Pulls from our fake database)
# ==============================================================================
@app.get("/profile.html", response_class=HTMLResponse)  
def view_profile_page(request: Request): 
    
    # 1. Pretend User ID #1 is the one who logged in
    current_logged_in_id = 1
    
    # 2. Grab the fake user data out of our python dictionary above
    single_user = fake_database.get(current_logged_in_id)
    
    # 3. Open 'Profile.html' and send that fake user data to the screen
    return templates.TemplateResponse(
        request=request,
        name="Profile.html",  
        context={"user": single_user}  # This passes the data to your HTML file
    )


#To view pages and insert data
@app.get("/scheduler.html", response_class=HTMLResponse)  
def view_scheduler_page(request: Request):
    # This opens your Scheduler.html file when someone clicks the link
    return templates.TemplateResponse(request=request, name="Scheduler.html")


#To view pages and insert data
@app.get("/contact.html", response_class=HTMLResponse)  
def view_contact_page(request: Request):
    # This opens your Contact.html file
    return templates.TemplateResponse(request=request, name="Contact.html")

#To view pages and insert data
@app.get("/notifications.html", response_class=HTMLResponse)  
def view_notifications_page(request: Request):
    # This opens your Notifications.html file
    return templates.TemplateResponse(request=request, name="Notifications.html")

