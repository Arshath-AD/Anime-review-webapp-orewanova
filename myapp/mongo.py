from pymongo import MongoClient
import os

MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb://localhost:27017/"
)

client = MongoClient(MONGO_URI)
db = client["anime_review"]

anime_collection = db["anime"]
genre_collection = db["genre"]
activity_collection = db["user_activity"]
admin_activity_collection = db["admin_activity"]
ratings_collection = db["ratings"]
comments_collection = db["comments"]
