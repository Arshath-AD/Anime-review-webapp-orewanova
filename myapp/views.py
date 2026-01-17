from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from bson import ObjectId
from .mongo import anime_collection, genre_collection, activity_collection

#auth & authentication
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "myapp/auth/signup.html", {"form": form})

def profile(request):
    return render(request, 'profile.html')


#others
def home(request):
    anime = list(anime_collection.find())
    genres = list(genre_collection.find())

    for a in anime:
        a["id"] = str(a["_id"])   # 👈 convert _id → id (SAFE)

    recommendations = []

    if request.user.is_authenticated:
        pipeline = [
            {"$match": {"user_id": request.user.id}},
            {"$group": {"_id": "$genre", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ]
        top_genre = list(activity_collection.aggregate(pipeline))

        if top_genre:
            recommendations = list(
                anime_collection.find({"genre": top_genre[0]["_id"]}).limit(3)
            )
            for r in recommendations:
                r["id"] = str(r["_id"])

    return render(request, "myapp/home.html", {
        "anime": anime,
        "genres": genres,
        "recommendations": recommendations
    })

def genre_page(request, slug):
    anime = list(anime_collection.find({"genre": slug}))
    genres = list(genre_collection.find())

    for a in anime:
        a["id"] = str(a["_id"])

    return render(request, "myapp/genre.html", {
        "anime": anime,
        "genres": genres,
        "current_genre": slug
    })

def anime_detail(request, anime_id):
    anime = anime_collection.find_one({"_id": ObjectId(anime_id)})
    anime["id"] = str(anime["_id"])

    if request.user.is_authenticated:
        activity_collection.insert_one({
            "user_id": request.user.id,
            "genre": anime["genre"]
        })

    return render(request, "myapp/anime_detail.html", {
        "anime": anime
    })
