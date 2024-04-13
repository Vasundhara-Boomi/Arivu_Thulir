import pymongo
from werkzeug.security import generate_password_hash
from datetime import datetime


client = pymongo.MongoClient("mongodb+srv://tncpl:hackathon@cluster0.otrvhqa.mongodb.net/")
db = client["School"]
admin_collection = db["Admin"]
admin_collection.delete_many({})

def insert_admin(data):
    data['password'] = generate_password_hash(data['password'])
    admin_collection.insert_one(data)

admin_data = [
    {
        'username':'vasundharaboomi@gmail.com',
        'password': '2345'
    }
]

for i in admin_data:
    insert_admin(i)