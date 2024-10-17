from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas.user_schemas import UserIn,UserCreate,Token
from app.db.database import get_db
from app.utils.auth import get_password_hash,verify_password,create_access_token
from app.crud.user_management import create_user,get_user_by_email,get_all_users,get_user_by_username
from app.core.config import settings    

router = APIRouter()

@router.post("/register",response_model=UserIn)
def register_user(user:UserCreate,db:Session = Depends(get_db)):
    """
        Register a new user in the system.

        Args:
            user (UserCreate): The user information to create a new user.
            db (Session): The database session dependency.

        Raises:
            HTTPException: If the email is already registered or if user creation fails.

        Returns:
            UserIn: The newly created user object.
    """
    existing_user = get_user_by_email(db,user.email)
    if existing_user:
        settings.logger.warning(f"Attempt to register with existing email: {user.email}")
        raise HTTPException(
            status_code=400,
            detail = "Email is Already register"    
        )
    # hash the password 
    hashed_password = get_password_hash(user.password)
    # creating a new user in the database 
    try:
        new_user = create_user(db,user.username,user.email,hashed_password)
    except Exception as e:
        settings.logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create user, please try again later: {e}"
        )
    return new_user


@router.post("/login",response_model=Token)
def login_for_access_token(form_data:OAuth2PasswordRequestForm = Depends(),db:Session = Depends(get_db) ):
    """
        Log in a user and obtain an access token.

        Args:
            form_data (OAuth2PasswordRequestForm): The form containing user login information.
            db (Session): The database session dependency.

        Raises:
            HTTPException: If the email or password is incorrect.

        Returns:
            Token: A token containing the access token and token type.
    """
    user = get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password,user.hashed_password):
        settings.logger.warning(f"Failed login attempt for email: {form_data.username}")
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or Password",
            headers={"WWW-Authenticate":"Bearer"}   
        )
    access_token = create_access_token(data={"sub":user.email})
    return {"access_token":access_token,"token_type":"bearer"}

@router.get("/",response_model=list[UserIn])
def get_users(db:Session=Depends(get_db)):
    """
        Retrieve all registered users.

        Args:
            db (Session): The database session dependency.

        Returns:
            list[UserIn]: A list of registered users.
    """
    users = get_all_users(db)
    return users
    

@router.get("/{name}",response_model=UserIn)
def get_user_by_name(name:str,db:Session = Depends(get_db)):
    """
        Retrieve a user by their username.

        Args:
            name (str): The username of the user to retrieve.
            db (Session): The database session dependency.

        Raises:
            HTTPException: If the user is not found.

        Returns:
            UserIn: The user object if found.
    """
    user = get_user_by_username(db,name=name)
    if not user:
        settings.logger.info(f"User not found: {name}")
        raise HTTPException(status_code=400,detail="User not found")
    return user
    