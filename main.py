#Successfully created unique logins!!!!!!!
#Bug in navigation bar for inventory page

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
from sqlalchemy import DateTime

from pydantic import BaseModel


# 2. STARTING THE APP ENGINE & STYLE SHARING
app = FastAPI()  # Turn on the FastAPI engine

# Tell FastAPI to look inside your CURRENT folder 
templates = Jinja2Templates(directory=".")
app.mount("/static", StaticFiles(directory="."), name="static")

# ==============================================================================
# 3. THE DATABASE CONNECTION (Setting up the pipe to PostgreSQL)
DATABASE_URL = URL.create(
    "postgresql+psycopg2",
    username="ocheabah",
    password="Yolor787@",  # plain (unescaped) text
    host="oche-server.postgres.database.azure.com",
    port=5432,
    database="foodbank",
)

#---------------------------------------------------------------------------
# TESTING CODE BLOCK
# Create the engine manager that talks to the database
engine = create_engine(DATABASE_URL)

try:
    # 1. Connect to the database and execute a dummy query
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("✅ SUCCESS: Successfully connected to the Azure PostgreSQL database!")

except Exception as e:
    print("❌ CONNECTION FAILED! See the error details below:")
    print(e)

# Setup temporary database workspace creator
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#-----------------------------------------------------------------------------

# Base template for our blueprint class
Base = declarative_base()




# The variable where the number will live
current_logged_in_id = None

class LoginPayload(BaseModel):
    user_id: int

@app.post("/set-active-user")
def set_active_user(payload: LoginPayload):
    global current_logged_in_id
    current_logged_in_id = payload.user_id  # Stores the number here
    print(f"Python received the user ID number: {current_logged_in_id}")
    return {"status": "received"}


class UserProfile(Base):
    __tablename__ = "users"  # Tells Python to search your "users" table

    user_id = Column(Integer, primary_key=True)
    full_name = Column(String)
    email = Column(String)
    password_hash = Column(String)
    phone_number = Column(String)
    role = Column(String)
    is_manager = Column(Boolean)
    age = Column(Integer)

class Notification(Base):
    __tablename__ = "messages"  # <-- This fixed the 500 error!

    message_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    content = Column(String)
    created_at = Column(String)


# Safety function to open a database connection per page load, and close it when done
def get_db():
    db = SessionLocal()  # Open the connection workspace
    try:
        yield db  # Hand it to the page function below
    finally:
        db.close()  # Close it up when the page finishes loading to save memory


#Search database for messages related to user ID Make function
#Get Oche to add "Message Type"

#Code per Page
@app.get("/profile.html", response_class=HTMLResponse)  
def view_profile_page(request: Request, db: Session = Depends(get_db)): 
    
    # CHANGE THIS: Tell the function to look at the global variable at the top of your file
    global current_logged_in_id
        
    # If nobody has logged in yet, default to user 1 so the page doesn't crash
    if current_logged_in_id is None:
        current_logged_in_id = 1
    
    # This now dynamically queries whoever logged in!
    user = db.query(UserProfile).filter(UserProfile.user_id == current_logged_in_id).first()

    profile_data = {}
    if user:  
        profile_data[current_logged_in_id] = {
            "user_id": user.user_id,
            "full_name": user.full_name,
            "email": user.email,
            "password": user.password_hash, 
            "phone_number": user.phone_number,
            "role": user.role,
            "is_manager": user.is_manager,
            "age": user.age
        }
    
    single_user = profile_data.get(current_logged_in_id)
    
    return templates.TemplateResponse(
        request=request,
        name="Profile.html",  
        context={"user": single_user}  
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


@app.get("/notifications.html", response_class=HTMLResponse)  
def view_notifications_page(request: Request, db: Session = Depends(get_db)):
    global current_logged_in_id
    
    # Fallback to user 1 if no one is explicitly logged in yet
    active_id = current_logged_in_id if current_logged_in_id is not None else 1
        
    # Query rows from the "messages" table matching this user
    db_notifications = db.query(Notification).filter(Notification.user_id == active_id).all()
    
    # Format for the Jinja frontend template script loop
    formatted_notifications = {}
    for n in db_notifications:
        msg_content = n.content.lower() if n.content else ""
        
        # UI Layout styling logic based on message keywords
        if "urgent" in msg_content or "low on" in msg_content or "alert" in msg_content:
            msg_type = "alert"
        elif "shift" in msg_content or "schedule" in msg_content:
            msg_type = "shift"
        else:
            msg_type = "check"

        formatted_notifications[n.message_id] = {
            "message_type": msg_type.capitalize(),
            "message": n.content if n.content else "No message details.",
            "time": n.created_at if n.created_at else "Recent"
        }
    
    return templates.TemplateResponse(
        request=request,
        name="Notifications.html",
        context={
            "notifications_data": formatted_notifications  
        }
    )

# Login Page
@app.get("/login.html", response_class=HTMLResponse)  
def view_login_page(request: Request, db: Session = Depends(get_db)):
    
    # 1. Fetch ALL user rows from your Azure database table
    db_users = db.query(UserProfile).all()

    # 2. Loop through all database users to build the full profile_data dictionary
    #Puts all profiles in profile page
    profile_data = {}
    for user in db_users:
        profile_data[user.user_id] = {
            "user_id": user.user_id,
            "full_name": user.full_name,
            "email": user.email,
            "password": user.password_hash, 
            "phone_number": user.phone_number,
            "role": user.role,
            "is_manager": user.is_manager,
            "age": user.age
        }
    # 3. Pass the complete dictionary containing everyone over to Login.html
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

#john@example.com
#hashedpassword1

#hashedpassword2
#hashedpassword3
#hashedpassword4
#hashedpassword5