import argparse
from getpass import getpass
from backend.app.db.session import SessionLocal
from backend.app.db.models import User
from backend.app.core.security import get_password_hash

def create_user(email: str, username: str, full_name: str, password: str):
    db = SessionLocal()
    try:
        # Check if user exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User {email} already exists!")
            return

        hashed_pw = get_password_hash(password)
        user = User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=hashed_pw
        )
        db.add(user)
        db.commit()
        print(f"User {email} created successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new user")
    parser.add_argument("--username", required=True, help="Username")
    parser.add_argument("--email", required=True, help="User email")
    parser.add_argument("--full_name", required=False, help="Full name")
    args = parser.parse_args()

    password = getpass("Password: ")
    confirm = getpass("Confirm password: ")
    if password != confirm:
        print("Passwords do not match!")
        exit(1)

    create_user(args.email, args.username, args.full_name, password)