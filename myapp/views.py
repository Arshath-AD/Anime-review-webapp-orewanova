from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from bson import ObjectId
from .mongo import anime_collection, genre_collection, activity_collection

from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.utils.text import slugify
import os

@staff_member_required
def admin_dashboard(request):
    return render(request, "myapp/admin/dashboard.html")

@staff_member_required
def add_anime(request):
    genres = list(genre_collection.find())

    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]

        new_genre = request.POST.get("new_genre")
        if new_genre:
            slug = slugify(new_genre)
            genre_collection.insert_one({
                "name": new_genre.title(),
                "slug": slug
            })
            genre = slug
        else:
            genre = request.POST["genre"]

        image = request.FILES["image"]
        image_name = slugify(title) + os.path.splitext(image.name)[1]
        image_path = f"anime/thumbnails/{genre}/{image_name}"

        default_storage.save(image_path, image)

        anime_collection.insert_one({
            "title": title,
            "description": description,
            "genre": genre,
            "image_path": image_path
        })

        return redirect("admin_dashboard")

    return render(request, "myapp/admin/add_anime.html", {
        "genres": genres
    })

@staff_member_required
def admin_anime_list(request):
    anime = list(anime_collection.find())
    for a in anime:
        a["id"] = str(a["_id"])
    return render(request, "myapp/admin/anime_list.html", {"anime": anime})

@staff_member_required
def edit_anime(request, anime_id):
    anime = anime_collection.find_one({"_id": ObjectId(anime_id)})

    if request.method == "POST":
        anime_collection.update_one(
            {"_id": ObjectId(anime_id)},
            {"$set": {
                "title": request.POST["title"],
                "description": request.POST["description"],
                "genre": request.POST["genre"]
            }}
        )
        return redirect("admin_anime_list")

    anime["id"] = str(anime["_id"])
    return render(request, "myapp/admin/edit_anime.html", {"anime": anime})

@staff_member_required
def delete_anime(request, anime_id):
    anime_collection.delete_one({"_id": ObjectId(anime_id)})
    return redirect("admin_anime_list")


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
