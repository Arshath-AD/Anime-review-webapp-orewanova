import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from bson import ObjectId
from .mongo import anime_collection, genre_collection, activity_collection, admin_activity_collection, ratings_collection, comments_collection

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.core.files.storage import default_storage
from django.contrib import messages
from django.utils.text import slugify
from .models import Profile
import os
from datetime import datetime
from django.utils.text import slugify

from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone

from collections import OrderedDict

ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]

@staff_member_required
def admin_dashboard(request):
    total_anime = anime_collection.count_documents({})
    total_genres = genre_collection.count_documents({})
    total_users = User.objects.count()

    # Count total slides
    animes = list(anime_collection.find().sort("_id", -1).limit(5))
    total_slides = sum(len(a.get("slides", [])) for a in animes)

    # Build activity feed
    activity = list(
        admin_activity_collection.find()
        .sort("timestamp", -1)
        .limit(8)
    )

    # Latest users
    latest_users = User.objects.order_by("-date_joined")[:3]
    for user in latest_users:
        activity.append({
            "type": "user",
            "message": f"New user registered: {user.username}"
        })

    return render(request, "myapp/admin/dashboard.html", {
        "total_anime": total_anime,
        "total_genres": total_genres,
        "total_users": total_users,
        "total_slides": total_slides,
        "activity": activity[:6],  # limit feed
    })

@staff_member_required
def manage_content(request):
    anime_list = list(anime_collection.find().sort("_id", -1))
    query = request.GET.get("q", "").strip()

    if query:
        anime = search_anime(query)
    else:
        anime = list(anime_collection.find())

    for a in anime:
        a["id"] = str(a["_id"])

    for a in anime_list:
        a["id"] = str(a["_id"])

    return render(request, "myapp/admin/manage_content.html", {
        "anime_list": anime_list,
        "anime": anime,
        "query": query
    })

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
        
        # insert activity
        admin_activity_collection.insert_one({
            "action": "CREATE",
            "entity": "ANIME",
            "title": title,
            "admin": request.user.username,
            "timestamp": datetime.utcnow()
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

        admin_activity_collection.insert_one({
            "action": "UPDATE",
            "entity": "ANIME",
            "anime_id": anime_id,
            "title": title,
            "admin": request.user.username,
            "timestamp": datetime.utcnow()
        })

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
    anime = anime_collection.find_one({"_id": ObjectId(anime_id)})

    if not anime:
        return redirect("admin_anime_list")

    # Store title before deletion
    title = anime.get("title", "Unknown")

    # Delete anime
    anime_collection.delete_one({"_id": ObjectId(anime_id)})

    # Log activity
    admin_activity_collection.insert_one({
        "action": "DELETE",
        "entity": "ANIME",
        "anime_id": anime_id,
        "title": title,
        "admin": request.user.username,
        "timestamp": datetime.utcnow()
    })

    return redirect("admin_anime_list")

@staff_member_required
def manage_users(request):
    query = request.GET.get("q", "")
    
    users = User.objects.all().order_by("-date_joined")

    if query:
        users = users.filter(
            username__icontains=query
        ) | users.filter(
            email__icontains=query
        )

    return render(request, "myapp/admin/manage_users.html", {
        "users": users,
        "query": query
    })


@staff_member_required
def toggle_admin(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user == request.user:
        messages.error(request, "You cannot modify your own admin status.")
        return redirect("manage_users")

    user.is_staff = not user.is_staff
    user.save()

    messages.success(request, f"{user.username} admin status updated.")
    return redirect("manage_users")


@staff_member_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user == request.user:
        messages.error(request, "You cannot delete yourself.")
        return redirect("manage_users")

    if user.is_superuser:
        messages.error(request, "You cannot delete a superuser.")
        return redirect("manage_users")

    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect("manage_users")


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
    query = request.GET.get("q", "").strip()

    if query:
        anime = list(anime_collection.find({
            "title": {"$regex": query, "$options": "i"}
        }))
    else:
        anime = list(anime_collection.find())

    for a in anime:
        a["id"] = str(a["_id"])

    genres = list(genre_collection.find())
    genre_rows = OrderedDict()

    featured = list(
        anime_collection.find().sort("_id", -1).limit(5)
    )

    for a in featured:
        a["id"] = str(a["_id"])

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
        "recent_anime": recent_anime,
        "featured": featured,
        "query": query
    })

def serialize_anime(anime):
    anime["id"] = str(anime["_id"])
    return anime

def genre_list(request):
    query = request.GET.get("q", "").strip()

    if query:
        genres = list(
            genre_collection.find({
                "name": {"$regex": query, "$options": "i"}
            })
        )
    else:
        genres = list(genre_collection.find())

    return render(request, "myapp/genre_list.html", {
        "genres": genres,
        "query": query
    })



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
        return redirect("/")

    anime["id"] = str(anime["_id"])

    # === Slides Loader ===
    if not anime.get("slides"):
        slides_dir = os.path.join(settings.MEDIA_ROOT, "anime", "slidesimg", anime_id)
        found_slides = []

        if os.path.exists(slides_dir):
            for filename in sorted(os.listdir(slides_dir)):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                    found_slides.append(f"anime/slidesimg/{anime_id}/{filename}")

        anime["slides"] = found_slides

    # === Activity Tracking (Session Safe) ===
    if request.user.is_authenticated:
        viewed_key = f"viewed_{anime_id}"

        if not request.session.get(viewed_key):
            genres = anime.get("genres", [])
            for g in genres:
                activity_collection.insert_one({
                    "user_id": request.user.id,
                    "genre": g
                })
            request.session[viewed_key] = True

    # === Rating Aggregation ===
    pipeline = [
        {"$match": {"anime_id": ObjectId(anime_id)}},
        {
            "$group": {
                "_id": None,
                "avg_rating": {"$avg": "$rating"},
                "total": {"$sum": 1}
            }
        }
    ]

    result = list(ratings_collection.aggregate(pipeline))

    user_rating = 0

    if request.user.is_authenticated:
        existing = ratings_collection.find_one({
            "user_id": request.user.id,
            "anime_id": ObjectId(anime_id)
        })

        if existing:
            user_rating = existing["rating"]

    anime["user_rating"] = user_rating

    anime["avg_rating"] = round(result[0]["avg_rating"], 1) if result else 0
    anime["total_ratings"] = result[0]["total"] if result else 0

    comments = list(
        comments_collection.find({"anime_id": ObjectId(anime_id)})
        .sort("created_at", -1)
    )

    anime["comments"] = comments

    return render(request, "myapp/anime_detail.html", {
        "anime": anime,
        "comments": comments
    })


# rating method
@login_required
def rate_anime(request, anime_id):
    if request.method == "POST":
        rating_value = int(request.POST.get("rating"))

        if rating_value < 1 or rating_value > 5:
            return redirect("anime_detail", anime_id=anime_id)

        ratings_collection.update_one(
            {
                "user_id": request.user.id,
                "anime_id": ObjectId(anime_id)
            },
            {
                "$set": {
                    "rating": rating_value,
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )

    return redirect("anime_detail", anime_id=anime_id)

# AJAX rating endpoint

@login_required
def rate_anime(request, anime_id):
    if request.method == "POST":
        rating_value = int(request.POST.get("rating"))

        if rating_value < 1 or rating_value > 5:
            return JsonResponse({"error": "Invalid rating"}, status=400)

        ratings_collection.update_one(
            {
                "user_id": request.user.id,
                "anime_id": ObjectId(anime_id)
            },
            {
                "$set": {
                    "rating": rating_value,
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )

        # Recalculate average
        pipeline = [
            {"$match": {"anime_id": ObjectId(anime_id)}},
            {
                "$group": {
                    "_id": None,
                    "avg_rating": {"$avg": "$rating"},
                    "total": {"$sum": 1}
                }
            }
        ]

        result = list(ratings_collection.aggregate(pipeline))

        avg = round(result[0]["avg_rating"], 1) if result else 0
        total = result[0]["total"] if result else 0

        return JsonResponse({
            "avg_rating": avg,
            "total_ratings": total
        })

@login_required
def add_comment(request, anime_id):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    text = request.POST.get("comment", "").strip()

    if not text:
        return JsonResponse({"error": "Empty comment"}, status=400)

    comment = {
        "anime_id": ObjectId(anime_id),
        "user_id": request.user.id,
        "username": request.user.username,
        "text": text,
        "created_at": timezone.now()
    }

    comments_collection.insert_one(comment)

    return JsonResponse({
        "username": request.user.username,
        "text": text
    })

# AJAX search 
def search_api(request):
    query = request.GET.get("q", "")

    if not query:
        return JsonResponse({"results": []})

    results = list(anime_collection.find(
        {"title": {"$regex": query, "$options": "i"}},
        {"title": 1, "images.landscape": 1}
    ).limit(5))

    data = []
    for a in results:
        data.append({
            "id": str(a["_id"]),
            "title": a["title"],
            "image": a.get("images", {}).get("landscape", "")
        })

    return JsonResponse({"results": data})

def search_genre(request):
    query = request.GET.get("q", "").strip()
    results = []

    if query:
        genres = genre_collection.find({
            "name": {"$regex": query, "$options": "i"}
        })

        for g in genres:
            results.append({
                "name": g["name"],
                "slug": slugify(g["name"])
            })

    return JsonResponse({"results": results})