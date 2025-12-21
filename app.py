from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import check_password_hash
from functools import wraps
import os
from dotenv import load_dotenv
import re
import html

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            return redirect(url_for('index'))
        if not session.get('verified'):
            return redirect(url_for('verify_code'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = db.session.execute(
            text("SELECT * FROM user WHERE username = :username"),
            {'username': username}
        ).fetchone()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['verified'] = False
            
            if user.role == 'admin':
                return redirect(url_for('verify_code'))
            else:
                session['verified'] = True
                return redirect(url_for('index'))
        else:
            flash('Username atau password salah', 'danger')
    
    return render_template('login.html')

@app.route('/verify_code', methods=['GET', 'POST'])
@login_required
def verify_code():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    if session.get('verified'):
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        code = request.form['code']
        admin_code = os.getenv('ADMIN_CODE')
        
        if code == admin_code:
            session['verified'] = True
            return redirect(url_for('index'))
        else:
            flash('Kode verifikasi salah!', 'danger')
    
    return render_template('verify_code.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    # RAW Query
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    return render_template('index.html', students=students)

@app.route('/add', methods=['POST'])
@admin_required
def add_student():
    raw_name = request.form['name']
    name = html.escape(raw_name)
    age = request.form['age']
    raw_grade = request.form['grade']
    grade = html.escape(raw_grade)

    # name = request.form['name']
    # age = request.form['age']
    # grade = request.form['grade']
    

    # RAW Query
    # db.session.execute(
    #     text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)"),
    #     {'name': name, 'age': age, 'grade': grade}
    # )
    # db.session.commit()
    # query = f"INSERT INTO student (name, age, grade) VALUES ('{name}', {age}, '{grade}')"
    # cursor.execute(query)
    sql = text("INSERT INTO student (name, age, grade) VALUES (:name, :age, :grade)")
    db.session.execute(sql, {'name': name, 'age': age, 'grade': grade})
    db.session.commit()
    flash('Student berhasil ditambahkan!', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<string:id>')
@admin_required 
def delete_student(id):
    if not re.match(r'^\d+$', id):
        return "Yaa gagal yaa", 404

    sql = text("DELETE FROM student WHERE id = :id_valid")
    db.session.execute(sql, {'id_valid': int(id)})
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.name = request.form['name']
        student.age = request.form['age']
        student.grade = request.form['grade']
        
        # RAW Query
        # db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))
        db.session.commit()
        return redirect(url_for('index'))
    else:
        # RAW Query
        # student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
        return render_template('edit.html', student=student)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)