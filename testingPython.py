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
