import pymongo
from werkzeug.security import generate_password_hash
from datetime import datetime


client = pymongo.MongoClient("mongodb+srv://tncpl:hackathon@cluster0.otrvhqa.mongodb.net/")
db = client["School"]
student_collection = db["Students"]
student_collection.delete_many({})

def insert_student(data):
    dob = datetime.strptime(data['DOB'], '%Y-%m-%d')
    data['DOB'] = dob
    data['password'] = generate_password_hash(data['password'])
    student_collection.insert_one(data)

student_data = [
    {
        'id': 1,
        'name': 'Vasundhara',
        'username':'vasundhara2110257@ssn.edu.in',
        'DOB': '2007-07-03',
        'class': '12A',
        'nationality': 'Indian',
        'Score': 0,
        'password': '2309'
    },
    {
        'id': 2,
        'name': 'Selcia',
        'username':'selcia2110605@ssn.edu.in',
        'DOB': '2007-10-06',
        'class': "12A",
        'nationality': 'Indian',
        'score': 0,
        'password': '1973'
    },
    {
        'id': 3,
        'name': 'Rajat Verma',
        'username':'xyz@gmail.com',
        'DOB': '2007-12-10',
        'class': '12A',
        'nationality': 'Indian',
        'score': 0,
        'password': '1893'
    },
    {
        'id': 4,
        'name': 'Sanya D',
        'username':'abc@gmail.com',
        'DOB': '2007-05-07',
        'class': "12A",
        'nationality': 'Indian',
        'score': 0,
        'password': '4829'
    },
    {
        'id': 5,
        'name': 'Akshay P',
        'username':'pqr@gmail.com',
        'DOB': '2007-03-07',
        'class': '12A',
        'nationality': 'Indian',
        'score': 0,
        'password': '7389'
    }
]


for i in student_data:
    insert_student(i)