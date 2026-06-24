from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_PASSWORD",
        database="student_db"
    )

@app.route('/')
def home():
    if 'user' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            session['user'] = username
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")

    total_students = cursor.fetchone()[0]

    return render_template(
        'dashboard.html',
        total_students=total_students
    )

@app.route('/add', methods=['GET', 'POST'])
def add_student():

    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':

        name = request.form['name']
        roll_no = request.form['roll_no']
        cgpa = request.form['cgpa']

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO students (name, roll_no, cgpa) VALUES (%s, %s, %s)",
            (name, roll_no, cgpa)
        )

        db.commit()

        return render_template(
            'add.html',
            success="Student added successfully!"
        )

    return render_template('add.html')


@app.route('/students')
def students():

    if 'user' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    return render_template(
        'students.html',
        students=students

    )

@app.route('/delete/<int:id>')
def delete_student(id):

    if 'user' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id=%s",
        (id,)
    )

    db.commit()

    return redirect('/students')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):

    if 'user' not in session:
        return redirect('/login')

    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':

        name = request.form['name']
        roll_no = request.form['roll_no']
        cgpa = request.form['cgpa']

        cursor.execute(
            "UPDATE students SET name=%s, roll_no=%s, cgpa=%s WHERE id=%s",
            (name, roll_no, cgpa, id)
        )

        db.commit()

        return render_template(
            'edit.html',
            student=(id, name, roll_no, cgpa),
            success="Student updated successfully!"
        )

    cursor.execute(
        "SELECT * FROM students WHERE id=%s",
        (id,)
    )

    student = cursor.fetchone()

    return render_template(
        'edit.html',
        student=student
    )

@app.route('/search', methods=['GET', 'POST'])
def search():

    if 'user' not in session:
        return redirect('/login')

    student = None

    if request.method == 'POST':

        roll_no = request.form['roll_no']

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE roll_no = %s",
            (roll_no,)
        )

        student = cursor.fetchone()

    return render_template(
        'search.html',
        student=student
    )

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)