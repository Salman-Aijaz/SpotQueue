from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas.token_schemas import TokenRequest, TokenResponse, UpdateTokenRequest
from app.schemas.user_schemas import UserIn,UserCreate,Token
from app.db.database import get_db
from app.utils.auth import get_password_hash,verify_password,create_access_token
from app.crud.user_management import create_user,get_user_by_email,get_all_users,get_user_by_username
from app.core.config import settings    
from app.crud.token_management import check_reach_out, generate_token, get_token_by_user_id, update_token_distance_duration
from app.utils.get_distance import get_distance

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
async def generate_token_for_user(request: TokenRequest, db: Session = Depends(get_db)):
    try:
        token = await generate_token(request, db)
        
        # Return a TokenResponse
        return TokenResponse(
            token_number=token.token_number,
            user_id=token.user_id,
            service_id=token.service_id,
            counter_id=token.counter_id,
            distance = token.distance,
            duration = token.duration,
            status="Token generated successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating token: {e}")
    
@router.put("/new-location",response_model=TokenResponse)
async def update_eta(request:UpdateTokenRequest,db:Session = Depends(get_db)):
    try:
        token = get_token_by_user_id(db, request.user_id)
        if not token:
            raise HTTPException(status_code=400,detail="Token Not Found")
        
        # Get the new distance and duration
        duration_value,distance_value=await get_distance(request.latitude,request.longitude)

        # Check if the user has reached the service location
        reach_out = check_reach_out(
            latitude=request.latitude,
            longitude=request.longitude,
            distance=distance_value,
            duration=duration_value
        )
        
        # Update the token with the new distance and duration
        updated_token = update_token_distance_duration(
            db=db,
            token=token,
            latitude=request.latitude,
            longitude=request.longitude,
            duration_value=duration_value,
            distance_value=distance_value
        )   
        updated_token.reach_out = reach_out
        db.commit()
        db.refresh(updated_token)

        return TokenResponse(
            token_number = updated_token.token_number,
            user_id = updated_token.user_id,
            service_id = updated_token.service_id,
            counter_id= updated_token.counter_id,
            distance=updated_token.distance,
            duration = updated_token.duration,
            status ="ETA Updated Successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error Updating ETA: {e}")