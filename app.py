from flask import Flask, request, render_template, redirect, url_for, request, jsonify, session, Response
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash
import cv2
import numpy as np
import mediapipe as mp1
import math
import matplotlib.pyplot as plt
from googletrans import LANGUAGES,Translator
from PyPDF2 import PdfReader
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import re
import speech_recognition as sr
import os
from predict import predict
from moviepy import editor as mp



translator = Translator()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

client = MongoClient("mongodb+srv://tncpl:hackathon@cluster0.otrvhqa.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["School"]
student_collection = db["Students"]
teacher_collection = db["Teachers"]
admin_collection = db["Admin"]


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/student_login')
def student_login():
    return render_template('student_login.html')

@app.route('/faculty_login')
def faculty_login():
    return render_template('faculty_login.html')

@app.route('/admin')
def admin():
    return render_template('admin_login.html')

@app.route('/student_register')
def student_register():
    return render_template('student_register.html')

@app.route('/faculty_register')
def faculty_register():
    return render_template('faculty_register.html')

@app.route('/admin_student_requests')
def admin_student_requests():
    return render_template('admin_student_requests.html')

@app.route('/admin_student_requests_action')
def admin_student_requests_action():
    return render_template('admin_student_requests_action.html')

@app.route('/admin_faculty_requests')
def admin_faculty_requests():
    return render_template('admin_faculty_requests.html')

@app.route('/admin_faculty_requests_action')
def admin_faculty_requests_action():
    return render_template('admin_faculty_requests_action.html')

@app.route('/add_course')
def add_course():
    return render_template('add_course.html')

@app.route('/qna')
def qna():
    return render_template('qna.html')

@app.route('/study_material')
def study_material():
    return render_template('study-material.html')

@app.route('/logout')
def logout():
    return render_template('admin_logout.html')

@app.route('/logout_redirect')
def logout_redirect():
    return render_template('index.html')

@app.route('/faculty_dashboard')
def faculty_dashboard():
    return render_template('faculty_dashboard.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/student_dashboard')
def student_dashboard():
    return render_template('student_dashboard.html')

@app.route('/students')
def students():
    students_1A = student_collection.find({'class': '1A'})
    students_1B = student_collection.find({'class': '1B'})
    students_10A = student_collection.find({'class': '10A'})
    students_10B = student_collection.find({'class': '10B'})
    return render_template('view_student.html', students_1A=students_1A, students_1B=students_1B, students_10A=students_10A, students_10B=students_10B)

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        role = request.args.get('role')
        username = request.form['username']
        password = request.form['password']
        
        if role=="student":
            cred = student_collection.find_one({'username': username})
            session['role']='student'
        elif role=="teacher":
            cred = teacher_collection.find_one({'username': username})
            session['role']='teacher'

        if cred and check_password_hash(cred['password'], password):
            otp = send_email(username)
            session['generated_otp'] = otp
            return render_template('otp.html')
            # if role=="student":
            #     return render_template('student_dashboard.html')
            # if role=="teacher":
            #     return render_template('faculty_dashboard.html')
        else:
            # If username or password is incorrect
            return render_template('index.html')
        
@app.route('/admin_login', methods=['POST'])
def admin_login():
    if request.method == 'POST':
        entered_password = request.form['password']
        admin_data = admin_collection.find_one({'username': 'vasundharaboomi@gmail.com'})
        admin_password = admin_data['password']
        
        if check_password_hash(admin_password, entered_password):
                session['role']='admin'
                otp = send_email('vasundharaboomi@gmail.com')
                session['generated_otp'] = otp
                return render_template('otp.html')
                # return render_template('admin_dashboard.html')
        else:
                return render_template('admin_login.html', error="Invalid password")

def send_email(to_address):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'no.reply.hosschman@gmail.com'  
    smtp_password = 'ywwx wykh gkkk bkkd'

    # Create a connection to the SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)

    # Generate a random 6-digit OTP
    otp = ''.join(random.choices('0123456789', k=6))

    message = MIMEMultipart()
    message['From'] = smtp_username
    message['To'] = to_address
    message['Subject'] = "GUVI Verification Code"
    message.attach(MIMEText(f"The verification code is: {otp}", 'plain'))

    # Send the email
    server.sendmail(smtp_username, to_address, message.as_string())
    print("Email sent successfully.")
    server.quit()
    
    return otp
    
@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    entered_otp = request.form.get('otp')
    generated_otp = session.get('generated_otp')
    _role=session.get('role')
    
    if entered_otp == generated_otp:
        if _role=='student':
            return render_template('student_dashboard.html')
        elif _role=='teacher':
            return render_template('faculty_dashboard.html')
        elif _role=='admin':
            return render_template('admin_dashboard.html')
            
        return jsonify({'success': True, 'message': 'OTP verified successfully'})
    else:
        return jsonify({'success': False, 'message': 'Incorrect OTP'})
    
@app.route('/register_student', methods=['POST'])
def register_student():
    if request.method == 'POST':
        student_data = {
            'id': request.form['roll_no'],
            'name': request.form['name'],
            'username': request.form['email'],
            'DOB': request.form['birthday'],
            'class': request.form['class'],
            'nationality': request.form['nationality'],
            'Score': 0,
            'password': request.form['password']
        }
        dob = datetime.strptime(student_data['DOB'], '%Y-%m-%d')
        student_data['DOB'] = dob
        student_data['password'] = generate_password_hash(student_data['password'])
        student_collection.insert_one(student_data)
        print("success")
        return render_template('admin_dashboard.html')
    
@app.route('/register_faculty', methods=['POST'])
def register_faculty():
    if request.method == 'POST':
        faculty_data = {
            'eid': request.form['roll_no'],
            'name': request.form['name'],
            'username': request.form['email'],
            'DOB': request.form['birthday'],
            'education': request.form['education'],
            'nationality': request.form['nationality'],
            'password': request.form['password']
        }
        dob = datetime.strptime(faculty_data['DOB'], '%Y-%m-%d')
        faculty_data['DOB'] = dob
        faculty_data['password'] = generate_password_hash(faculty_data['password'])
        teacher_collection.insert_one(faculty_data)
        print("success")
        return render_template('admin_dashboard.html')
 
 
# PHYSICAL EXERCISE STARTS HERE
   
mp_pose = mp1.solutions.pose
mp_drawing = mp1.solutions.drawing_utils

show_message = False
counter_left = 0  # Define global variables for counters
counter_right = 0

# Function to calculate the angle between three points
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle 

# Function to stream the video with landmarks and angles displayed
def video_stream():
    global counter_left, counter_right
    cap = cv2.VideoCapture(0)
    counter_left = 0
    counter_right = 0
    stage_left = None
    stage_right = None

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
        
            # Recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            
            # Make detection
            results = pose.process(image)

            # Recolor back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Extract landmarks
            try:
                landmarks = results.pose_landmarks.landmark
                
                # Calculate angles for left arm (similarly for right arm)
                # Left Arm
                left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                angle_left = calculate_angle(left_shoulder, left_elbow, left_wrist)

                # Right Arm
                right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                angle_right = calculate_angle(right_shoulder, right_elbow, right_wrist)

                # Visualize angle for left arm
                cv2.putText(image, f"Left Angle: {angle_left:.2f}", tuple(np.multiply(left_elbow, [640, 480]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                # Visualize angle for right arm
                cv2.putText(image, f"Right Angle: {angle_right:.2f}", tuple(np.multiply(right_elbow, [640, 480]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                # Counter logic for left arm
                
                if angle_left > 160 and stage_left != 'down':
                    stage_left = "down"
                if angle_left < 30 and stage_left == 'down':
                    stage_left = "up"
                    # Increase count value only when all landmarks are visible
                    counter_left += 1
                    if counter_left == 25:
                        counter_left = 0

                # Inside the code block for right arm count
                
                if angle_right > 160 and stage_right != 'down':
                    stage_right = "down"
                if angle_right < 30 and stage_right == 'down':
                    stage_right = "up"
                    # Increase count value only when all landmarks are visible

                    counter_right += 1
                    if counter_right == 25:
                        counter_right = 0


            except:
                pass
            
            # Render counters
            cv2.putText(image, f"Left Count: {counter_left}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, f"Right Count: {counter_right}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            
            # Render detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                    )               
            
            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
    cv2.destroyAllWindows()
        
@app.route('/physical_exercise')
def physical_exercise():
    return render_template('physical_exercise.html')

@app.route('/restart')
def restart():
    return render_template('physical_exercise.html')

@app.route('/get_counts')
def get_counts():
    global counter_left, counter_right
    # Return updated counts as JSON response
    return jsonify({'counter_left': counter_left, 'counter_right': counter_right})

@app.route('/phy_health')
def phy_health():
    global counter_left, counter_right  
    print(counter_left)
    print(counter_right)
    return render_template('physical.html',counter_left=counter_left, counter_right=counter_right)

# Route for video feed
@app.route('/video_feed')
def video_feed():
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

# YOGA STARTS HERE

# Setting up the Pose function
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, model_complexity=1)

def detectPose(image, pose, display=True):
    '''
    This function performs pose detection on an image.
    Args:
        image: The input image with a prominent person whose pose landmarks needs to be detected.
        pose: The pose setup function required to perform the pose detection.
        display: A boolean value that is if set to true the function displays the original input image, the resultant image, 
                and the pose landmarks in 3D plot and returns nothing.
    Returns:
        output_image: The input image with the detected pose landmarks drawn.
        landmarks: A list of detected landmarks converted into their original scale.
    '''
    
    # Create a copy of the input image.
    output_image = image.copy()
    
    # Convert the image from BGR into RGB format.
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Perform the Pose Detection.
    results = pose.process(imageRGB)
    
    # Retrieve the height and width of the input image.
    height, width, _ = image.shape
    
    # Initialize a list to store the detected landmarks.
    landmarks = []
    
    # Check if any landmarks are detected.
    if results.pose_landmarks:
    
        # Draw Pose landmarks on the output image.
        mp_drawing.draw_landmarks(image=output_image, landmark_list=results.pose_landmarks,
                                connections=mp_pose.POSE_CONNECTIONS)
        
        # Iterate over the detected landmarks.
        for landmark in results.pose_landmarks.landmark:
            
            # Append the landmark into the list.
            landmarks.append((int(landmark.x * width), int(landmark.y * height),
                                (landmark.z * width)))
    
    
    return output_image,landmarks


def calculateAngle(landmark1, landmark2, landmark3):
    '''
    This function calculates angle between three different landmarks.
    Args:
        landmark1: The first landmark containing the x,y and z coordinates.
        landmark2: The second landmark containing the x,y and z coordinates.
        landmark3: The third landmark containing the x,y and z coordinates.
    Returns:
        angle: The calculated angle between the three landmarks.

    '''

    # Get the required landmarks coordinates.
    x1, y1, _ = landmark1
    x2, y2, _ = landmark2
    x3, y3, _ = landmark3

    # Calculate the angle between the three points
    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    
    # Check if the angle is less than zero.
    if angle < 0:

        # Add 360 to the found angle.
        angle += 360
    
    # Return the calculated angle.
    return angle


def classifyPose(landmarks, output_image, display=False):
    '''
    This function classifies yoga poses depending upon the angles of various body joints.
    Args:
        landmarks: A list of detected landmarks of the person whose pose needs to be classified.
        output_image: A image of the person with the detected pose landmarks drawn.
        display: A boolean value that is if set to true the function displays the resultant image with the pose label 
        written on it and returns nothing.
    Returns:
        output_image: The image with the detected pose landmarks drawn and pose label written.
        label: The classified pose label of the person in the output_image.

    '''
    
    # Initialize the label of the pose. It is not known at this stage.
    label = 'Unknown Pose'

    # Specify the color (Red) with which the label will be written on the image.
    color = (0, 0, 255)
    
    # Calculate the required angles.
    #----------------------------------------------------------------------------------------------------------------
    
    # Get the angle between the left shoulder, elbow and wrist points. 
    left_elbow_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                                      landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
                                      landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value])
    
    # Get the angle between the right shoulder, elbow and wrist points. 
    right_elbow_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                                       landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value],
                                       landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value])   
    
    # Get the angle between the left elbow, shoulder and hip points. 
    left_shoulder_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value],
                                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value],
                                         landmarks[mp_pose.PoseLandmark.LEFT_HIP.value])

    # Get the angle between the right hip, shoulder and elbow points. 
    right_shoulder_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
                                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value],
                                          landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value])

    # Get the angle between the left hip, knee and ankle points. 
    left_knee_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value],
                                     landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value],
                                     landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value])

    # Get the angle between the right hip, knee and ankle points 
    right_knee_angle = calculateAngle(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value],
                                      landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value],
                                      landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value])
    
    #----------------------------------------------------------------------------------------------------------------
    
    # Check if it is the warrior II pose or the T pose.
    # As for both of them, both arms should be straight and shoulders should be at the specific angle.
    #----------------------------------------------------------------------------------------------------------------
    
    if (165 < left_knee_angle < 195) and (165 < right_knee_angle < 195) \
        and (130 < left_elbow_angle < 180) and (175 < right_elbow_angle < 220) \
        and (100 < left_shoulder_angle < 200) and (50 < right_shoulder_angle < 130):
        
        # Specify the label of the pose as Trikonasana Pose
        label = 'T Pose'
    #----------------------------------------------------------------------------------------------------------------
    
    # Check if the both arms are straight.
    if left_elbow_angle > 165 and left_elbow_angle < 195 and right_elbow_angle > 165 and right_elbow_angle < 195:

        # Check if shoulders are at the required angle.
        if left_shoulder_angle > 80 and left_shoulder_angle < 110 and right_shoulder_angle > 80 and right_shoulder_angle < 110:

    # Check if it is the warrior II pose.
    #----------------------------------------------------------------------------------------------------------------

            # Check if one leg is straight.
            if left_knee_angle > 165 and left_knee_angle < 195 or right_knee_angle > 165 and right_knee_angle < 195:

                # Check if the other leg is bended at the required angle.
                if left_knee_angle > 90 and left_knee_angle < 120 or right_knee_angle > 90 and right_knee_angle < 120:

                    # Specify the label of the pose that is Warrior II pose.
                    label = 'Warrior II Pose' 
                        
    #----------------------------------------------------------------------------------------------------------------
    
    # Check if it is the T pose.
    #----------------------------------------------------------------------------------------------------------------
    
            # Check if both legs are straight
            # if left_knee_angle > 160 and left_knee_angle < 195 and right_knee_angle > 160 and right_knee_angle < 195:

            #     # Specify the label of the pose that is tree pose.
            #     label = 'T Pose'

    #----------------------------------------------------------------------------------------------------------------
    
    # Check if it is the tree pose.
    #----------------------------------------------------------------------------------------------------------------
    
    # Check if one leg is straight
    if left_knee_angle > 165 and left_knee_angle < 195 or right_knee_angle > 165 and right_knee_angle < 195:

        # Check if the other leg is bended at the required angle.
        if left_knee_angle > 315 and left_knee_angle < 335 or right_knee_angle > 25 and right_knee_angle < 45:

            # Specify the label of the pose that is tree pose.
            label = 'Tree Pose'

    #----------------------------------------------------------------------------------------------------------------
    
   
   
    # Check if the pose is classified successfully
    if label != 'Unknown Pose':
        
        # Update the color (to green) with which the label will be written on the image.
        color = (0, 255, 0)  
    
    # Write the label on the output image. 
    cv2.putText(output_image, label, (10, 30),cv2.FONT_HERSHEY_PLAIN, 2, color, 2)
    
    # Check if the resultant image is specified to be displayed.
    if display:
    
        # Display the resultant image.
        plt.figure(figsize=[10,10])
        plt.imshow(output_image[:,:,::-1]);plt.title("Output Image");plt.axis('off');
        
    else:
        
        # Return the output image and the classified label.
        return output_image, label

# Release the VideoCapture object and close the windows
def webcam_feed():
    # Initialize the VideoCapture object to read from the webcam
    camera_video = cv2.VideoCapture(0)
    camera_video.set(3, 1380)
    camera_video.set(4, 960)

    while camera_video.isOpened():
        # Read a frame
        ok, frame = camera_video.read()

        if not ok:
            continue

        # Flip the frame horizontally for natural (selfie-view) visualization
        frame = cv2.flip(frame, 1)

        # Get the width and height of the frame
        frame_height, frame_width, _ = frame.shape

        # Resize the frame while keeping the aspect ratio
        frame = cv2.resize(frame, (int(frame_width * (640 / frame_height)), 640))

        # Perform Pose landmark detection
        frame, landmarks = detectPose(frame, pose, display=False)

        if landmarks:
            # Perform the Pose Classification
            frame, _ = classifyPose(landmarks, frame, display=False)

        # Convert the frame to JPEG format
        ret, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    camera_video.release()
    cv2.destroyAllWindows()

@app.route('/yoga')
def yoga():
    return render_template('yoga.html')

@app.route('/yoga_try')
def yoga_try():
    return render_template('yoga_try.html')

@app.route('/video_feed1')
def video_feed1():
    return Response(webcam_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')


#COURSES

# Initialize NLTK stopwords
nltk.download('punkt')
nltk.download('stopwords')
stop_words = set(stopwords.words("english"))

# Sample data for courses
courses = [
    {
        "title": "Environmental Science",
        "description": "Through fun activities and interactive lessons, children will explore basic concepts like plants, animals, fostering a love for nature and a sense of environmental responsibility from an early age.",
        "standard": "I",
        "modules": [
            {
                "title": "Living and Non Living Things",
                "video_link": "video/module1.mp4",
                "pdf_link": "static/pdf/EVS-1-Chap1.pdf",
                "summary_link": "The text from www.tntextbooks.in focuses on educating children about animals, particularly insects, birds, and mammals, while also promoting an awareness of animal protection. It encourages children to observe, name, identify, describe, compare, and classify animals into these categories. The text includes various activities and discussions about animals, their body parts, behavior, and habitats. It also emphasizes the importance of caring for animals and includes fun activities like solving riddles, making paper plate masks, and acting like animals. Overall, the text aims to develop children's understanding and appreciation of the animal kingdom.",
                "test_link": "drag_drop.html"
            },
            {
                "title": "My Wonderful Body",
                "video_link": "video/module2.mp4",
                "pdf_link": "static/pdf/EVS-1-Chap2.pdf",
                "summary_link": "summary/module2_summary.pdf",
                "test_link": "cam_hygiene.html"
            },
            {
                "title": "Nature's Bounty",
                "video_link": "video/module2.mp4",
                "pdf_link": "pdf/EVS-1-Chap3.pdf",
                "summary_link": "summary/module2_summary.pdf",
                "test_link": "comprehension_check.html"
            },
            {
                "title": "Animals Around Us",
                "video_link": "video/module2.mp4",
                "pdf_link": "pdf/EVS-1-Chap4.pdf",
                "summary_link": "summary/module2_summary.pdf",
                "test_link": "test/module2_test.pdf"
            }
            # Add more modules as needed
        ],
    },
    {
        "title": "Biology",
        "description": "Explore the complexities of life, from cellular structures to ecosystems, and delve into topics such as genetics, evolution, and human biology. Students will gain a deeper understanding of the living world around them.",
        "standard": "X",
        "modules": [
            {
                "title": "Module 1",
                "video_link": "video_link_2",
                "pdf_link": "pdf_link_2",
                "summary_link": "summary_link_2",
                "test_link": "test_link_2"
            },
            {
                "title": "Module 2",
                "video_link": "video_link_2",
                "pdf_link": "pdf_link_2",
                "summary_link": "summary_link_2",
                "test_link": "test_link_2"
            }
            # Add more modules as needed
        ],
    }
]

@app.route('/student_study')
def student_study():
    return render_template('student_study.html', courses=courses)

@app.route('/sign_learn')
def sign_learn():
    return render_template('sign_learn.html')

@app.route('/course/<int:course_id>')
def course(course_id):
    course = courses[course_id]
    return render_template('course.html', course=course, course_id=course_id)

@app.route('/translate', methods=['POST'])
def translate():
    text = request.form['text']
    lang = request.form['lang']
    translated_text = translator.translate(text, dest=lang).text
    return translated_text

@app.route('/video/<int:course_id>')
def video(course_id):
    module_id = request.args.get('module_id', default=0, type=int)
    course = courses[course_id]
    module = course['modules'][module_id]
    languages = LANGUAGES
    return render_template('video.html', course=course, module=module, languages=languages, course_id=course_id, module_id=module_id)

@app.route('/quiz/<int:course_id>/<int:module_id>')
def quiz(course_id, module_id):
    course = courses[course_id]
    module = course['modules'][module_id]
    return render_template(module['test_link'])

@app.route('/transcribe/<int:course_id>/<int:module_id>', methods=['POST'])
def transcribe(course_id, module_id):
    lang = request.form['lang']
    course = courses[course_id]
    module = course['modules'][module_id]
    video_path = os.path.join("static", module["video_link"])
    try:
        # Load the video
        video = mp.VideoFileClip(video_path)
        # Extract the audio from the video
        audio_file = video.audio
        audio_file.write_audiofile("notes.wav")
        # Initialize recognizer
        r = sr.Recognizer()
        # Load the audio file
        with sr.AudioFile("notes.wav") as source:
            data = r.record(source)
        # Convert speech to text
        transcript = r.recognize_google(data, language="en")
        # Translate the transcribed text (new section)
        translator = Translator()
        translated_transcript = translator.translate(transcript, dest=lang).text  # Replace 'ta' with the target language code  
    except Exception as e:
        # Handle any errors that occur
        translated_transcript = "Error: " + str(e)
    finally:
        # Clean up the audio file
        if 'audio_file' in locals():
            audio_file.close()    
    return render_template('video.html', course=course, module=module, languages=LANGUAGES, course_id=course_id, module_id=module_id, transcript=translated_transcript)
    
@app.route('/summary_pdf/<int:course_id>/<int:module_id>', methods=['GET', 'POST'])
def summary_pdf(course_id, module_id):
    course = courses[course_id]
    module = course['modules'][module_id]
    pdf_path = module['pdf_link']
    lang = request.args.get('lang', 'en')  # Get the selected language or default to English
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    
    # Summarize the extracted text
    summary = summarize_text(text)
    languages = LANGUAGES
    translator = Translator()
    translated_transcript = translator.translate(summary, dest=lang).text
    return render_template('summary.html', summary=translated_transcript, course_id=course_id, module_id=module_id, languages=LANGUAGES)

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def summarize_text(text):
    stopWords = set(stopwords.words("english")) 
    # Tokenize the text
    words = word_tokenize(text)
    
    # Create a frequency table
    freq_table = {}
    for word in words:
        if word in stopWords:
            continue
        if word in freq_table:
            freq_table[word] += 1
        else:
            freq_table[word] = 1

    # Calculate sentence scores
    sentences = sent_tokenize(text)
    sentence_scores = {}
    for sentence in sentences:
        if re.search(r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b', sentence) or re.search(r'SKYATLAS', sentence):
            continue  # Skip sentences with dates
        for word, freq in freq_table.items():
            if word in sentence.lower():
                if sentence in sentence_scores:
                    sentence_scores[sentence] += freq
                else:
                    sentence_scores[sentence] = freq

    # Calculate the average sentence score
    sum_scores = sum(sentence_scores.values())
    avg_score = sum_scores / len(sentence_scores)

    # Generate the summary
    summary = "\n".join([sentence.replace("", " ").replace("◊", " ") + "\n" for sentence, score in sentence_scores.items() if score > (1.2 * avg_score)])
    return summary

#IMAGE DESCRIPTION
@app.route('/image_des_home')
def image_des_home():
    return render_template('image_des_home.html')

@app.route('/results', methods=['POST'])
def results():
    form = request.form
    if request.method == 'POST':
        myfile = request.files['myfile']
        predicted_desc = predict(myfile).replace('start ','').replace('end','')
        del myfile
        return predicted_desc


@app.route('/refresh')
def refresh():
    return render_template('image_des_body.html')
if __name__ == '__main__':
    app.run(debug=True)