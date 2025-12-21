from app import app, db
from sqlalchemy import text
from werkzeug.security import generate_password_hash
import re

def create_user(username, password):
    with app.app_context():
        try:
            existing_user = db.session.execute(
                text("SELECT * FROM user WHERE username = :username"),
                {'username': username}
            ).fetchone()
            
            if existing_user:
                print(f"Username '{username}' sudah digunakan!")
                return False
            
            password_hash = generate_password_hash(password)
            
            db.session.execute(
                text("INSERT INTO user (username, password_hash, role) VALUES (:u, :p, :r)"),
                {'u': username, 'p': password_hash, 'r': 'user'}
            )
            db.session.commit()
            
            print("User berhasil dibuat")
            print(f"Username: {username}")
            print(f"Password: {password}")
            print("Role    : user")
            return True
            
        except Exception as e:
            print(f"error : {e}")
            return False

def main():
    print("Input user baru ke sistem")
    
    while True:
        print("Masukkan data user baru:")
        username = input("Username: ").strip()
        
        if not username:
            print("Username tidak boleh kosong!\n")
            continue
        
        if len(username) < 6:
            print("Username minimal 6 karakter!\n")
            continue
        
        password = input("Password: ").strip()
        
        if not password:
            print("Password tidak boleh kosong!\n")
            continue
        
        if len(password) < 12:
            print("Password minimal 12 karakter!\n")
            continue
        
        if not re.search(r'[A-Z]', password):
            print("Password harus mengandung minimal 1 huruf BESAR!\n")
            continue
        
        if not re.search(r'[a-z]', password):
            print("Password harus mengandung minimal 1 huruf kecil!\n")
            continue
        
        if not re.search(r'[0-9]', password):
            print("Password harus mengandung minimal 1 angka!\n")
            continue
        
        password_confirm = input("Konfirmasi Password: ").strip()
        
        if password != password_confirm:
            print("Password tidak cocok!\n")
            continue
        
        print()
        success = create_user(username, password)
        
        if not success:
            print("Coba lagi dengan username lain.\n")
            continue
        
        print()
        while True:
            lanjut = input("Buat user lagi? (y/n): ").strip().lower()
            if lanjut in ['y', 'n', 'yes', 'no']:
                break
            print("Input tidak valid, ketik 'y' atau 'n'")
        
        if lanjut in ['n', 'no']:
            print("Selesai")
            print("Semua user berhasil dibuat")
            break
        
        print("\n" + "-" * 60)
        print("Buat user baru:")
        print("-" * 60 + "\n")

if __name__ == '__main__':
    with app.app_context():
        try:
            db.session.execute(text("SELECT 1 FROM user LIMIT 1"))
            main()
        except Exception as e:
            print("Tabel di database belum ada")