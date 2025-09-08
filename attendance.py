from datetime import datetime
import streamlit as st 
import sqlite3
import qrcode
import numpy as np
import face_recognition
import os
from pyzbar.pyzbar import decode
import cv2
from db_utils import add_student,init_db,fetch_student

#MARKING ATTENDANCE

def mark_attendance(roll):
    attendance_db=sqlite3.connect("attendance.db")
    att_queries=attendance_db.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M:%S")

    #avoiding duplicates attendance on same day
    att_queries.execute("Select * from attendance_db where roll=? and date=?",(roll,today))
    existing=att_queries.fetchone()

    #if Not already exist
    if not existing:
        att_queries.execute("INSERT INTO attendance (roll, date, time, status) VALUES (?, ?, ?, ?)",
                       (roll, today, now, "Present"))
        attendance_db.commit()
        status=f"Attendance marked for roll {roll}"
    else:
        status=f"attendance already marked"

    attendance_db.close()
    return status



#Setting up QR Scanner with opencv and pyzbar
def scan_qr():
    cap=cv2.VideoCapture(0)

    while True:
        ret,frame=cap.read()

        if not ret:
            st.warning("could not read frame")
            break

    #copy pasted code
        for qr in decode(frame):
            qr_data = qr.data.decode("utf-8")
            # Draw rectangle
            pts = qr.polygon
            pts = [(pt.x, pt.y) for pt in pts]
            pts = cv2.convexHull(np.array(pts, dtype=np.int32))
            cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
            cv2.putText(frame, qr_data, (qr.rect.left, qr.rect.top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
            cap.release()
            cv2.destroyAllWindows()
            return qr_data  # Return first scanned QR(returnning roll number)
        
    
        cv2.imshow("QR Scanner - Press Q to exit", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None



#QR Attendance page
def qr_attendance_page():
    st.title("QR Attendance System")

    if st.button("Scan QR"):
        st.info("Scanning...Hold QR in front of camera")

        qr_data=scan_qr()

        if qr_data: #if QR is scanned
            #checking student exist in db
            attendance_db=sqlite3.connect("attendance.db")
            att_queries=attendance_db.cursor()

            att_queries.execute("SELECT * from attendance where roll=?",(qr_data,))
            student=att_queries.fetchone()
            attendance_db.close()

            if student:
                status=mark_attendance(qr_data) #here qr_data is roll number
                st.success(status)
            else:
                st.error("Student not found in database")

        else:
            st.warning("No QR is detected")        
                

# View Attendance
def fetch_attendance():
    attendance_db=sqlite3.connect("attendance.db")
    att_queries=attendance_db.cursor()
    att_queries.execute("select * from attendance order by date desc,time desc")
    rows=att_queries.fetchall()
    attendance_db.close()
    return rows
