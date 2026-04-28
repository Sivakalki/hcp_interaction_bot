import sys
import os

# Add the parent directory to sys.path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import init_db
from app.core.config import get_settings

def run_init():
    settings = get_settings()
    print(f"Initializing database at: {settings.DB_URL}")
    try:
        init_db()
        print("✅ Database tables created successfully.")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

if __name__ == "__main__":
    run_init()
