from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.crud.counter_management import get_counter_by_service_id
from app.crud.services_management import get_service_by_name
from app.schemas.token_schemas import TokenCreate,TokenRequest, TokenResponse
from app.schemas.user_schemas import  UserIn,UserCreate,Token
from app.db.database import get_db
from app.utils.auth import get_password_hash,verify_password,create_access_token
from app.crud.user_management import create_user,get_user_by_email,get_all_users,get_user_by_username
from app.core.config import settings    
from app.crud.token_management import create_token_record


router = APIRouter()

@router.post("/register",response_model=UserIn)
def register_user(user:UserCreate,db:Session = Depends(get_db)):
    """
        Register a new user.

        This endpoint allows a new user to register by providing a username, email, 
        and password. It checks for existing users with the same email and 
        hashes the password before storing it.

        Parameters:
            - user (UserCreate): The user details for registration.
            - db (Session, optional): The database session. Defaults to a dependency from `get_db`.

        Raises:
            - HTTPException: If the email is already registered (status code 400).
            - HTTPException: If there's an error creating the user (status code 500).

        Returns:
            - UserIn: The created user object.
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
        new_user = create_user(db,user.name,user.email,hashed_password)
    except Exception as e:
        settings.logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create user, please try again later: {e}"
        )
    return UserIn(id=new_user.id,name=new_user.name,email=new_user.email,role=new_user.role)


@router.post("/login",response_model=Token)
def login_for_access_token(form_data:OAuth2PasswordRequestForm = Depends(),db:Session = Depends(get_db) ):
    """
        Login a user and return an access token.

        This endpoint allows a user to log in by providing their email and password. 
        If successful, it generates and returns an access token for authenticated access.

        Parameters:
            - form_data (OAuth2PasswordRequestForm, optional): The login credentials (email and password).
            - db (Session, optional): The database session. Defaults to a dependency from `get_db`.

        Raises:
            - HTTPException: If the login credentials are incorrect (status code 400).

        Returns:
            - Token: An object containing the access token and its type.
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
        Retrieve a list of all registered users.

        This endpoint returns a list of all users stored in the database.

        Parameters:
            - db (Session, optional): The database session. Defaults to a dependency from `get_db`.

        Returns:
            - list[UserIn]: A list of user objects.
    """
    users = get_all_users(db)
    return users
    

@router.get("/{name}",response_model=UserIn)
def get_user_by_name(name:str,db:Session = Depends(get_db)):
    """
        Retrieve a user by their username.

        This endpoint allows the retrieval of a user’s details using their username. 
        If the user is not found, a 404 error is raised.

        Parameters:
            - name (str): The username of the user to retrieve.
            - db (Session, optional): The database session. Defaults to a dependency from `get_db`.

        Raises:
            - HTTPException: If the user is not found (status code 400).

        Returns:
            - UserIn: The user object corresponding to the provided username.
    """
    user = get_user_by_username(db,name=name)
    if not user:
        settings.logger.info(f"User not found: {name}")
        raise HTTPException(status_code=400,detail="User not found")
    return user


@router.post("/token", response_model=TokenResponse)
def generate_token_for_user(request: TokenRequest, db: Session = Depends(get_db)):
    # Get user by email
    user = get_user_by_email(db, request.email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Get service by name
    service = get_service_by_name(db, request.service_name)
    if not service:
        raise HTTPException(status_code=400, detail="Service not found")

    # Access the service ID from the dictionary
    service_id = service['id']  

    # Get counter responsible for this service
    counter_id = get_counter_by_service_id(db, service_id)
    if counter_id is None:
        raise HTTPException(status_code=400, detail="No counter available for this service")

    # Generate the token and store it in the database
    token_data = TokenCreate(
        user_id=user.id,
        service_id=service_id,
        counter_id=counter_id,  
        latitude=request.latitude,
        longitude=request.longitude
    )
    
    try:
        token = create_token_record(db, token_data)
        
        # Return a TokenResponse
        return TokenResponse(
            token_number=token.token_number,
            user_id=token.user_id,
            service_id=token.service_id,
            counter_id=token.counter_id,
            status="Token generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating token: {str(e)}")