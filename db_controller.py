import random
import sqlite3
import time

# Connect to the database or create it if not exists
connector = sqlite3.connect('student_records.db')

# Create a cursor
init_cursor = connector.cursor()

# Create a table to store student information
init_cursor.execute('''
    CREATE TABLE IF NOT EXISTS students
         (id INTEGER PRIMARY KEY,
          first_name TEXT,
          last_name TEXT,
          email TEXT,
          password TEXT,
          access_token TEXT,
          token_created_at INTEGER,
          period_1 TEXT DEFAULT NULL,
          period_2 TEXT DEFAULT NULL,
          period_3 TEXT DEFAULT NULL,
          period_4 TEXT DEFAULT NULL,
          period_5 TEXT DEFAULT NULL,
          period_6 TEXT DEFAULT NULL,
          period_7 TEXT DEFAULT NULL
          )
        ''')

init_cursor.execute('''
    CREATE TABLE IF NOT EXISTS otp_data (
        id INTEGER PRIMARY KEY,
        email TEXT NOT NULL,
        otp TEXT,
        approved BOOLEAN DEFAULT FALSE,
        first_name TEXT,
        last_name TEXT,
        password TEXT
    )
''')

init_cursor.execute('''
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY,
        course_category TEXT NOT NULL,
        course_name TEXT NOT NULL,
        teacher_name TEXT NOT NULL,
        course_code TEXT NOT NULL
    )
''')

connector.commit()
connector.close()


def create_user(email):
    conn = sqlite3.connect('student_records.db')
    cursor = conn.cursor()

    # Check if the email already exists in the 'students' table
    cursor.execute('SELECT * FROM students WHERE email = ?', (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return False
    else:
        # Fetch missing info from the 'otp_data' table
        cursor.execute("SELECT first_name, last_name, password FROM otp_data WHERE email = ?", (email,))
        otp_data = cursor.fetchone()

        if otp_data:
            first_name, last_name, password = otp_data
            cursor.execute('''INSERT INTO students
                              (first_name, last_name, email, password, period_1, period_2, period_3, period_4, period_5, period_6, period_7)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (first_name, last_name, email, password, "", "", "", "", "", "", ""))
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False


def add_user_courses(email, classes):
    conn = sqlite3.connect('student_records.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE email = ?", (email,))
    existing_user = cursor.fetchone()
    for i in range(len(classes), 8):
        classes.append(None)
    if existing_user:
        cursor.execute(
            '''UPDATE students SET period_1 = ?, period_2 = ?, period_3 = ?, period_4 = ?, period_5 = ?, period_6 = 
            ?, period_7 = ? WHERE email = ?''',
            (classes[0], classes[1], classes[2], classes[3], classes[4], classes[5], classes[6], email))
        conn.commit()
    conn.close()
    return True


def generate_code():
    code = ""
    for i in range(6):
        code += str(random.randint(0, 9))
    return code


import sqlite3
import secrets


def insert_random_otp(email, first_name, last_name, password):
    conn = sqlite3.connect('student_records.db')
    cursor = conn.cursor()

    # Check if the email is already approved
    cursor.execute('SELECT * FROM otp_data WHERE email = ?', (email,))
    existing_data = cursor.fetchone()
    if existing_data:
        if existing_data[3] == 1:  # Check if 'approved' column is True (1)
            conn.close()
            return None

        code = generate_code()
        cursor.execute('UPDATE otp_data SET otp = ? WHERE email = ?', (code, email))
    else:
        code = generate_code()
        cursor.execute('''INSERT INTO otp_data (email, otp, approved, first_name, last_name, password) 
                                VALUES (?, ?, ?, ?, ?, ?)''', (email, code, 0, first_name, last_name, password))

    conn.commit()
    conn.close()
    return code


# Function to retrieve OTP data by email
def verify_OTP(email, test_otp):
    conn = sqlite3.connect('student_records.db')
    cursor = conn.cursor()
    cursor.execute('SELECT otp FROM otp_data WHERE email = ?', (email,))
    otp = cursor.fetchone()
    if otp[0] == test_otp:
        cursor.execute('UPDATE otp_data SET approved = TRUE WHERE email = ?', (email,))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False


def approved_user(email):
    conn = sqlite3.connect('student_records.db')
    cursor = conn.cursor()
    cursor.execute('SELECT approved FROM otp_data WHERE email = ?', (email,))
    approved = cursor.fetchone()
    if approved is None:
        conn.close()
        return False
    if approved[0] == 1:
        conn.close()
        return True
    else:
        conn.close()
        return False


def new_otp(email):
    conn = sqlite3.connect('student_records.db')
    cursor = conn.cursor()
    cursor.execute('SELECT approved FROM otp_data WHERE email = ?', (email,))
    existing_data = cursor.fetchone()
    if existing_data:
        if existing_data[0] != 1:  # Check if 'approved' column is True (1)
            conn.close()
            return None

        code = generate_code()
        cursor.execute('UPDATE otp_data SET otp = ? WHERE email = ?', (code, email))
    else:
        conn.close()
        return None

    conn.commit()
    conn.close()
    return code


def get_courses():
    conn = sqlite3.connect('student_records.db')
    cursor = conn.cursor()
    cursor.execute('SELECT course_category, course_name, teacher_name, course_code FROM courses')
    courses = cursor.fetchall()
    conn.close()

    courses_by_category = {}  # Create a dictionary to store courses by category

    for course in courses:
        category, course_name, teacher_name, course_code = course

        if category not in courses_by_category:
            courses_by_category[category] = []

        course_info = {
            "course_name": course_name,
            "teacher_name": teacher_name,
            "course_code": course_code
        }

        courses_by_category[category].append(course_info)

    return courses_by_category


def insert_course(category, course_name, teacher_name, code):
    conn = sqlite3.connect('student_records.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO courses
                      (course_category, course_name, teacher_name, course_code) VALUES (?, ?, ?, ?)''',
                   (category, course_name, teacher_name, code))
    conn.commit()
    conn.close()


def login(email, password):
    conn = sqlite3.connect('student_records.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, password FROM students WHERE email = ?', (email,))
    user = cursor.fetchone()
    if user is None:
        conn.close()
        return False

    if user[1] == password:
        current_time = time.time()
        access_token = secrets.token_hex(16)  # Adjust the token length as needed
        cursor.execute('UPDATE students SET access_token = ?, token_created_at = ? WHERE id = ?',
                       (access_token, current_time, user[0]))
        conn.commit()
        conn.close()
        return access_token
    else:
        conn.close()
        return False


def check_token(email, token):
    conn = sqlite3.connect('student_records.db')
    cursor = conn.cursor()
    cursor.execute('SELECT access_token, token_created_at FROM students WHERE email = ?', (email,))
    token_info = cursor.fetchone()

    if token_info is None:
        conn.close()
        return False

    access_token = token_info[0]
    token_created_at = token_info[1]
    current_time = time.time()
    token_age = current_time - token_created_at

    if access_token == token and token_age <= 604800:  # 604800 seconds = 1 week
        conn.close()
        return True
    else:
        conn.close()
        return False


def logout(email):
    conn = sqlite3.connect('student_records.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE students SET access_token = NULL, token_created_at = NULL WHERE email = ?', (email,))
    conn.commit()
    conn.close()


import json


def get_classmates(email):
    conn = sqlite3.connect('student_records.db')
    cursor = conn.cursor()

    cursor.execute(
        '''SELECT period_1, period_2, period_3, period_4, period_5, period_6, period_7 FROM students WHERE email = ?''',
        (email,))
    classes = cursor.fetchone()

    classmates_by_period = {}
    if classes:
        for period, course_code in enumerate(classes, start=1):
            if course_code:
                # Retrieve classmates for each class in the period
                cursor.execute(
                    '''SELECT first_name, last_name, email FROM students WHERE period_{period} = ? AND email != ?'''.format(
                        period=period),
                    (course_code, email))
                classmates = cursor.fetchall()
                if classmates:
                    classmates_info = [{
                        "first_name": row[0],
                        "last_name": row[1],
                        "email": row[2]
                    } for row in classmates]
                    classmates_by_period[f"Period {period} ({course_code})"] = classmates_info
                else:
                    classmates_by_period[f"Period {period} ({course_code})"] = []

    conn.close()
    return classmates_by_period


def check_email(email):
    conn = sqlite3.connect('student_records.db')
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM students WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    if user is None:
        return False
    else:
        return True


def update_user_password(email, new_password):
    conn = sqlite3.connect('student_records.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE students SET password = ? WHERE email = ?', (new_password, email))
    conn.commit()
    conn.close()


def clear_otp(email):
    conn = sqlite3.connect('student_records.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE otp_data SET otp = NULL WHERE email = ?', (email,))
    conn.commit()
    conn.close()
