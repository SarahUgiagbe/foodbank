#JUST FOR SAVING CODE FOR WHEN DATABASE IS READY! SAM!! 



#Replace when database is ready
# ==============================================================================
# 4. THE USER BLUEPRINT (Matching your table design exactly)
# ==============================================================================
class User(Base):
    __tablename__ = "users"  # The actual table name inside PostgreSQL

    user_id = Column(Integer, primary_key=True, index=True)  # Unique row number
    full_name = Column(String, nullable=False)               # User's Name
    email = Column(String, unique=True, index=True, nullable=False) # User's Email
    age = Column(Integer, nullable=True)                    # User's Age 
    password_hash = Column(String, nullable=False)           # Scrambled password text
    phone_number = Column(String, nullable=True)             # Phone number text
    role = Column(String, default="Volunteer")               # Job role text
    is_manager = Column(Boolean, default=False)             # True or False switch

# FIXED: Removed the '#' hashtag so Python WILL build this table inside PostgreSQL on boot!
#Base.metadata.create_all(bind=engine)

# ==============================================================================
# 5. THE PROFILE WEB PAGE (For one specific user)
# ==============================================================================
@app.get("/profile", response_class=HTMLResponse)  
def view_profile_page(request: Request, db: Session = Depends(get_db)):
    
    # 1. HARDCODED LOGGED-IN USER ID FOR NOW
    # (Since we haven't built the login box yet, let's pretend User ID #1 logged in)
    current_logged_in_id = 1
    
    # 2. Go to PostgreSQL and find ONLY the user whose user_id matches our logged-in ID
    single_user = db.query(User).filter(User.user_id == current_logged_in_id).first()
    
    # 3. Open 'Profile.html' and pass that ONE user object to the page
    return templates.TemplateResponse(
        request=request,
        name="Profile.html",  
        context={"user": single_user}  # Passing just ONE user item instead of a list
    )


#To view pages and insert data
@app.get("/notifications.html", response_class=HTMLResponse)  
def view_notifications_page(request: Request):
    # This opens your Notifications.html file
    # 1. Pretend User ID #1 is the one who logged in
    current_logged_in_id = 1
    
    # 2. Grab the fake user data out of our python dictionary above
    single_user = fake_profile_database.get(current_logged_in_id)
    
    # 3. Open 'Notifications.html' and send that fake user data to the screen
    return templates.TemplateResponse( #Using fake database again for testing data
        request=request,
        name="Notifications.html",  
        context={"user": single_user}  # This passes the data to your HTML file
    )
    #return templates.TemplateResponse(request=request, name="Notifications.html")


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

@app.get("/notifications.html", response_class=HTMLResponse)  # 1. FIXED: Removed .html so it matches your navbar link!
def view_notifications_page(request: Request):
    # 2. Pretend User ID #1 is the one who logged in
    current_logged_in_id = 1
    
    # 4. Open 'Notifications.html' and pass both variables to the screen safely
    return templates.TemplateResponse(
        request=request,
        name="Notifications.html",
        context={
            "notifications_data": notifications_data  
        }
    )


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
}


#To view pages and insert data
@app.get("/inventory.html", response_class=HTMLResponse)  
def view_inventory_page(request: Request):
    # This opens your Inventory.html file
    return templates.TemplateResponse(request=request, name="Inventory.html")


#Before manager page -----------------------------------------------
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


#SCHEDULOR PAGE -------------------------------------------------------------------------------------------------
#The page successfully shows days people are assigned, but people can assign themselves
#A bug regarding days assigned as well?
@app.get("/scheduler.html", response_class=HTMLResponse)  
def view_scheduler_page(request: Request, db: Session = Depends(get_db)):
    global current_logged_in_id
    active_id = current_logged_in_id if current_logged_in_id is not None else 1

    # Fetch ALL shifts across the team to calculate daily capacities
    all_shifts = db.query(Shift).all()

    # Compile team shifts together to see how full a single day is
    # Formatted as: {"2026-06-10": 3} (meaning 3 people signed up on June 10th)
    team_capacity_map = {}
    
    # Track exactly which days this specific logged-in individual is working
    user_assigned_days = []

    for shift in all_shifts:
        # Standardize date format strings to match frontend (YYYY-MM-DD)
        date_str = str(shift.shift_date).strip()
        
        # Build global count tracking map
        team_capacity_map[date_str] = team_capacity_map.get(date_str, 0) + 1
        
        # Isolate if this specific block row belongs to our logged in user
        if shift.user_id == active_id:
            user_assigned_days.append(date_str)

    return templates.TemplateResponse(
        request=request, 
        name="Scheduler.html",
        context={
            "team_capacities": team_capacity_map,
            "user_shifts": user_assigned_days,
            "active_user_id": active_id
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
        # Clear out previous placeholder shifts for this specific user
        db.query(Shift).filter(
            Shift.user_id == payload.user_id, 
            Shift.status != 'approved'
        ).delete()

        # Insert new rows into the shifts database
        for day_string in payload.available_days:
            # Convert incoming text string "YYYY-MM-DD" into a real Python date object
            parsed_date = datetime.strptime(day_string, "%Y-%m-%d").date()

            new_shift = Shift(
                user_id=payload.user_id,
                shift_date=parsed_date,  # <-- Pushing a real date object stops the crash!
                start_time="09:00",      
                end_time="17:00",        
                status="scheduled"       
            )
            db.add(new_shift)
            
        db.commit()
        return {"status": "success", "message": "Schedule stored in PostgreSQL cloud storage."}
    except Exception as e:
        db.rollback()
        print(f"Database error details: {e}")
        return {"status": "error", "message": str(e)}
#End SCHEDULOR PAGE -------------------------------------------------------------------------------------------------

#INVENTORY PAGE -------------------------------------------------------------------------------------------------
@app.get("/inventory.html", response_class=HTMLResponse)  
def view_inventory_page(request: Request, db: Session = Depends(get_db)):
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
        context={"inventory_data": formatted_inventory}
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
@app.get("/ManagerScheduler.html", response_class=HTMLResponse)  
def view_manager_scheduler_page(request: Request):
    # This opens your ManagerScheduler.html file
    return templates.TemplateResponse(request=request, name="ManagerScheduler.html")


@app.get("/scheduler.html", response_class=HTMLResponse)  
def view_scheduler_page(request: Request, db: Session = Depends(get_db)):
    global current_logged_in_id
    active_id = current_logged_in_id if current_logged_in_id is not None else 1

    user = db.query(UserProfile).filter(UserProfile.user_id == active_id).first()
    is_manager = user.is_manager if user else False

    # Fetch ALL shifts across the team to calculate daily capacities
    all_shifts = db.query(Shift).all()

    # Compile team shifts together to see how full a single day is
    # Formatted as: {"2026-06-10": 3} (meaning 3 people signed up on June 10th)
    team_capacity_map = {}
    
    # Track exactly which days this specific logged-in individual is working
    user_assigned_days = []

    for shift in all_shifts:
        # Standardize date format strings to match frontend (YYYY-MM-DD)
        date_str = str(shift.shift_date).strip()
        
        # Build global count tracking map
        team_capacity_map[date_str] = team_capacity_map.get(date_str, 0) + 1
        
        # Isolate if this specific block row belongs to our logged in user
        if shift.user_id == active_id:
            user_assigned_days.append(date_str)

    return templates.TemplateResponse(
        request=request, 
        name="Scheduler.html",
        context={
            "team_capacities": team_capacity_map,
            "user_shifts": user_assigned_days,
            "active_user_id": active_id,
            "is_manager": is_manager
        }
    )

@app.get("/scheduler.html", response_class=HTMLResponse)  
def view_scheduler_page(request: Request, db: Session = Depends(get_db)):
    global current_logged_in_id
    active_id = current_logged_in_id if current_logged_in_id is not None else 1

    user = db.query(UserProfile).filter(UserProfile.user_id == active_id).first()
    is_manager = user.is_manager if user else False

    all_shifts = db.query(Shift).all()

    team_capacity_map = {}
    # CHANGED: Dict to store date mapping to its specific status {"2026-06-10": "scheduled"}
    user_assigned_shifts = {}

    for shift in all_shifts:
        date_str = str(shift.shift_date).strip()
        
        team_capacity_map[date_str] = team_capacity_map.get(date_str, 0) + 1
        
        if shift.user_id == active_id:
            # Save the exact status string from the database (lowercased for safety)
            user_assigned_shifts[date_str] = shift.status.lower() if shift.status else "scheduled"

    return templates.TemplateResponse(
        request=request, 
        name="Scheduler.html",
        context={
            "team_capacities": team_capacity_map,
            "user_shifts": user_assigned_shifts,  # <-- Sending the dict structured data now
            "active_user_id": active_id,
            "is_manager": is_manager
        }
    )