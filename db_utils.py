import os
from datetime import datetime
import streamlit as st 
import sqlite3
import qrcode
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image
import cv2


#buildinf=g setup files for qrcode and face encoding
os.makedirs("qrcodes",exist_ok=True)
os.makedirs("encodings",exist_ok=True)


#creating database
def init_db():
    student_db=sqlite3.connect("students.db")
    queries=student_db.cursor()

    # create a table to store students
    queries.execute(
        '''
            CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll TEXT UNIQUE NOT NULL,
            class TEXT NOT NULL
            )
    '''
    )


    #creating attendance table
    queries.execute('''
            CREATE TABLE IF NOT EXISTS attendance(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                date TEXT,
                time TEXT,
                method TEXT,
                status TEXT NOT NULL,
                FOREIGN KEY(student_id) REFERENCES students(id)
            )
            '''    
    )

    student_db.commit()
    student_db.close()


# function to add student + qrcode  +face recognition encodings
def add_student(name,roll,class_name,img_file):
    student_db=sqlite3.connect("students.db")
    queries=student_db.cursor()

    try:
        queries.execute(
            "INsert into students (name,roll,class) VALUES (?,?,?)",(name,roll,class_name)
        )
        student_db.commit()

        #now after the adding of students details let's generatre QRCODE based on the roll no.(unique)
        qr=qrcode.make(roll) #generating qrcode
        qr.save(f"qrcodes/{roll}.png")  #saving qrcode as png format for  each regisyred student in qrcodes folder

        
        st.success(f" student {name} addedd successfully! with qrcode and face encodings")
    except sqlite3.IntegrityError:
        st.error("Roll number already exists")


    student_db.close()


#fetch students
def fetch_student():
    student_db=sqlite3.connect('students.db')
    queries=student_db.cursor()

    queries.execute(
        "select * from students"
    )
    rows=queries.fetchall()
    student_db.close()
    return rows

# View Attendance
def fetch_attendance():
        db = sqlite3.connect("students.db")  # use same DB
        cur = db.cursor()
        cur.execute("""
            SELECT s.name, s.roll, s.class, a.date, a.time, a.method, a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            ORDER BY a.date DESC, a.time DESC
        """)
        rows = cur.fetchall()
        db.close()
        return rows




def mark_attendance(roll):
    db = sqlite3.connect("students.db")
    cur = db.cursor()

    # get student_id from roll
    cur.execute("SELECT id FROM students WHERE roll=?", (roll,))
    student = cur.fetchone()
    if not student:
        db.close()
        return f"Student with roll {roll} not found!"

    student_id = student[0]

    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M:%S")

    # avoid duplicate for same day
    cur.execute("SELECT * FROM attendance WHERE student_id=? AND date=?", (student_id, today))
    existing = cur.fetchone()

    if not existing:
        cur.execute(
            "INSERT INTO attendance (student_id, date, time, method, status) VALUES (?, ?, ?, ?, ?)",
            (student_id, today, now, "QR", "Present")
        )
        db.commit()
        status = f"Attendance marked for roll {roll}"
    else:
        status = f"Attendance already marked today"

    db.close()
    return status


#Setting up QR Scanner with opencv and pyzbar
# def scan_qr():
#     cap=cv2.VideoCapture(0)

#     while True:
#         ret,frame=cap.read()

#         if not ret:
#             st.warning("could not read frame")
#             break

#     #copy pasted code
#         for qr in decode(frame):
#             qr_data = qr.data.decode("utf-8")
#             # Draw rectangle
#             pts = qr.polygon
#             pts = [(pt.x, pt.y) for pt in pts]
#             pts = cv2.convexHull(np.array(pts, dtype=np.int32))
#             cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
#             cv2.putText(frame, qr_data, (qr.rect.left, qr.rect.top - 10),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
#             cap.release()
#             cv2.destroyAllWindows()
#             return qr_data  # Return first scanned QR(returnning roll number)
        
    
#         cv2.imshow("QR Scanner - Press Q to exit", frame)

#         if cv2.waitKey(1) & 0xFF == ord("q"):
#             break

#     cap.release()
#     cv2.destroyAllWindows()
#     return None

#FOR STREAMLIT DEPLOY
def scan_qr():
    st.info("Scan a QR Code using your webcam")

    # Streamlit camera input
    img_file = st.camera_input("Take a picture of the QR Code")

    if img_file is not None:
        # Convert to OpenCV format
        img = Image.open(img_file)
        frame = np.array(img)

        # Decode QR
        decoded_objs = decode(frame)
        qr_data = None
        for obj in decoded_objs:
            qr_data = obj.data.decode("utf-8")

            # Draw rectangle around QR
            pts = [(pt.x, pt.y) for pt in obj.polygon]
            pts = np.array(pts, dtype=np.int32)
            cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
            cv2.putText(frame, qr_data, (obj.rect.left, obj.rect.top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        # Show scanned frame in Streamlit
        st.image(frame, channels="RGB")

        if qr_data:
            return qr_data
        else:
            st.warning("No QR code detected. Please try again.")

    return None


#QR Attendance page
def qr_attendance_page():
    st.title("QR Attendance System")

    if st.button("Scan QR"):
        st.info("Scanning...Hold QR in front of camera")

        qr_data=scan_qr()

        if qr_data: #if QR is scanned
            #checking student exist in db
            attendance_db=sqlite3.connect("students.db")
            att_queries=attendance_db.cursor()

            att_queries.execute("SELECT * from students where roll=?",(qr_data,))
            student=att_queries.fetchone()
            attendance_db.close()

            if student:
                status=mark_attendance(qr_data) #here qr_data is roll number
                st.success(status)
            else:
                st.error("Student not found in database")

        else:
            st.warning("No QR is detected")        
                

