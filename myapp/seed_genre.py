from .mongo import genre_collection

genres = [
    {"name": "Action", "slug": "action"},
    {"name": "Fantasy", "slug": "fantasy"},
    {"name": "Romance", "slug": "romance"},
    {"name": "Supernatural", "slug": "supernatural"},
]

genre_collection.insert_many(genres)
print("Genres inserted")
