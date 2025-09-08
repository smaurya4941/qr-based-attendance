import streamlit as st 
import sqlite3
import qrcode
import numpy as np
import os
import cv2
from db_utils import init_db,qr_attendance_page,mark_attendance,fetch_attendance,add_student,fetch_student

#Now streamlit UI Working
def main():
    st.set_page_config(page_title="Smart Attendance App")
    st.title("Attendance App")

    #creating sidebar
    st.sidebar.title("Navigation")
    menu=st.sidebar.radio("Go to",["Home","QR attendance","Register students","view Students","View Attendance"])

    #based on selected optionsfrom menu  ==> appears on main page
    #HOME PAGE
    if menu=="Home":
        st.subheader("This is Home page")
        st.info("Hello welcome to student smart attendance app")

    #REGISTRATION  page
    elif menu=="Register students":
        st.subheader("Register Students")
        with st.form("Student Registration Form",clear_on_submit=True):
            name=st.text_input("Enter your name here")
            roll=st.text_input("Enter roll no.")
            class_name=st.text_input("Enter yout class")
            img_file=st.file_uploader("upload student face image", type=['jpg','png','jpeg'])
            submitted=st.form_submit_button("Register")
            
            #checking whether all columns are filled or not
            if submitted:
                if name and roll and class_name and img_file:
                    add_student(name,roll,class_name,img_file)
                else:
                    st.warning("Enter all details")
    #Viewing STUDENTS
    elif menu=="view Students":
        st.subheader("Viewing Students")
        students=fetch_student()
        if students:
            st.table(students)
        else:
            st.warning("No students found")

    #QR Attendance page
    elif menu=="QR attendance":
        qr_attendance_page()

    #VIEWING ATTENDANCE PAGE
    elif menu=="View Attendance":
        st.subheader("Attendance Records")
        attendance=fetch_attendance()
        if attendance:
            st.table(attendance)
        else:
            st.warning("No attendance records found")
        
        


if __name__ == "__main__":
    init_db()
    main()