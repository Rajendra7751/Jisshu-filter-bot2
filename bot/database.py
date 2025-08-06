import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI")
mongo = MongoClient(MONGO_URI)
db = mongo.get_default_database()

def set_thumb(user_id, file_id):
    db.thumbs.update_one({"user": user_id}, {"$set": {"thumb": file_id}}, upsert=True)

def get_thumb(user_id):
    data = db.thumbs.find_one({"user": user_id})
    return data["thumb"] if data else None

def del_thumb(user_id):
    db.thumbs.delete_one({"user": user_id})
