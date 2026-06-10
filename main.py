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

from sqlalchemy import text
from sqlalchemy.engine import URL


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

DATABASE_URL = URL.create(
    "postgresql+psycopg2",
    username="ocheabah",
    password="Yolor787@",  # plain (unescaped) text
    host="oche-server.postgres.database.azure.com",
    port=5432,
    database="foodbank",
)

# Create the engine manager that talks to the database}
engine = create_engine(DATABASE_URL)

try:
    # 1. Connect to the database and execute a dummy query
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("✅ SUCCESS: Successfully connected to the Azure PostgreSQL database!")

except Exception as e:
    print("❌ CONNECTION FAILED! See the error details below:")
    print(e)


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
# 1. Query JUST the row matching the logged-in ID
#user = db.query(UserProfile).filter(UserProfile.user_id == current_logged_in_id).first()

# 2. Build the nested dictionary structure for just this one user
#profile_data = {}

#if user:  # Safety check to make sure the user actually exists in Postgres
#    profile_data[current_logged_in_id] = {
#        "user_id": user.user_id,
#        "full_name": user.full_name,
#        "email": user.email,
#        "password": user.password_hash, 
#        "phone_number": user.phone_number,
#        "role": user.role,
#        "is_manager": user.is_manager,
#        "age": user.age
#    }




#TESTING
profile_data = {
    1: {
        "user_id": 1,
        "full_name": "Sam",
        "email": "Sam@email.com",
        "password": "password",
        "phone_number": "+31 6 12345678",
        "role": "Volunteer",
        "is_manager": False,
        "age": 21,
    },
    2: {
        "user_id": 2,
        "full_name": "Bob",
        "email": "Bob@email.com",
        "password": "password2",
        "phone_number": "+31 6 12345678",
        "role": "Volunteer",
        "is_manager": True,
        "age": 21,
    }
}


#Search database for messages related to user ID Make function
#Get Oche to add "Message Type"
notifications_data = {
    1: {
        "message_type": "You're Great Reminder",
        "message": "This is a message",
        "time": "1 day ago",
    },
    2: {
        "message_type": "Shift Reminder",
        "message": "This is the message of the notification",
        "time": "2 hours ago",
    },
    3: {
        "message_type": "Shift Reminder",
        "message": "This is the message of the notification",
        "time": "2 hours ago",
    },
    4: {
        "message_type": "Shift Reminder",
        "message": "This is the message of the notification",
        "time": "2 hours ago",
    },
    5: {
        "message_type": "Shift Reminder",
        "message": "This is the message of the notification",
        "time": "2 hours ago",
    },
    6: {
        "message_type": "Shift Reminder",
        "message": "This is the message of the notification",
        "time": "2 hours ago",
    },
    7: {
        "message_type": "Shift Reminder",
        "message": "This is the ",
        "time": "2 hours ago",
    },
}
# ==============================================================================
# 4. THE PROFILE WEB PAGE (Pulls from our fake database)
# ==============================================================================
@app.get("/profile.html", response_class=HTMLResponse)  
def view_profile_page(request: Request): 
    
    # 1. Pretend User ID #1 is the one who logged in
    current_logged_in_id = 1
    
    # 2. Grab the fake user data out of our python dictionary above
    single_user = profile_data.get(current_logged_in_id)
    
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


@app.get("/notifications.html", response_class=HTMLResponse)  # 1. FIXED: Removed .html so it matches your navbar link!
def view_notifications_page(request: Request):
    # 2. Pretend User ID #1 is the one who logged in
    current_logged_in_id = 1
    
    # 3. FIXED: Grab user details from the PROFILE database, not the notifications database!
    single_user = profile_data.get(current_logged_in_id)
    
    # 4. Open 'Notifications.html' and pass both variables to the screen safely
    return templates.TemplateResponse(
        request=request,
        name="Notifications.html",
        context={
            "user": single_user, 
            "notifications_data": notifications_data  
        }
    )

#Login Page
@app.get("/login.html", response_class=HTMLResponse)  
def view_login_page(request: Request):
    # This opens your Login.html file
    return templates.TemplateResponse(
        request=request,
        name="Login.html",
        context={
            "profile_data": profile_data
        }
    )


#To view pages and insert data
@app.get("/inventory.html", response_class=HTMLResponse)  
def view_inventory_page(request: Request):
    # This opens your Inventory.html file
    return templates.TemplateResponse(request=request, name="Inventory.html")