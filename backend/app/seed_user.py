import os
import sys
from sqlalchemy.orm import Session

# Add the parent directory to sys.path so app can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.db import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, Profile
from app.routers.auth import calculate_default_zones

def seed_default_user():
    db: Session = SessionLocal()
    try:
        email = "mdziurgot@gmail.com"
        password = os.getenv("SEED_USER_PASSWORD", "BibiCoach2026!")
        
        # Check if the user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User {email} already exists in the database. Skipping seeding.")
            return

        print(f"Seeding user: {email}")
        db_user = User(
            email=email,
            password_hash=get_password_hash(password)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Calculate default zones for FTP=200, MaxHR=190
        ftp = 200
        max_hr = 190
        power_z, hr_z = calculate_default_zones(ftp, max_hr)

        # Create Profile
        db_profile = Profile(
            user_id=db_user.id,
            ftp=ftp,
            w_prime=20000,
            resting_hr=60,
            max_hr=max_hr,
            weight_kg=78.0,
            power_zones=power_z,
            hr_zones=hr_z,
            weekly_availability={"mon": 0, "tue": 90, "wed": 90, "thu": 90, "fri": 0, "sat": 180, "sun": 180}
        )
        db.add(db_profile)
        db.commit()
        
        print(f"Successfully seeded user {email} with profile (FTP: {ftp}W, Weight: 78.0kg).")
        print(f"Temporary password: {password}")
        print("IMPORTANT: Change your password or update SEED_USER_PASSWORD in your production environment variables.")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding user: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_default_user()
