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

templates = Jinja2Templates(directory=".")
app.mount("/static", StaticFiles(directory="."), name="static")

# THE DATABASE CONNECTION (Setting up the pipe to PostgreSQL)
DATABASE_URL = URL.create(
    "postgresql+psycopg2",
    username="ocheabah",
    password="Yolor787@",  
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
    __tablename__ = "users"  

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

#New donation tabele
class NewDonationPayload(BaseModel):
    food_name: str
    food_type: str
    quantity: int
    expiry_date: str

class UpdateQuantitiesPayload(BaseModel):
    items: list[dict] 

#For urgent messages
class UrgentMessagePayload(BaseModel):
    message_html: str

class DayStaffResponse(BaseModel):
    working: list[dict]  
    requests: list[dict] 

class SingleShiftChange(BaseModel):
    name: str
    date: str  # Format: YYYY-MM-DD
    action: str  # 'accept', 'reject', or 'remove'

class BatchShiftPayload(BaseModel):
    changes: list[SingleShiftChange]

# Safety function to open a database connection per page load, and close it when done
def get_db():
    db = SessionLocal()  # Open the connection workspace
    try:
        yield db  # Hand it to the page function below
    finally:
        db.close()  # Close it up when the page finishes loading to save memory


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

# Almost Finished. Need more data in database?
@app.get("/notifications.html", response_class=HTMLResponse)  
def view_notifications_page(request: Request, db: Session = Depends(get_db)):
    global current_logged_in_id
    
    active_id = current_logged_in_id if current_logged_in_id is not None else 1
        
    user = db.query(UserProfile).filter(UserProfile.user_id == active_id).first()
    is_manager = user.is_manager if user else False

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

    return templates.TemplateResponse(
        request=request,
        name="Login.html",
        context={
            "profile_data": profile_data
        }
    )


#SCHEDULOR PAGE -------------------------------------------------------------------------------------------------
@app.get("/scheduler.html", response_class=HTMLResponse)  
def view_scheduler_page(request: Request, db: Session = Depends(get_db)):
    global current_logged_in_id
    active_id = current_logged_in_id if current_logged_in_id is not None else 1

    user = db.query(UserProfile).filter(UserProfile.user_id == active_id).first()
    is_manager = user.is_manager if user else False
    
    # FETCH CURRENT SELECTION: Grab the saved number of days, defaulting to 0 if not found
    days_worked_saved = user.days_worked_in_month if user and user.days_worked_in_month is not None else 0

    all_shifts = db.query(Shift).all()

    team_capacity_map = {}
    user_assigned_shifts = {}

    for shift in all_shifts:
        date_str = str(shift.shift_date).strip()
        
        # Only increment the calendar capacity counter if the shift is officially approved!
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
            "is_manager": is_manager,
            "days_worked_saved": days_worked_saved 
        }
    )

class ScheduleSubmitPayload(BaseModel):
    user_id: int
    days_wanted: int
    available_days: list[str]  # Array containing ['2026-06-12', '2026-06-15']

@app.post("/submit-schedule")
def save_user_schedule(payload: ScheduleSubmitPayload, db: Session = Depends(get_db)):
    try:
        # 1. UPDATE USER PREFERENCE: Save the value directly to the users table row
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == payload.user_id).first()
        if user_profile:
            user_profile.days_worked_in_month = payload.days_wanted

        # 2. Clear out previous placeholder/scheduled shifts for this user safely
        db.query(Shift).filter(
            Shift.user_id == payload.user_id, 
            Shift.status != 'approved'
        ).delete()

        # 3. Rebuild fresh selections if any exist. Empty collections safely skip this block.
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
        return {"status": "success", "message": "Schedule and preferences updated successfully."}
        
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

#START MANAGER SCHEDULOR PAGE ---------------------------------------------------------------------------------------
@app.post("/api/shifts/batch-update")
def batch_update_shifts(payload: BatchShiftPayload, db: Session = Depends(get_db)):
    try:
        from sqlalchemy import extract

        for change in payload.changes:
            # 1. Map the text string 'name' to its unique numeric database 'user_id'
            user = db.query(UserProfile).filter(UserProfile.full_name == change.name).first()
            if not user:
                print(f"⚠️ Warning: User named '{change.name}' could not be matched in database.")
                continue  # Safe skip to prevent query errors
            
            # Parse the incoming date string into a structured Python date object
            parsed_date = datetime.strptime(change.date, "%Y-%m-%d").date()

            # 2. Locate the matching record in your shifts table
            shift_record = db.query(Shift).filter(
                Shift.user_id == user.user_id,
                Shift.shift_date == parsed_date
            ).first()

            # 3. Apply the dynamic transactional rules requested
            if change.action == "accept":
                if shift_record:
                    # BACKEND SAFETY CAP GUARD:
                    # Calculate how many shifts this specific user has ALREADY had approved for this specific calendar month
                    approved_this_month = db.query(Shift).filter(
                        Shift.user_id == user.user_id,
                        Shift.status == "approved",
                        extract('year', Shift.shift_date) == parsed_date.year,
                        extract('month', Shift.shift_date) == parsed_date.month
                    ).count()

                    # Fallback cleanly to 0 if days_worked_in_month is null
                    user_max_allowed = user.days_worked_in_month if user.days_worked_in_month is not None else 0

                    # Block approval if it exceeds their chosen cap limit
                    if approved_this_month >= user_max_allowed:
                        print(f"❌ Safety Cap Triggered: Refusing to over-approve {user.full_name}.")
                        continue

                    shift_record.status = "approved"
            
            elif change.action == "reject":
                if shift_record:
                    db.delete(shift_record)
            
            elif change.action == "remove":
                if shift_record:
                    # Revert status from 'approved' back to a normal 'scheduled' worker request
                    shift_record.status = "scheduled"

        # Commit all modified entries to Azure PostgreSQL simultaneously
        db.commit()
        return {"status": "success", "message": "All staging area changes saved successfully."}

    except Exception as e:
        db.rollback()
        print(f"❌ Batch Update Database error details: {e}")
        return {"status": "error", "message": str(e)}
    

@app.get("/api/shifts/by-date/{date_str}", response_model=DayStaffResponse)
def get_shifts_by_date(date_str: str, db: Session = Depends(get_db)):
    try:
        from sqlalchemy import extract

        # Parse incoming date parameter string (YYYY-MM-DD) safely
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Pull all database records recorded for this day
        day_shifts = db.query(Shift).filter(Shift.shift_date == parsed_date).all()
        
        working_list = []
        requests_list = []
        
        for s in day_shifts:
            # Query the user profile to fetch the volunteer's real full name and role mapping
            user_profile = db.query(UserProfile).filter(UserProfile.user_id == s.user_id).first()
            if not user_profile:
                continue

            full_name = user_profile.full_name
            user_role = user_profile.role if user_profile.role else "Volunteer"
            user_preference = user_profile.days_worked_in_month if user_profile.days_worked_in_month is not None else 0
            
            # Look up total approved slots across this user's entire month
            total_approved_this_month = db.query(Shift).filter(
                Shift.user_id == s.user_id,
                Shift.status == "approved",
                extract('year', Shift.shift_date) == parsed_date.year,
                extract('month', Shift.shift_date) == parsed_date.month
            ).count()

            # Map the precise variables your JavaScript frontend expects
            shift_info = {
                "name": full_name,
                "role": user_role,
                "days_wanted": user_preference,
                "total_approved_this_month": total_approved_this_month
            }
            
            # Clear segregation to prevent duplicate rendering bugs
            if s.status == "approved":
                working_list.append(shift_info)
            elif s.status == "scheduled":
                requests_list.append(shift_info)
                
        return {"working": working_list, "requests": requests_list}
        
    except Exception as e:
        print(f"Error fetching day breakdown details: {e}")
        return {"working": [], "requests": []}


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
                created_at=text(f"'{current_time_str}'::timestamp")
            )
            db.add(new_notification)
            
        db.commit()
        return {"status": "success", "message": f"Broadcasted message to {len(all_users)} users."}
        
    except Exception as e:
        db.rollback()
        print(f"Error broadcasting message: {e}")
        return {"status": "error", "message": str(e)}
    
@app.get("/Managerscheduler.html", response_class=HTMLResponse)  
def view_manager_scheduler_page(request: Request, db: Session = Depends(get_db)):
    global current_logged_in_id
    active_id = current_logged_in_id if current_logged_in_id is not None else 1
    
    user = db.query(UserProfile).filter(UserProfile.user_id == active_id).first()
    is_manager = user.is_manager if user else False

    # Get today's local date to look at current or future shift allocations
    today_date = datetime.now().date()

    # 1. FETCH ALL SHIFTS FOR TODAY OR THE FUTURE (Both pending requests and finalized ones)
    active_shifts = db.query(Shift).filter(
        Shift.status.in_(["scheduled", "approved"]),
        Shift.shift_date >= today_date
    ).order_by(Shift.shift_date.asc()).all()

    # 2. AGGREGATE DATES BY USER ID
    requests_map = {}
    
    for shift in active_shifts:
        u_id = shift.user_id
        date_str = shift.shift_date.strftime("%d/%m/%Y") if shift.shift_date else ""
        
        # If this user isn't in our tracking map yet, initialize their profile statistics
        if u_id not in requests_map:
            volunteer = db.query(UserProfile).filter(UserProfile.user_id == u_id).first()
            v_name = volunteer.full_name if volunteer else f"User #{u_id}"
            v_preference = volunteer.days_worked_in_month if volunteer and volunteer.days_worked_in_month else 0
            
            requests_map[u_id] = {
                "user_obj": volunteer, # Keep track of the DB object to update it later
                "volunteer_name": v_name,
                "available_dates": [],  # Holds pending ('scheduled') dates
                "approved_dates": [],   # Holds locked-in ('approved') dates
                "days_wanted": v_preference
            }
            
        # Distribute dates to their respective lists based on database status string
        if date_str:
            if shift.status == "scheduled":
                if date_str not in requests_map[u_id]["available_dates"]:
                    requests_map[u_id]["available_dates"].append(date_str)
            elif shift.status == "approved":
                if date_str not in requests_map[u_id]["approved_dates"]:
                    requests_map[u_id]["approved_dates"].append(date_str)

    # 3. CRITICAL AUTOMATIC ADJUSTMENT: Run through users and fix preferences based on future options
    database_changed = False
    for u_id, data in requests_map.items():
        total_future_options = len(data["available_dates"]) + len(data["approved_dates"])
        
        # If days_wanted is higher than their remaining active calendar dates, force it down
        if data["days_wanted"] > total_future_options:
            print(f"⏰ Time-Passed Adjustment: {data['volunteer_name']} wanted {data['days_wanted']} days, "
                  f"but only has {total_future_options} shifts remaining from today onward. Adjusting database.")
            
            data["days_wanted"] = total_future_options
            if data["user_obj"]:
                data["user_obj"].days_worked_in_month = total_future_options
                database_changed = True

    if database_changed:
        db.commit()

    # Flatten collections mapping cleanly into an iterable list for Jinja
    shift_requests_list = list(requests_map.values())

    # 4. PASS THE DATA TO THE TEMPLATE
    return templates.TemplateResponse(
        request=request, 
        name="ManagerScheduler.html", 
        context={
            "is_manager": is_manager,
            "shift_requests": shift_requests_list
        }
    )

@app.get("/api/shifts/approved-counts")
def get_approved_counts(year: int, month: int, db: Session = Depends(get_db)):
    try:
        # Query approved shifts for the specific year and month
        # EXTRACT components out of the Date field for performance stability
        from sqlalchemy import extract
        
        results = db.query(Shift.shift_date, text("count(*)"))\
            .filter(Shift.status == "approved")\
            .filter(extract('year', Shift.shift_date) == year)\
            .filter(extract('month', Shift.shift_date) == month)\
            .group_by(Shift.shift_date)\
            .all()
            
        # Format the response object into a clean dictionary mapping: {"YYYY-MM-DD": count}
        counts_map = {}
        for shift_date, count in results:
            if shift_date:
                date_str = shift_date.strftime("%Y-%m-%d")
                counts_map[date_str] = count
                
        return counts_map
        
    except Exception as e:
        print(f"❌ Error compiling approved capacities: {e}")
        return {}

#END Maneger page-----------------------------------------------------------------------------------------

#john@example.com
#hashedpassword1

#Sarah
#hashedpassword2

#Mike
#hashedpassword3

#Emma
#hashedpassword4

#David
#hashedpassword5

