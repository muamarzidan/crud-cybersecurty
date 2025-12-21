from app import app, db
from sqlalchemy import text
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

def create_admin():
    with app.app_context():
        try:
            existing_admin = db.session.execute(
                text("SELECT * FROM user WHERE role='admin'")
            ).fetchone()
            
            admin_username = os.getenv('ADMIN_USERNAME')
            admin_password = os.getenv('ADMIN_PASSWORD')
            
            if existing_admin:
                print("ADMIN SUDAH ADA DI SISTEM")
                print(f"Username saat ini: {existing_admin.username}")
                print("\nApakah Anda ingin UPDATE username dan password admin?")
                print("Kredensial baru akan diambil dari file .env")
                print(f" ADMIN_USERNAME: {admin_username}")
                print(f" ADMIN_PASSWORD: {admin_password}")
                print("="*60)
                
                while True:
                    pilihan = input("Update admin? (y/n): ").strip().lower()
                    if pilihan in ['y', 'n', 'yes', 'no']:
                        break
                    print("Input tidak valid, ketik 'y' atau 'n'")
                
                if pilihan in ['n', 'no']:
                    print("\nProses dibatalkan, admin tidak diubah")
                    return
                
                password_hash = generate_password_hash(admin_password)
                db.session.execute(
                    text("UPDATE user SET username=:u, password_hash=:p WHERE role='admin'"),
                    {'u': admin_username, 'p': password_hash}
                )
                db.session.commit()
                
                print("\n" + "="*60)
                print("ADMIN BERHASIL DIUPDATE")
                print(f"Username baru: {admin_username}")
                print(f"Password baru: {admin_password}")
                print("Role        : admin")
                print("\nCATATAN: Maksimal hanya 1 admin di sistem")
                
            else:
                password_hash = generate_password_hash(admin_password)
                
                db.session.execute(
                    text("INSERT INTO user (username, password_hash, role) VALUES (:u, :p, :r)"),
                    {'u': admin_username, 'p': password_hash, 'r': 'admin'}
                )
                db.session.commit()
                
                print("ADMIN BERHASIL DIBUAT!")
                print("="*60)
                print(f"Username: {admin_username}")
                print(f"Password: {admin_password}")
                print("Role    : admin")
                print("\n CATATAN: Maksimal hanya 1 admin di sistem")
            
        except Exception as e:
            print(f"\nerr: {e}")

if __name__ == '__main__':
    create_admin()