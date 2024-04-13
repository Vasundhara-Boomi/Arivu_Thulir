import pymongo
from werkzeug.security import generate_password_hash
from datetime import datetime


client = pymongo.MongoClient("mongodb+srv://tncpl:hackathon@cluster0.otrvhqa.mongodb.net/")
db = client["School"]
teacher_collection = db["Teachers"]
teacher_collection.delete_many({})

def insert_teacher(data):
    dob = datetime.strptime(data['DOB'], '%Y-%m-%d')
    data['DOB'] = dob
    data['password'] = generate_password_hash(data['password'])
    teacher_collection.insert_one(data)

teacher_data = [
    {
        'eid': 1,
        'name': 'Meera M',
        'username':'vasundharaboomi@gmail.com',
        'DOB': '1988-09-15',
        'education': 'BSc, PhD',
        'nationality': 'Indian',
        'password': '1234'
    },
    {
        'eid': 2,
        'name': 'Arnav K',
        'username':'lmn@gmail.com',
        'DOB': '1983-11-27',
        'education': 'BE, MTech',
        'nationality': 'Indian',
        'password': '7893'
    }
]


for i in teacher_data:
    insert_teacher(i)