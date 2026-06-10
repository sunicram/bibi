from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.db import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.models.user import User, Profile, AuthSession
from app.schemas.user import UserCreate, UserLogin, Token, ProfileUpdate, UserResponse, ProfileResponse

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    
    user_id_str = decode_token(token)
    if not user_id_str:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == UUID(user_id_str)).first()
    if not user:
        raise credentials_exception
    return user

def calculate_default_zones(ftp: int, max_hr: int) -> tuple[dict, dict]:
    # Coggan 7-zone Power Model
    power_zones = {
        "z1_recovery": {"min": 0, "max": int(round(ftp * 0.55))},
        "z2_endurance": {"min": int(round(ftp * 0.56)), "max": int(round(ftp * 0.75))},
        "z3_tempo": {"min": int(round(ftp * 0.76)), "max": int(round(ftp * 0.90))},
        "z4_sweetspot": {"min": int(round(ftp * 0.88)), "max": int(round(ftp * 0.93))},
        "z4_threshold": {"min": int(round(ftp * 0.91)), "max": int(round(ftp * 1.05))},
        "z5_vo2max": {"min": int(round(ftp * 1.06)), "max": int(round(ftp * 1.20))},
        "z6_anaerobic": {"min": int(round(ftp * 1.21)), "max": int(round(ftp * 1.50))},
        "z7_neuromuscular": {"min": int(round(ftp * 1.51)), "max": 9999}
    }
    
    # 5-zone HR Model (Estimates based on Max HR)
    hr_zones = {
        "z1_recovery": {"min": 0, "max": int(round(max_hr * 0.60))},
        "z2_endurance": {"min": int(round(max_hr * 0.61)), "max": int(round(max_hr * 0.70))},
        "z3_tempo": {"min": int(round(max_hr * 0.71)), "max": int(round(max_hr * 0.80))},
        "z4_threshold": {"min": int(round(max_hr * 0.81)), "max": int(round(max_hr * 0.90))},
        "z5_vo2max": {"min": int(round(max_hr * 0.91)), "max": max_hr}
    }
    return power_zones, hr_zones

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if email exists
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    db_user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create empty default profile
    power_z, hr_z = calculate_default_zones(200, 190)
    db_profile = Profile(
        user_id=db_user.id,
        ftp=200,
        w_prime=20000,
        resting_hr=60,
        max_hr=190,
        weight_kg=75.0,
        power_zones=power_z,
        hr_zones=hr_z,
        weekly_availability={"mon": 0, "tue": 90, "wed": 90, "thu": 90, "fri": 0, "sat": 180, "sun": 180}
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
        
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    # Save session
    session = AuthSession(
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.add(session)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
def refresh(refresh_token: str = Header(...), db: Session = Depends(get_db)):
    user_id_str = decode_token(refresh_token)
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    # Check if session exists in DB
    session = db.query(AuthSession).filter(
        AuthSession.user_id == UUID(user_id_str),
        AuthSession.refresh_token == refresh_token,
        AuthSession.expires_at > datetime.utcnow()
    ).first()
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
        
    # Generate new tokens
    new_access = create_access_token(user_id_str)
    new_refresh = create_refresh_token(user_id_str)
    
    # Rotate refresh token
    session.refresh_token = new_refresh
    session.expires_at = datetime.utcnow() + timedelta(days=30)
    db.commit()
    
    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me/profile", response_model=ProfileResponse)
def update_profile(
    profile_in: ProfileUpdate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    profile = current_user.profile
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
        
    # Update fields
    profile.ftp = profile_in.ftp
    profile.w_prime = profile_in.w_prime
    profile.resting_hr = profile_in.resting_hr
    profile.max_hr = profile_in.max_hr
    profile.weight_kg = profile_in.weight_kg
    
    # Recalculate power/HR zones if not manually customized
    power_z, hr_z = calculate_default_zones(profile_in.ftp, profile_in.max_hr)
    profile.power_zones = profile_in.power_zones or power_z
    profile.hr_zones = profile_in.hr_zones or hr_z
    
    profile.weekly_availability = profile_in.weekly_availability
    profile.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(profile)
    return profile
