from app import app, db
from sqlalchemy import text
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

def create_admin():
    with app.app_context():
        try:
            admin_count = db.session.execute(
                text("SELECT COUNT(*) as count FROM user WHERE role='admin'")
            ).fetchone()
            
            if admin_count and admin_count.count > 0:
                print("Admin gagal dibuat karena sudah ada datanya")
                return
            
            admin_username = os.getenv('ADMIN_USERNAME')
            admin_password = os.getenv('ADMIN_PASSWORD')
            
            password_hash = generate_password_hash(admin_password)
            
            db.session.execute(
                text("INSERT INTO user (username, password_hash, role) VALUES (:u, :p, :r)"),
                {'u': admin_username, 'p': password_hash, 'r': 'admin'}
            )
            db.session.commit()
            
            print("Admin telah dibuat")
            print(f"Username: {admin_username}")
            print(f"Password: {admin_password}")
            print("Role    : admin")
            
        except Exception as e:
            print(f"error : {e}")

if __name__ == '__main__':
    create_admin()