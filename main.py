#Bug in navigation bar for inventory page
#How many days do you want to work not working as intended
#Message saying "you are already assigned days is wrong"
#You are already assigned days needs to ignore previous days
#Cannot unselect days in scheduler page
#No difference betwwen assigned days and days they want to work
#Hovering over profile picture in navbar does makes whole page shift down
#Add a logout button? Just a button that links back to login page

#Notifications sorted backwards

#Manager Schedulor page-----------
#Accepting or refusing a shift does not update the staff requests

import os  

from fastapi import FastAPI, Request, Depends  # FASTAPI: Web server and routing tools
from fastapi.responses import HTMLResponse  # FASTAPI: Tool to send back HTML web pages
from fastapi.templating import Jinja2Templates  # FASTAPI: Bridge to drop text into HTML
from fastapi.staticfiles import StaticFiles  # FASTAPI: Tool to automatically share CSS styles

from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date  # SQLALCHEMY: Database tools
from sqlalchemy.ext.declarative import declarative_base  # SQLALCHEMY: Table tracker
from sqlalchemy.orm import sessionmaker, Session  # SQLALCHEMY: Database pipeline tools
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy import DateTime
from datetime import datetime  

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

# Database table blueprint for user profile
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
    days_worked_in_month = Column(Integer)

#Database table blueprint for notifications
class Notification(Base):
    __tablename__ = "messages"  

    message_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    content = Column(String)
    created_at = Column(String)

#Database table blueprint for shifts
class Shift(Base):
    __tablename__ = "shifts"

    shift_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    shift_date = Column(Date)  # <-- CHANGED FROM String TO Date TO MATCH POSTGRES
    start_time = Column(String)
    end_time = Column(String)
    status = Column(String)

#Database table blueprint for inventory items
class InventoryItem(Base):
    __tablename__ = "inventory"

    inventory_id = Column(Integer, primary_key=True)
    food_name = Column(String)
    food_type = Column(String)
    quantity = Column(Integer)
    expiry_date = Column(Date)


class NewDonationPayload(BaseModel):
    food_name: str
    food_type: str
    quantity: int
    expiry_date: str

class UpdateQuantitiesPayload(BaseModel):
    items: list[dict] # Expected format: [{"id": 1, "quantity": 12}, ...]

#For urgent messages
class UrgentMessagePayload(BaseModel):
    message_html: str


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

    # Add lookups for layout-level role verification
    is_manager = user.is_manager if user else False

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
        context={"user": single_user, "is_manager": is_manager}  
    )

#To view pages and insert data
@app.get("/contact.html", response_class=HTMLResponse)  
def view_contact_page(request: Request, db: Session = Depends(get_db)):
    global current_logged_in_id
    active_id = current_logged_in_id if current_logged_in_id is not None else 1
    
    user = db.query(UserProfile).filter(UserProfile.user_id == active_id).first()
    is_manager = user.is_manager if user else False

    # This opens your Contact.html file
    return templates.TemplateResponse(
        request=request, 
        name="Contact.html", 
        context={"is_manager": is_manager}
    )

#Almost Finished. Need more data in database?
# Almost Finished. Need more data in database?
@app.get("/notifications.html", response_class=HTMLResponse)  
def view_notifications_page(request: Request, db: Session = Depends(get_db)):
    global current_logged_in_id
    
    active_id = current_logged_in_id if current_logged_in_id is not None else 1
        
    user = db.query(UserProfile).filter(UserProfile.user_id == active_id).first()
    is_manager = user.is_manager if user else False

    # FIX: Added .order_by(Notification.created_at.desc()) to pull newest first
    db_notifications = db.query(Notification)\
                         .filter(Notification.user_id == active_id)\
                         .order_by(Notification.created_at.desc())\
                         .all()
    
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
            "notifications_data": formatted_notifications,
            "is_manager": is_manager  
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
            "age": user.age,
            "working_days": user.days_worked_in_month
        }
    # 3. Pass the complete dictionary containing everyone over to Login.html
    return templates.TemplateResponse(
        request=request,
        name="Login.html",
        context={
            "profile_data": profile_data
        }
    )


#SCHEDULOR PAGE -------------------------------------------------------------------------------------------------
#The page successfully shows days people are assigned, but people can assign themselves
#A bug regarding days assigned as well?
@app.get("/scheduler.html", response_class=HTMLResponse)  
def view_scheduler_page(request: Request, db: Session = Depends(get_db)):
    global current_logged_in_id
    active_id = current_logged_in_id if current_logged_in_id is not None else 1

    user = db.query(UserProfile).filter(UserProfile.user_id == active_id).first()
    is_manager = user.is_manager if user else False

    all_shifts = db.query(Shift).all()

    team_capacity_map = {}
    user_assigned_shifts = {}

    for shift in all_shifts:
        date_str = str(shift.shift_date).strip()
        
        # FIX: Only increment the calendar capacity counter if the shift is officially approved!
        if shift.status == 'approved':
            team_capacity_map[date_str] = team_capacity_map.get(date_str, 0) + 1
        
        if shift.user_id == active_id:
            user_assigned_shifts[date_str] = shift.status.lower() if shift.status else "scheduled"

    return templates.TemplateResponse(
        request=request, 
        name="Scheduler.html",
        context={
            "team_capacities": team_capacity_map,
            "user_shifts": user_assigned_shifts,  
            "active_user_id": active_id,
            "is_manager": is_manager
        }
    )

# 3. ADD THE DATA SUBMIT ACTION ENDPOINT
class ScheduleSubmitPayload(BaseModel):
    user_id: int
    days_wanted: int
    available_days: list[str]  # Array containing ['2026-06-12', '2026-06-15']

@app.post("/submit-schedule")
def save_user_schedule(payload: ScheduleSubmitPayload, db: Session = Depends(get_db)):
    try:
        # Clear out previous placeholder/scheduled shifts for this user safely
        db.query(Shift).filter(
            Shift.user_id == payload.user_id, 
            Shift.status != 'approved'
        ).delete()

        # Rebuild fresh selections if any exist. Empty collections safely skip this block.
        for day_string in payload.available_days:
            parsed_date = datetime.strptime(day_string, "%Y-%m-%d").date()

            new_shift = Shift(
                user_id=payload.user_id,
                shift_date=parsed_date,  
                start_time="09:00",      
                end_time="17:00",        
                status="scheduled"       
            )
            db.add(new_shift)
            
        db.commit()
        return {"status": "success", "message": "Schedule updated successfully."}
        
    except Exception as e:
        db.rollback()
        print(f"Database error details: {e}")
        return {"status": "error", "message": str(e)}
#End SCHEDULOR PAGE -------------------------------------------------------------------------------------------------

#INVENTORY PAGE -------------------------------------------------------------------------------------------------
@app.get("/inventory.html", response_class=HTMLResponse)  
def view_inventory_page(request: Request, db: Session = Depends(get_db)):
    global current_logged_in_id
    active_id = current_logged_in_id if current_logged_in_id is not None else 1
    
    user = db.query(UserProfile).filter(UserProfile.user_id == active_id).first()
    is_manager = user.is_manager if user else False

    # Retrieve all stock entries from Azure, sorted closest to expiry
    db_items = db.query(InventoryItem).order_by(InventoryItem.expiry_date.asc()).all()

    today = datetime.now().date()
    formatted_inventory = []

    for item in db_items:
        # Calculate remaining lifespan metric real-time
        days_left = (item.expiry_date - today).days if item.expiry_date else 0
        
        formatted_inventory.append({
            "id": item.inventory_id,
            "productName": item.food_name,
            "category": item.food_type.lower(),
            "quantity": item.quantity,
            "expiryDate": str(item.expiry_date),
            "daysLeft": days_left
        })

    return templates.TemplateResponse(
        request=request, 
        name="Inventory.html",
        context={"inventory_data": formatted_inventory, "is_manager": is_manager}
    )


# 4. API ENDPOINT TO ADD NEW ITEM
@app.post("/api/inventory/add")
def add_new_donation(payload: NewDonationPayload, db: Session = Depends(get_db)):
    try:
        parsed_date = datetime.strptime(payload.expiry_date, "%Y-%m-%d").date()
        new_item = InventoryItem(
            food_name=payload.food_name,
            food_type=payload.food_type,
            quantity=payload.quantity,
            expiry_date=parsed_date
        )
        db.add(new_item)
        db.commit()
        return {"status": "success", "message": "Item added successfully."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}


# 5. API ENDPOINT TO BULK UPDATE QUANTITIES
@app.post("/api/inventory/update-quantities")
def update_inventory_quantities(payload: UpdateQuantitiesPayload, db: Session = Depends(get_db)):
    try:
        for update in payload.items:
            item = db.query(InventoryItem).filter(InventoryItem.inventory_id == update["id"]).first()
            if item:
                if update["quantity"] <= 0:
                    db.delete(item) # Automatically purge exhausted stock lines
                else:
                    item.quantity = update["quantity"]
        db.commit()
        return {"status": "success", "message": "Inventory records synchronized."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    
#END INVENTORY PAGE -------------------------------------------------------------------------------------------------


#START MANAGER SCHEDULOR PAGE -------------------------------------------------------------------------------------------------
@app.get("/Managerscheduler.html", response_class=HTMLResponse)  
def view_manager_scheduler_page(request: Request, db: Session = Depends(get_db)):
    global current_logged_in_id
    active_id = current_logged_in_id if current_logged_in_id is not None else 1
    
    user = db.query(UserProfile).filter(UserProfile.user_id == active_id).first()
    
    # This opens your ManagerScheduler.html file
    return templates.TemplateResponse(
        request=request, 
        name="ManagerScheduler.html", 
        context={"is_manager": True}
    )

@app.post("/api/urgent-message")
def send_broadcast_message(payload: UrgentMessagePayload, db: Session = Depends(get_db)):
    try:
        # Fetch every user ID from the system
        all_users = db.query(UserProfile.user_id).all()
        
        if not all_users:
            return {"status": "error", "message": "No users found in database."}

        # Generate the current time as a clean string format
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Loop through and create a notification row for every individual user
        for user_row in all_users:
            new_notification = Notification(
                user_id=user_row.user_id,
                content=payload.message_html,
                # Use text() to force PostgreSQL to accept the string as a timestamp
                created_at=text(f"'{current_time_str}'::timestamp")
            )
            db.add(new_notification)
            
        db.commit()
        return {"status": "success", "message": f"Broadcasted message to {len(all_users)} users."}
        
    except Exception as e:
        db.rollback()
        print(f"Error broadcasting message: {e}")
        return {"status": "error", "message": str(e)}
    

#END Maneger page-----------------------------------------------------------------------------------------

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

#Sam to do
#Need to test with Oche the messaging works properly and for him to add custom messages for the presentation
#Check schedulor page is sending data properly
#John @example not working???