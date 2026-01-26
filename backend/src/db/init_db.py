import sys
import os

# Add backend directory to path
sys.path.append(os.getcwd())

from src.db.session import init_db
from src.db.models import Session

if __name__ == "__main__":
    print("Creating database tables...")
    try:
        init_db()
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
