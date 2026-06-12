#Bug in navigation bar for inventory page

import os  

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


# STARTING THE APP ENGINE & STYLE SHARING
#-------------------------------------------------------------------------------------------------------
app = FastAPI()  # Turn on the FastAPI engine

# Tell FastAPI to look inside your CURRENT folder 
templates = Jinja2Templates(directory=".")
app.mount("/static", StaticFiles(directory="."), name="static")

# THE DATABASE CONNECTION (Setting up the pipe to PostgreSQL)
DATABASE_URL = URL.create(
    "postgresql+psycopg2",
    username="ocheabah",
    password="Yolor787@",  # plain (unescaped) text
    host="oche-server.postgres.database.azure.com",
    port=5432,
    database="foodbank",
)

# Create the engine manager that talks to the database
engine = create_engine(DATABASE_URL)
#Testing connection to database
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

# Base template for our blueprint class
Base = declarative_base()
#--------------------------------------------------------------------------------------------------------------

# Variable for tracking who's logged in using user_id numbers from the database
current_logged_in_id = None

#This code saves which user is logged in
class LoginPayload(BaseModel):
    user_id: int

@app.post("/set-active-user")
def set_active_user(payload: LoginPayload):
    global current_logged_in_id
    current_logged_in_id = payload.user_id  
    print(f"Python received the user ID number: {current_logged_in_id}")
    return {"status": "received"}

#Database table blueprint for user profile
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

#Database table blueprint for notifications
class Notification(Base):
    __tablename__ = "messages"  

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


# ALL BELOW ARE CODE PER PAGE

#Finished
@app.get("/profile.html", response_class=HTMLResponse)  
def view_profile_page(request: Request, db: Session = Depends(get_db)): 
    
    global current_logged_in_id
        
    if current_logged_in_id is None:
        current_logged_in_id = 1
    
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

@app.get("/scheduler.html", response_class=HTMLResponse)  
def view_scheduler_page(request: Request):
    # This opens your Scheduler.html file when someone clicks the link
    return templates.TemplateResponse(request=request, name="Scheduler.html")


#To view pages and insert data
@app.get("/contact.html", response_class=HTMLResponse)  
def view_contact_page(request: Request):
    # This opens your Contact.html file
    return templates.TemplateResponse(request=request, name="Contact.html")

#Almost Finished. Need more data in database?
@app.get("/notifications.html", response_class=HTMLResponse)  
def view_notifications_page(request: Request, db: Session = Depends(get_db)):
    global current_logged_in_id
    
    active_id = current_logged_in_id if current_logged_in_id is not None else 1
        
    db_notifications = db.query(Notification).filter(Notification.user_id == active_id).all()
    
    formatted_notifications = {}
    for n in db_notifications:
        msg_content = n.content.lower() if n.content else ""
        
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

#Finished
@app.get("/login.html", response_class=HTMLResponse)  
def view_login_page(request: Request, db: Session = Depends(get_db)):
    
    db_users = db.query(UserProfile).all()

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

#John
#hashedpassword2

#Mike
#hashedpassword3

#Emma
#hashedpassword4

#David
#hashedpassword5