from app import app, db
from app.models import *

def setup_database():
    with app.app_context():          # ✅ Add this line
        db.create_all()
        print("Database and tables created.")