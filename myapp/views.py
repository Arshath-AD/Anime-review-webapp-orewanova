import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from bson import ObjectId
from .mongo import anime_collection, genre_collection, activity_collection

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core.files.storage import default_storage
from django.contrib import messages
from django.utils.text import slugify
from .models import Profile
import os

from collections import OrderedDict

ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]

@staff_member_required
def admin_dashboard(request):
    return render(request, "myapp/admin/dashboard.html")

@staff_member_required
def add_anime(request):
    genres = list(genre_collection.find())

    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        genres_selected = request.POST.getlist("genres")

        new_genre = request.POST.get("new_genre")
        if new_genre:
            slug = slugify(new_genre)
            if not genre_collection.find_one({"slug": slug}):
                genre_collection.insert_one({
                    "name": new_genre.title(),
                    "slug": slug
                })
            genres_selected.append(slug)

        if not genres_selected:
            return render(request, "myapp/admin/add_anime.html", {
                "genres": genres,
                "error": "Select at least one genre"
            })

        # ===== LANDSCAPE + PORTRAIT =====
        landscape_image = request.FILES["landscape_image"]
        portrait_image = request.FILES["portrait_image"]

        ext_land = os.path.splitext(landscape_image.name)[1].lower()
        ext_port = os.path.splitext(portrait_image.name)[1].lower()

        if ext_land not in ALLOWED_IMAGE_EXTENSIONS:
            return render(request, "myapp/admin/add_anime.html", {
                "genres": genres,
                "error": "Landscape image must be JPG or PNG"
            })

        if ext_port not in ALLOWED_IMAGE_EXTENSIONS:
            return render(request, "myapp/admin/add_anime.html", {
                "genres": genres,
                "error": "Portrait image must be JPG or PNG"
            })

        image_base_name = slugify(title)

        landscape_path = f"anime/thumbnails/landscapes/{image_base_name}{ext_land}"
        portrait_path = f"anime/thumbnails/portraits/{image_base_name}{ext_port}"

        default_storage.save(landscape_path, landscape_image)
        default_storage.save(portrait_path, portrait_image)

        summary = request.POST["summary"]

        # ===== INSERT ANIME FIRST =====
        result = anime_collection.insert_one({
            "title": title,
            "description": description,
            "genres": genres_selected,
            "images": {
                "landscape": landscape_path,
                "portrait": portrait_path
            }
        })

        anime_id = str(result.inserted_id)

        # ===== HANDLE SLIDES =====
        slides = request.FILES.getlist("slides")
        slide_paths = []

        for index, slide in enumerate(slides):
            ext_slide = os.path.splitext(slide.name)[1].lower()

            if ext_slide not in ALLOWED_IMAGE_EXTENSIONS:
                continue  # skip invalid files

            slide_path = f"anime/slidesimg/{anime_id}/{index+1}{ext_slide}"
            default_storage.save(slide_path, slide)
            slide_paths.append(slide_path)

        # ===== UPDATE DOCUMENT WITH SLIDES =====
        anime_collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {"slides": slide_paths}}
        )

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

    if not anime:
        return redirect("admin_anime_list")

    if request.method == "POST":
        title = request.POST["title"]
        summary = request.POST["summary"]   
        description = request.POST["description"]
        genres_selected = request.POST.getlist("genres")

        update_data = {
            "title": title,
            "summary": summary,                
            "description": description,
            "genres": genres_selected
        }

        image_base_name = slugify(title)

        # ===== OPTIONAL THUMBNAIL UPDATE =====
        landscape_image = request.FILES.get("landscape_image")
        portrait_image = request.FILES.get("portrait_image")

        if landscape_image:
            ext = os.path.splitext(landscape_image.name)[1].lower()
            landscape_path = f"anime/thumbnails/landscapes/{image_base_name}{ext}"
            default_storage.save(landscape_path, landscape_image)
            update_data["images.landscape"] = landscape_path

        if portrait_image:
            ext = os.path.splitext(portrait_image.name)[1].lower()
            portrait_path = f"anime/thumbnails/portraits/{image_base_name}{ext}"
            default_storage.save(portrait_path, portrait_image)
            update_data["images.portrait"] = portrait_path

        # ===== OPTIONAL NEW SLIDES =====
        slides = request.FILES.getlist("slides")
        if slides:
            slide_paths = []
            for index, slide in enumerate(slides):
                ext = os.path.splitext(slide.name)[1].lower()
                slide_path = f"anime/slidesimg/{anime_id}/{index+1}{ext}"
                default_storage.save(slide_path, slide)
                slide_paths.append(slide_path)

            update_data["slides"] = slide_paths

        anime_collection.update_one(
            {"_id": ObjectId(anime_id)},
            {"$set": update_data}
        )

        return redirect("admin_anime_list")

    anime["id"] = str(anime["_id"])

    # 🛡 Backward safety for old anime without summary
    if "summary" not in anime:
        anime["summary"] = ""

    genres = list(genre_collection.find())

    return render(request, "myapp/admin/edit_anime.html", {
        "anime": anime,
        "genres": genres
    })



@staff_member_required
def delete_anime(request, anime_id):
    anime_collection.delete_one({"_id": ObjectId(anime_id)})
    return redirect("admin_anime_list")


#auth & authentication
def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        # Profile is created automatically via signal
        login(request, user)
        return redirect("home")

    return render(request, "myapp/auth/signup.html")

@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        image = request.FILES.get("image")
        if image:
            profile.image = image
            profile.save()
        return redirect("profile")

    return render(request, "myapp/profile.html")


#others
def home(request):
    anime = list(anime_collection.find())
    for a in anime:
        a["id"] = str(a["_id"])

    genres = list(genre_collection.find())
    genre_rows = OrderedDict()

    if request.user.is_authenticated:
        pipeline = [
            {"$match": {"user_id": request.user.id}},
            {"$group": {"_id": "$genre", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_genres = list(activity_collection.aggregate(pipeline))

        # 🔑 FALLBACK IF NO ACTIVITY YET
        if top_genres:
            genre_slugs = [g["_id"] for g in top_genres]
        else:
            genre_slugs = [g["slug"] for g in genres[:5]]

    else:
        genre_slugs = [g["slug"] for g in genres[:5]]

    for slug in genre_slugs:
        anime_list = list(
            anime_collection.find({"genres": slug}).limit(10)
        )

        for a in anime_list:
            a["id"] = str(a["_id"])

        if anime_list:
            genre_rows[slug] = anime_list
    
    recent_anime = list(
        anime_collection.find().sort("_id", -1).limit(10)
    )

    for a in recent_anime:
        a["id"] = str(a["_id"])

    return render(request, "myapp/home.html", {
        "anime": anime,
        "genres": genres,
        "genre_rows": genre_rows,
        "recent_anime": recent_anime
    })

def serialize_anime(anime):
    anime["id"] = str(anime["_id"])
    return anime

def genre_page(request, slug):
    anime = list(anime_collection.find({"genres": slug}))
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
    if not anime:
        return redirect("/") # Handle missing anime

    anime["id"] = str(anime["_id"])

    # === DYNAMIC SLIDES LOADER ===
    # Check DB first, if empty, scan disk
    db_slides = anime.get("slides", [])
    if not db_slides: 
        slides_dir = os.path.join(settings.MEDIA_ROOT, 'anime', 'slidesimg', anime_id)
        found_slides = []
        
        if os.path.exists(slides_dir):
            for filename in sorted(os.listdir(slides_dir)):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    found_slides.append(f"anime/slidesimg/{anime_id}/{filename}")
        
        if found_slides:
            anime["slides"] = found_slides

    print(f"DEBUG: Anime ID: {anime_id}")
    print(f"DEBUG: Slides in context: {anime.get('slides')}")

    if request.user.is_authenticated:
        # Check if genres is a list or string before iterating
        genres = anime.get("genres", [])
        if isinstance(genres, list):
             for g in genres:
                activity_collection.insert_one({
                    "user_id": request.user.id,
                    "genre": g
                })

    return render(request, "myapp/anime_detail.html", {
        "anime": anime
    })
