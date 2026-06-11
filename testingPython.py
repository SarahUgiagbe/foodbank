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