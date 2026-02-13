Orewa Nova – Anime Review Web App

A full-stack anime discovery and review platform built with Django and MongoDB.

📌 Overview

Orewa Nova is a modern anime exploration platform where users can:

Browse anime by genre

View detailed anime pages

Explore image galleries with sliders

Manage profiles

Administer content through a custom admin dashboard

The project combines Django (auth + media handling) with MongoDB (content storage).

🧱 Tech Stack
Layer	Technology
Backend	Django 6
Database	MongoDB (anime data) + SQLite (auth)
Frontend	HTML5, CSS3, JavaScript
UI Library	Glide.js
Media	Django File Storage
✨ Features
🎨 UI & Experience

Dark modern theme

Hero image section on anime detail page

Portrait & landscape thumbnails

Responsive card grid

Animated hover effects

Glide.js image gallery slider

Genre-based browsing

Short summary + detailed description system

👤 Authentication & Profiles

User Signup/Login

Profile Page

Profile Picture Upload

Default Avatar System

Staff-based Admin Access

🛠 Admin Panel

Add / Edit / Delete Anime

Multi-genre support

Upload:

Landscape thumbnail

Portrait thumbnail

Multiple gallery slides

Media auto-organized:

media/
 └── anime/
      ├── thumbnails/
      │    ├── landscapes/
      │    └── portraits/
      └── slidesimg/<anime_id>/

🗂 Project Structure
orewa_nova/
│
├── myapp/
│   ├── templates/
│   ├── static/
│   ├── views.py
│   ├── models.py
│   └── mongo.py
│
├── media/
├── manage.py
├── requirements.txt
└── README.md

⚙️ Installation
1️⃣ Clone
git clone https://github.com/yourusername/anime-review-webapp-orewanova.git
cd anime-review-webapp-orewanova

2️⃣ Create Virtual Environment
python -m venv env
source env/bin/activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run Migrations
python manage.py migrate

5️⃣ Start Server
python manage.py runserver


Open:

http://127.0.0.1:8000/

🔄 Current Development Focus

⭐ Rating system

💬 Comments system

🔎 Search functionality

📊 Recommendation improvements

👨‍💻 Author

Arshath AD
BSc Computer Science
Full-Stack Developer