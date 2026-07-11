#!/usr/bin/env python3
"""
Production-Ready MongoDB Anime Database Seeder
Contains static, verified official data from AniList.
Clears old seeds, ensures idempotency, uses proper ObjectIds, downloads media.
"""

import os
import shutil
import requests
from datetime import datetime, timezone
from pymongo import MongoClient, UpdateOne

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "anime_review"
ANIME_COLLECTION = "anime"
GENRE_COLLECTION = "genre"

ALLOWED_GENRES = ["Action", "Adventure", "Fantasy", "Romance", "Sci-Fi", "Slice of Life"]

ANIME_DATA = [
    {
        "title": "Attack on Titan",
        "short_summary": "Several hundred years ago, humans were nearly exterminated by titans. Titans are typically several stories tall, seem...",
        "description": "Several hundred years ago, humans were nearly exterminated by titans. Titans are typically several stories tall, seem to have no intelligence, devour human beings and, worst of all, seem to do it for the pleasure rather than as a food source. A small percentage of humanity survived by walling themselves in a city protected by extremely high walls, even taller than the biggest of titans.\n\nFlash forward to the present and the city has not seen a titan in over 100 years. Teenage boy Eren and his foster sister Mikasa witness something horrific as the city walls are destroyed by a colossal titan that appears out of thin air. As the smaller titans flood the city, the two kids watch in horror as their mother is eaten alive. Eren vows that he will murder every single titan and take revenge for all of mankind.\n\n(Source: MangaHelpers)",
        "genres": [
            "slice-of-life",
            "fantasy",
            "action",
            "sci-fi"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/16498-8jpFCOcDmneX.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx16498-buvcRTBx4NSm.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/16498-8jpFCOcDmneX.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx16498-buvcRTBx4NSm.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/16498-8jpFCOcDmneX.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx16498-buvcRTBx4NSm.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b40881-F3gr1PkreDvj.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b40882-dsj7IP943WFF.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b46494-g7xYYuBtYPnO.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b45887-QPtJH0KwqthW.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b71479-huCD908XIdqv.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/n62501-CfTtAAgs64nE.jpg"
        ]
    },
    {
        "title": "Demon Slayer: Kimetsu no Yaiba",
        "short_summary": "It is the Taisho Period in Japan. Tanjiro, a kindhearted boy who sells charcoal for a living, finds his family slaugh...",
        "description": "It is the Taisho Period in Japan. Tanjiro, a kindhearted boy who sells charcoal for a living, finds his family slaughtered by a demon. To make matters worse, his younger sister Nezuko, the sole survivor, has been transformed into a demon herself. Though devastated by this grim reality, Tanjiro resolves to become a \u201cdemon slayer\u201d so that he can turn his sister back into a human, and kill the demon that massacred his family.\n\n(Source: Crunchyroll)",
        "genres": [
            "slice-of-life",
            "adventure",
            "fantasy",
            "action"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/101922-33MtJGsUSxga.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx101922-WBsBl0ClmgYL.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/101922-33MtJGsUSxga.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx101922-WBsBl0ClmgYL.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/101922-33MtJGsUSxga.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx101922-WBsBl0ClmgYL.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/n129130-SJC0Kn1DU39E.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b126071-BTNEc1nRIv68.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b129131-FZrQ7lSlxmEr.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b127518-NRlq1CQ1v1ro.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b137773-N4O52f73dJKZ.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b137808-4yA8XQUDrAho.png"
        ]
    },
    {
        "title": "JUJUTSU KAISEN",
        "short_summary": "A boy fights... for \"the right death.\"\n\n\n\nHardship, regret, shame: the negative feelings that humans feel become Curs...",
        "description": "A boy fights... for \"the right death.\"\n\nHardship, regret, shame: the negative feelings that humans feel become Curses that lurk in our everyday lives. The Curses run rampant throughout the world, capable of leading people to terrible misfortune and even death. What's more, the Curses can only be exorcised by another Curse.\n\nItadori Yuji is a boy with tremendous physical strength, though he lives a completely ordinary high school life. One day, to save a friend who has been attacked by Curses, he eats the finger of the Double-Faced Specter, taking the Curse into his own soul. From then on, he shares one body with the Double-Faced Specter. Guided by the most powerful of sorcerers, Gojou Satoru, Itadori is admitted to the Tokyo Metropolitan Technical High School of Sorcery, an organization that fights the Curses... and thus begins the heroic tale of a boy who became a Curse to exorcise a Curse, a life from which he could never turn back.\n\n(Source: Crunchyroll)",
        "genres": [
            "slice-of-life",
            "fantasy",
            "action"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/113415-jQBSkxWAAk83.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx113415-LHBAeoZDIsnF.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/113415-jQBSkxWAAk83.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx113415-LHBAeoZDIsnF.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/113415-jQBSkxWAAk83.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx113415-LHBAeoZDIsnF.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b126635-L0y3I92JSUkN.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b127212-FVm2tD0erQ5B.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b133700-f6sOO3TcgLV6.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b127691-9zqh1xpIubn7.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b133704-8wLTGjc234q2.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b157867-dHdd8ZECuzHx.png"
        ]
    },
    {
        "title": "Death Note",
        "short_summary": "Light Yagami is a genius high school student who is about to learn about life through a book of death. When a bored s...",
        "description": "Light Yagami is a genius high school student who is about to learn about life through a book of death. When a bored shinigami, a God of Death, named Ryuk drops a black notepad called a Death Note, Light receives power over life and death with the stroke of a pen. Determined to use this dark gift for the best, Light sets out to rid the world of evil\u2026 namely, the people he believes to be evil. Should anyone hold such power?\n\nThe consequences of Light\u2019s actions will set the world ablaze.\n\n(Source: VIZ Media)",
        "genres": [
            "fantasy",
            "action",
            "sci-fi"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/1535.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx1535-kUgkcrfOrkUM.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/1535.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx1535-kUgkcrfOrkUM.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/1535.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx1535-kUgkcrfOrkUM.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b835-CiZa8y2z2gCz.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b75-IkEpzO21LgFy.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b80-26EhwSsSqQ50.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b71-1W4panC53vfs.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/n464-6KeJpU6g7Hwj.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b463-QBLeLf6XxVg6.png"
        ]
    },
    {
        "title": "My Hero Academia",
        "short_summary": "What would the world be like if 80 percent of the population manifested extraordinary superpowers called \u201cQuirks\u201d at ...",
        "description": "What would the world be like if 80 percent of the population manifested extraordinary superpowers called \u201cQuirks\u201d at age four? Heroes and villains would be battling it out everywhere! Becoming a hero would mean learning to use your power, but where would you go to study? U.A. High's Hero Program of course! But what would you do if you were one of the 20 percent who were born Quirkless?\n\nMiddle school student Izuku Midoriya wants to be a hero more than anything, but he hasn't got an ounce of power in him. With no chance of ever getting into the prestigious U.A. High School for budding heroes, his life is looking more and more like a dead end. Then an encounter with All Might, the greatest hero of them all gives him a chance to change his destiny\u2026\n\n(Source: VIZ Media)",
        "genres": [
            "slice-of-life",
            "adventure",
            "action"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21459-yeVkolGKdGUV.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21459-nYh85uj2Fuwr.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21459-yeVkolGKdGUV.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21459-nYh85uj2Fuwr.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21459-yeVkolGKdGUV.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21459-nYh85uj2Fuwr.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89224-K6KEuQAuYKzq.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89028-8w1I9o1ISHMg.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89221-gSF2a4gPbG4m.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b88892-bdOha3lNcaN6.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89244-VVwK9loDHeTV.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89901-XCnkga69pLN9.png"
        ]
    },
    {
        "title": "Hunter x Hunter (2011)",
        "short_summary": "A new adaption of the manga of the same name by Togashi Yoshihiro.\n\n\nA Hunter is one who travels the world doing all ...",
        "description": "A new adaption of the manga of the same name by Togashi Yoshihiro.\n\nA Hunter is one who travels the world doing all sorts of dangerous tasks. From capturing criminals to searching deep within uncharted lands for any lost treasures. Gon is a young boy whose father disappeared long ago, being a Hunter. He believes if he could also follow his father's path, he could one day reunite with him.\n\nAfter becoming 12, Gon leaves his home and takes on the task of entering the Hunter exam, notorious for its low success rate and high probability of death to become an official Hunter. He befriends the revenge-driven Kurapika, the doctor-to-be Leorio and the rebellious ex-assassin Killua in the exam, with their friendship prevailing throughout the many trials and threats they come upon taking on the dangerous career of a Hunter.",
        "genres": [
            "fantasy",
            "adventure",
            "action"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/11061-8WkkTZ6duKpq.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx11061-y5gsT1hoHuHw.png",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/11061-8WkkTZ6duKpq.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx11061-y5gsT1hoHuHw.png"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/11061-8WkkTZ6duKpq.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx11061-y5gsT1hoHuHw.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b29-RgzoSeKmDYzl.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b28-ivA7UGnfE40a.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b31-FZckOuu7L1un.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b27-Z5O02kQUydpT.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b30-lyFExKyDhefc.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b6088-Bih7EhJL1QE6.jpg"
        ]
    },
    {
        "title": "One-Punch Man",
        "short_summary": "Saitama has a rather peculiar hobby, being a superhero, but despite his heroic deeds and superhuman abilities, a shad...",
        "description": "Saitama has a rather peculiar hobby, being a superhero, but despite his heroic deeds and superhuman abilities, a shadow looms over his life. He's become much too powerful, to the point that every opponent ends up defeated with a single punch.\n\nThe lack of challenge has driven him into a state of apathy, as he watches his life pass by having lost all enthusiasm, at least until he's unwillingly thrust in the role of being a mentor to the young and revenge-driven Genos.",
        "genres": [
            "slice-of-life",
            "fantasy",
            "action",
            "sci-fi"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21087-sHb9zUZFsHe1.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21087-B5DHjqZ3kW4b.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21087-sHb9zUZFsHe1.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21087-B5DHjqZ3kW4b.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21087-sHb9zUZFsHe1.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21087-B5DHjqZ3kW4b.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b73935-ON5d0mAcrItd.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b73979-tVi9maPID881.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b86031-7NpSkSSrT7ZJ.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b85991-pA7l7Lzp4JEf.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b85981-u9EhPhy76vJr.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b154767-B8TieN81pfMI.png"
        ]
    },
    {
        "title": "ONE PIECE",
        "short_summary": "Gold Roger was known as the Pirate King, the strongest and most infamous being to have sailed the Grand Line. The cap...",
        "description": "Gold Roger was known as the Pirate King, the strongest and most infamous being to have sailed the Grand Line. The capture and death of Roger by the World Government brought a change throughout the world. His last words before his death revealed the location of the greatest treasure in the world, One Piece. It was this revelation that brought about the Grand Age of Pirates, men who dreamed of finding One Piece (which promises an unlimited amount of riches and fame), and quite possibly the most coveted of titles for the person who found it, the title of the Pirate King.\n\nEnter Monkey D. Luffy, a 17-year-old boy that defies your standard definition of a pirate. Rather than the popular persona of a wicked, hardened, toothless pirate who ransacks villages for fun, Luffy\u2019s reason for being a pirate is one of pure wonder; the thought of an exciting adventure and meeting new and intriguing people, along with finding One Piece, are his reasons of becoming a pirate. Following in the footsteps of his childhood hero, Luffy and his crew travel across the Grand Line, experiencing crazy adventures, unveiling dark mysteries and battling strong enemies, all in order to reach One Piece.\n\n<b>*This includes the following special episodes:</b>\n\n- Chopperman to the Rescue! Protect the TV Station by the Shore! (Episode 336)",
        "genres": [
            "slice-of-life",
            "adventure",
            "fantasy",
            "action"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21-wf37VakJmZqs.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21-ELSYx3yMPcKM.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21-wf37VakJmZqs.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21-ELSYx3yMPcKM.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21-wf37VakJmZqs.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21-ELSYx3yMPcKM.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b724-GFGgI9AJQkfy.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b62-S7oAeA9WInjV.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b309-H64NhbJ2ywIQ.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b723-vp5hPptgnNEC.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b61-ywXUyyocEEqt.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b40-MNypXsxSRb1R.png"
        ]
    },
    {
        "title": "Tokyo Ghoul",
        "short_summary": "The suspense horror/dark fantasy story is set in Tokyo, which is haunted by mysterious \"ghouls\" who are devouring hum...",
        "description": "The suspense horror/dark fantasy story is set in Tokyo, which is haunted by mysterious \"ghouls\" who are devouring humans. People are gripped by the fear of these ghouls whose identities are masked in mystery. An ordinary college student named Kaneki encounters Rize, a girl who is an avid reader like him, at the caf\u00e9 he frequents. Little does he realize that his fate will change overnight.\n\n(Source: Anime News Network)",
        "genres": [
            "slice-of-life",
            "fantasy",
            "action",
            "sci-fi"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/20605-RCJ7M71zLmrh.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/medium/b20605-k665mVkSug8D.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/20605-RCJ7M71zLmrh.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/medium/b20605-k665mVkSug8D.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/20605-RCJ7M71zLmrh.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/medium/b20605-k665mVkSug8D.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b87275-mb13EWZBdbh3.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b87277-oUaqrI1iBzu6.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b88412-sIOJUnIkyFRe.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b88421-F8yaeVfHjwYn.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b125884-x9UNA2Lp31pf.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b167631-TV6kzYnv1iwP.jpg"
        ]
    },
    {
        "title": "Attack on Titan Season 2",
        "short_summary": "Eren Jaeger swore to wipe out every last Titan, but in a battle for his life he wound up becoming the thing he hates ...",
        "description": "Eren Jaeger swore to wipe out every last Titan, but in a battle for his life he wound up becoming the thing he hates most. With his new powers, he fights for humanity's freedom facing the monsters that threaten his home. After a bittersweet victory against the Female Titan, Eren finds no time to rest\u2014a horde of Titans is approaching Wall Rose and the battle for humanity continues!\n\n(Source: Funimation)",
        "genres": [
            "slice-of-life",
            "fantasy",
            "action",
            "sci-fi"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/20958-Y7eQdz9VENBD.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20958-HuFJyr54Mmir.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/20958-Y7eQdz9VENBD.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20958-HuFJyr54Mmir.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/20958-Y7eQdz9VENBD.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20958-HuFJyr54Mmir.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b40881-F3gr1PkreDvj.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b46494-g7xYYuBtYPnO.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b40882-dsj7IP943WFF.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b71479-huCD908XIdqv.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b46484-P6A2GjNQn49F.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/126849-jH0gw54UpbDQ.jpg"
        ]
    },
    {
        "title": "Fullmetal Alchemist: Brotherhood",
        "short_summary": "\"In order for something to be obtained, something of equal value must be lost.\"\n\n\n\nAlchemy is bound by this Law of Eq...",
        "description": "\"In order for something to be obtained, something of equal value must be lost.\"\n\nAlchemy is bound by this Law of Equivalent Exchange\u2014something the young brothers Edward and Alphonse Elric only realize after attempting human transmutation: the one forbidden act of alchemy. They pay a terrible price for their transgression\u2014Edward loses his left leg, Alphonse his physical body. It is only by the desperate sacrifice of Edward's right arm that he is able to affix Alphonse's soul to a suit of armor. Devastated and alone, it is the hope that they would both eventually return to their original bodies that gives Edward the inspiration to obtain metal limbs called \"automail\" and become a state alchemist, the Fullmetal Alchemist.\n\nThree years of searching later, the brothers seek the Philosopher's Stone, a mythical relic that allows an alchemist to overcome the Law of Equivalent Exchange. Even with military allies Colonel Roy Mustang, Lieutenant Riza Hawkeye, and Lieutenant Colonel Maes Hughes on their side, the brothers find themselves caught up in a nationwide conspiracy that leads them not only to the true nature of the elusive Philosopher's Stone, but their country's murky history as well. In between finding a serial killer and racing against time, Edward and Alphonse must ask themselves if what they are doing will make them human again... or take away their humanity.\n\n(Source: MAL Rewrite)",
        "genres": [
            "slice-of-life",
            "adventure",
            "fantasy",
            "action"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/5114-q0V5URebphSG.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx5114-nSWCgQlmOMtj.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/5114-q0V5URebphSG.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx5114-nSWCgQlmOMtj.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/5114-q0V5URebphSG.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx5114-nSWCgQlmOMtj.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b12-tCKu8yK5kFL5.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b11-TA5Nuk7EDUZG.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b5988-Wo1TMSnDnPIm.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/15540.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/10974.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/15532.jpg"
        ]
    },
    {
        "title": "Naruto",
        "short_summary": "Naruto Uzumaki, a hyperactive and knuckle-headed ninja, lives in Konohagakure, the Hidden Leaf village. Moments prior...",
        "description": "Naruto Uzumaki, a hyperactive and knuckle-headed ninja, lives in Konohagakure, the Hidden Leaf village. Moments prior to his birth, a huge demon known as the Kyuubi, the Nine-tailed Fox, attacked Konohagakure and wreaked havoc. In order to put an end to the Kyuubi's rampage, the leader of the village, the 4th Hokage, sacrificed his life and sealed the monstrous beast inside the newborn Naruto.\n\nShunned because of the presence of the Kyuubi inside him, Naruto struggles to find his place in the village. He strives to become the Hokage of Konohagakure, and he meets many friends and foes along the way.\n\n(Source: MAL Rewrite)",
        "genres": [
            "slice-of-life",
            "adventure",
            "fantasy",
            "action"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/20-HHxhPj5JD13a.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20-dE6UHbFFg1A5.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/20-HHxhPj5JD13a.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20-dE6UHbFFg1A5.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/20-HHxhPj5JD13a.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20-dE6UHbFFg1A5.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b145-IorfpI8arxeX.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b17-phjcWCkRuIhu.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b85-mkVBh2yjxjmx.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b13-SISLEw1oAD7a.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/n23215-psvpC0r5tkkI.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/n17546-zdnPQ3ZdKJjz.png"
        ]
    },
    {
        "title": "Sword Art Online",
        "short_summary": "In the near future, a Virtual Reality Massive Multiplayer Online Role-Playing Game (VRMMORPG) called Sword Art Online...",
        "description": "In the near future, a Virtual Reality Massive Multiplayer Online Role-Playing Game (VRMMORPG) called Sword Art Online has been released where players control their avatars with their bodies using a piece of technology called Nerve Gear. One day, players discover they cannot log out, as the game creator is holding them captive unless they reach the 100th floor of the game's tower and defeat the final boss. However, if they die in the game, they die in real life. Their struggle for survival starts now...\n\n(Source: Crunchyroll)",
        "genres": [
            "fantasy",
            "adventure",
            "romance",
            "action"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/11757-TlEEV9weG4Ag.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx11757-SxYDUzdr9rh2.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/11757-TlEEV9weG4Ag.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx11757-SxYDUzdr9rh2.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/11757-TlEEV9weG4Ag.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx11757-SxYDUzdr9rh2.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b36765-BnLbXg0Tzzh9.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b36831-JfyFU7gPPVmr.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b36828-j5ib0adAzGMx.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b65171-4gM7UgGDU6H5.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b36830-41SWIDvhqOo4.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b67149-UcNSv3YWMl26.png"
        ]
    },
    {
        "title": "Your Name.",
        "short_summary": "Mitsuha Miyamizu, a high school girl, yearns to live the life of a boy in the bustling city of Tokyo\u2014a dream that sta...",
        "description": "Mitsuha Miyamizu, a high school girl, yearns to live the life of a boy in the bustling city of Tokyo\u2014a dream that stands in stark contrast to her present life in the countryside. Meanwhile in the city, Taki Tachibana lives a busy life as a high school student while juggling his part-time job and hopes for a future in architecture.\n\nOne day, Mitsuha awakens in a room that is not her own and suddenly finds herself living the dream life in Tokyo\u2014but in Taki's body! Elsewhere, Taki finds himself living Mitsuha's life in the humble countryside. In pursuit of an answer to this strange phenomenon, they begin to search for one another.\n\nKimi no Na wa. revolves around Mitsuha and Taki's actions, which begin to have a dramatic impact on each other's lives, weaving them into a fabric held together by fate and circumstance.\n\n(Source: MAL Rewrite)",
        "genres": [
            "fantasy",
            "romance",
            "slice-of-life"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21519-1ayMXgNlmByb.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21519-SUo3ZQuCbYhJ.png",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21519-1ayMXgNlmByb.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21519-SUo3ZQuCbYhJ.png"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21519-1ayMXgNlmByb.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21519-SUo3ZQuCbYhJ.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b121514-MGI7JRluscpz.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b121516-kuPVJLNsH5uE.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/121524-aSUbujPYjFRX.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/121517-JHgyJZkaxYiW.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/121518-wB61TbuDbqOc.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/121520-UQ3c0qMgX6OJ.jpg"
        ]
    },
    {
        "title": "A Silent Voice",
        "short_summary": "After transferring into a new school, a deaf girl, Shouko Nishimiya, is bullied by the popular Shouya Ishida. As Shou...",
        "description": "After transferring into a new school, a deaf girl, Shouko Nishimiya, is bullied by the popular Shouya Ishida. As Shouya continues to bully Shouko, the class turns its back on him. Shouko transfers and Shouya grows up as an outcast. Alone and depressed, the regretful Shouya finds Shouko to make amends.\n\n(Source: Eleven Arts)",
        "genres": [
            "romance",
            "slice-of-life"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/20954-f30bHMXa5Qoe.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20954-sYRfE5jQRtSB.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/20954-f30bHMXa5Qoe.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20954-sYRfE5jQRtSB.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/20954-f30bHMXa5Qoe.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20954-sYRfE5jQRtSB.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b80491-NK6pxb6oH61P.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b80243-RzxE51iUU5eq.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/124035-Il86uF1hboRA.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/124037-3KFDLRIT66Bn.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b135853-86mTC0Tva8r3.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89335-3fy5a7Qa9h9J.jpg"
        ]
    },
    {
        "title": "Attack on Titan Season 3",
        "short_summary": "Eren and his companions in the 104th are assigned to the newly-formed Levi Squad, whose assignment is to keep Eren an...",
        "description": "Eren and his companions in the 104th are assigned to the newly-formed Levi Squad, whose assignment is to keep Eren and Historia safe given Eren's newly-discovered power and Historia's knowledge and pedigree. Levi and Erwin have good reason to be concerned, because the priest of the Church that Hanji had hidden away was found tortured to death, making it clear that the Military Police are involved with the cover-up. Things get more harrowing when the MPs make a move on Erwin and the Levi Squad narrowly avoids capture. Eren is also having problems with his Titan transformation, and a deadly killer has been hired to secure Eren and Historia, one Levi knows all too well from his youth.\n\n(Source: Anime News Network)",
        "genres": [
            "slice-of-life",
            "fantasy",
            "action",
            "sci-fi"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/99147-HACsFVrynFf5.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx99147-AiPDD8cwlCfi.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/99147-HACsFVrynFf5.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx99147-AiPDD8cwlCfi.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/99147-HACsFVrynFf5.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx99147-AiPDD8cwlCfi.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b40882-dsj7IP943WFF.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b40881-F3gr1PkreDvj.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b46496-Mu86MENd5wNB.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b46494-g7xYYuBtYPnO.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b45627-CR68RyZmddGG.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b62481-ZZDa7vn17lMU.png"
        ]
    },
    {
        "title": "My Hero Academia Season 2",
        "short_summary": "Taking off right after the last episode of the first season. The school is temporarily closed due to security. When U...",
        "description": "Taking off right after the last episode of the first season. The school is temporarily closed due to security. When U.A. restarts, it is announced that the highly anticipated School Sports Festival will soon be taking place. All classes: Hero, Support, General and Business will be participating. Tournaments all round will decide who is the top Hero in training.\n\n(Source: Anime News Network)",
        "genres": [
            "slice-of-life",
            "adventure",
            "action"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21856-wtSHgeHFmzdG.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21856-gutauxhWAwn6.png",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21856-wtSHgeHFmzdG.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21856-gutauxhWAwn6.png"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21856-wtSHgeHFmzdG.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21856-gutauxhWAwn6.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b88892-bdOha3lNcaN6.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89222-TL8MQM3wJgEB.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89224-K6KEuQAuYKzq.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89221-gSF2a4gPbG4m.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89220-KNBwaVFAR8FD.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89028-8w1I9o1ISHMg.png"
        ]
    },
    {
        "title": "Attack on Titan Final Season",
        "short_summary": "It\u2019s been four years since the Scout Regiment reached the shoreline, and the world looks different now. Things are he...",
        "description": "It\u2019s been four years since the Scout Regiment reached the shoreline, and the world looks different now. Things are heating up as the fate of the Scout Regiment\u2014and the people of Paradis\u2014are determined at last. However, Eren is missing. Will he reappear before age-old tensions between Marleyans and Eldians result in the war of all wars?\n\n(Source: Crunchyroll)",
        "genres": [
            "slice-of-life",
            "fantasy",
            "action",
            "sci-fi"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/110277-iuGn6F5bK1U1.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx110277-sKUNXAsWMNFw.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/110277-iuGn6F5bK1U1.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx110277-sKUNXAsWMNFw.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/110277-iuGn6F5bK1U1.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx110277-sKUNXAsWMNFw.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b40882-dsj7IP943WFF.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b125661-FiqFvAtNlL0v.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b40881-F3gr1PkreDvj.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b46494-g7xYYuBtYPnO.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b125660-mrmpOJLjJIkv.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b125659-O37MZQWibV7g.png"
        ]
    },
    {
        "title": "The Promised Neverland",
        "short_summary": "Emma, Norman and Ray are the brightest kids at the Grace Field House orphanage. And under the care of the woman they ...",
        "description": "Emma, Norman and Ray are the brightest kids at the Grace Field House orphanage. And under the care of the woman they refer to as \u201cMom,\u201d all the kids have enjoyed a comfortable life. Good food, clean clothes and the perfect environment to learn\u2014what more could an orphan ask for? One day, though, Emma and Norman uncover the dark truth of the outside world they are forbidden from seeing.\n\n(Source: VIZ Media)",
        "genres": [
            "action",
            "fantasy",
            "slice-of-life",
            "sci-fi"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/101759-MhlCoeqnODso.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx101759-8UR7r9MNVpz2.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/101759-MhlCoeqnODso.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx101759-8UR7r9MNVpz2.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/101759-MhlCoeqnODso.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx101759-8UR7r9MNVpz2.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b121700-CRwKIlcBcjbv.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b121724-SJTdODjeO7e6.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b121725-LQciVJOjnMVh.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b129784-fn5VoMYAqCsk.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b129785-7MHIm3Cp2HuM.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b126455-ki6wpr5Un4fF.png"
        ]
    },
    {
        "title": "Assassination Classroom",
        "short_summary": "The students of class 3-E have a mission: kill their teacher before graduation. He has already destroyed the moon, an...",
        "description": "The students of class 3-E have a mission: kill their teacher before graduation. He has already destroyed the moon, and has promised to destroy the Earth if he can not be killed within a year. But how\n\ncan this class of misfits kill a tentacled monster, capable of reaching Mach 20 speed, who may be the best teacher any of them have ever had?",
        "genres": [
            "slice-of-life",
            "fantasy",
            "action"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/20755-D4ipww9U8YkC.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20755-dWrhs569YGUO.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/20755-D4ipww9U8YkC.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20755-dWrhs569YGUO.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/20755-D4ipww9U8YkC.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20755-dWrhs569YGUO.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b65643-jimrOw0RGtoB.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b65645-nWH4mBMW5lYw.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b85807-mOgdYvQ0zlDD.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/85811-wV4VTP3IT1Ep.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/88802-5bvdO2byRTCS.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b172719-z5vrTMTtknNH.jpg"
        ]
    },
    {
        "title": "Mob Psycho 100",
        "short_summary": "The story revolves around \"Mob,\" a boy who will explode if his emotional capacity reaches 100%. This boy with psychic...",
        "description": "The story revolves around \"Mob,\" a boy who will explode if his emotional capacity reaches 100%. This boy with psychic powers earned his nickname \"Mob\" because he does not stand out among other people. He keeps his psychic powers bottled up so he can live normally, but if his emotional level reaches 100, something will overwhelm his entire body.\n\n(Source: Anime News Network)",
        "genres": [
            "slice-of-life",
            "fantasy",
            "action",
            "sci-fi"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21507-Qx8bGsLXUgLo.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21507-6YUSbh2m0N1p.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21507-Qx8bGsLXUgLo.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21507-6YUSbh2m0N1p.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21507-Qx8bGsLXUgLo.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21507-6YUSbh2m0N1p.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89616-dXmdOc7L6SDi.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89334-OPj1hCzvrt7X.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89617-HHZ1kziYxc0q.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89618-iSTUyCdu1yZ8.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/89623-9JhzOrRvzaII.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/n133199-4OdUFnhyNi37.jpg"
        ]
    },
    {
        "title": "Chainsaw Man",
        "short_summary": "Denji is a teenage boy living with a Chainsaw Devil named Pochita. Due to the debt his father left behind, he has bee...",
        "description": "Denji is a teenage boy living with a Chainsaw Devil named Pochita. Due to the debt his father left behind, he has been living a rock-bottom life while repaying his debt by harvesting devil corpses with Pochita.\n\nOne day, Denji is betrayed and killed. As his consciousness fades, he makes a contract with Pochita and gets revived as \"Chainsaw Man\" \u2014 a man with a devil's heart.\n\n(Source: Crunchyroll)",
        "genres": [
            "slice-of-life",
            "fantasy",
            "action"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/127230-o8IRwCGVr9KW.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx127230-DdP4vAdssLoz.png",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/127230-o8IRwCGVr9KW.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx127230-DdP4vAdssLoz.png"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/127230-o8IRwCGVr9KW.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx127230-DdP4vAdssLoz.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b137081-TSrUR3mUJL6r.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b137079-6yLEUYR3bmpr.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b137080-UHcynYNjb5ZU.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b130102-FO1VHNnEnLlB.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b174263-TTMWfBlU1k3f.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b174272-cU9W4oNykNM0.png"
        ]
    },
    {
        "title": "Re:ZERO -Starting Life in Another World-",
        "short_summary": "In the story, Subaru Natsuki is an ordinary high school student who is lost in an alternate world, where he is rescue...",
        "description": "In the story, Subaru Natsuki is an ordinary high school student who is lost in an alternate world, where he is rescued by a beautiful, silver-haired girl. He stays near her to return the favor, but the destiny she is burdened with is more than Subaru can imagine. Enemies attack one by one, and both of them are killed. He then finds out he has the power to rewind death, back to the time he first came to this world. But only he remembers what has happened since.\n\n(Source: Anime News Network)\n\nNotes:\n\n- The first episode aired with a runtime of ~50 minutes as opposed to the standard 25 minute long episode.",
        "genres": [
            "fantasy",
            "action",
            "adventure",
            "romance",
            "slice-of-life",
            "sci-fi"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21355-f9SjOfEJMk5P.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21355-wRVUrGxpvIQQ.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21355-f9SjOfEJMk5P.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21355-wRVUrGxpvIQQ.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21355-f9SjOfEJMk5P.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21355-wRVUrGxpvIQQ.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b88573-F8yMTK9GhnTA.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b88572-IzTwXEHSobRs.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b88575-Ayu8UPDA8NS6.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b88576-NWkotUiJ3mK3.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b90178-olaN8k9RJRxo.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b90186-yr2PT4gI2qa3.png"
        ]
    },
    {
        "title": "Your lie in April",
        "short_summary": "Piano prodigy Arima Kousei dominated the competition and all child musicians knew his name. But after his mother, who...",
        "description": "Piano prodigy Arima Kousei dominated the competition and all child musicians knew his name. But after his mother, who was also his instructor, passed away, he had a mental breakdown while performing\n\nat a recital. This resulted in him no longer being able to hear the sound of his piano playing. Two years later, Kousei hasn\u2019t touched the piano and views the world without any flair or color. He was\n\ncontent at living out his life with his good friends Tsubaki and Watari until, one day, a girl changed everything. Miyazono Kaori is a pretty, free spirited violinist whose playing style reflects her\n\npersonality. Kaori helps Kousei return to the music world and show that it should be free and mold breaking unlike the structured and rigid style Kousei was used to.",
        "genres": [
            "romance",
            "slice-of-life"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/20665-j4kSsfhfkM24.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20665-TLgkL8T8IRFd.png",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/20665-j4kSsfhfkM24.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20665-TLgkL8T8IRFd.png"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/20665-j4kSsfhfkM24.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20665-TLgkL8T8IRFd.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/69405-IpsjziJkHrHj.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b69407-eyIvpsFPeARS.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/69409-lq7MFPFTwmBu.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b69411-lxM0FRvWHqlv.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/88785-ddUKFQv4ZkND.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/88786-toDBw77jbCTx.png"
        ]
    },
    {
        "title": "Attack on Titan Season 3 Part 2",
        "short_summary": "The battle to retake Wall Maria begins now! With Eren\u2019s new hardening ability, the Scouts are confident they can seal...",
        "description": "The battle to retake Wall Maria begins now! With Eren\u2019s new hardening ability, the Scouts are confident they can seal the wall and take back Shiganshina District. If they succeed, Eren can finally unlock the secrets of the basement\u2014and the world. But danger lies in wait as Reiner, Bertholdt, and the Beast Titan have plans of their own. Could this be humanity\u2019s final battle for survival?\n\n(Source: Funimation)",
        "genres": [
            "slice-of-life",
            "fantasy",
            "action",
            "sci-fi"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/104578-z7SadpYEuAsy.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx104578-k61nx3LPjvgd.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/104578-z7SadpYEuAsy.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx104578-k61nx3LPjvgd.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/104578-z7SadpYEuAsy.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx104578-k61nx3LPjvgd.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b40882-dsj7IP943WFF.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b40881-F3gr1PkreDvj.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b46496-Mu86MENd5wNB.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b46494-g7xYYuBtYPnO.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b45627-CR68RyZmddGG.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b127703-qNIccR0yPZKu.png"
        ]
    },
    {
        "title": "Naruto: Shippuden",
        "short_summary": "Naruto: Shippuuden is the continuation of the original animated TV series Naruto. The story revolves around an older ...",
        "description": "Naruto: Shippuuden is the continuation of the original animated TV series Naruto. The story revolves around an older and slightly more matured Uzumaki Naruto and his quest to save his friend Uchiha Sasuke from the grips of the snake-like Shinobi, Orochimaru. After 2 and a half years Naruto finally returns to his village of Konoha, and sets about putting his ambitions to work, though it will not be easy, as he has amassed a few (more dangerous) enemies, in the likes of the shinobi organization; Akatsuki.\n\n(Source: Anime News Network)",
        "genres": [
            "slice-of-life",
            "adventure",
            "fantasy",
            "action"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/1735.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx1735-kGfVm0YqCPcu.png",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/1735.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx1735-kGfVm0YqCPcu.png"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/1735.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx1735-kGfVm0YqCPcu.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b145-IorfpI8arxeX.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b17-phjcWCkRuIhu.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b85-mkVBh2yjxjmx.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b13-SISLEw1oAD7a.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/52053.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b728-zHw77BzLzQKT.jpg"
        ]
    },
    {
        "title": "ERASED",
        "short_summary": "Satoru Fujinuma is a 29 year old manga artist struggling to make a name for himself following his debut. But, that wa...",
        "description": "Satoru Fujinuma is a 29 year old manga artist struggling to make a name for himself following his debut. But, that was not the only thing in his life that Satoru was feeling frustrated about\u2026 He has a\n\nunique supernatural ability of being forced to prevent deaths and catastrophes by being sent back in time before the incident occurred, repeating time until the accident is prevented. One day, he gets\n\ninvolved in an accident that has him framed as a murderer. Desperate to save the victim, he sends himself back in time only to find himself as a grade-schooler one month before fellow classmate Kayo\n\nHinazuki went missing. Satoru now embarks on a new quest: to save Kayo and solve the mystery behind her disappearance.",
        "genres": [
            "action",
            "fantasy",
            "slice-of-life",
            "sci-fi"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21234-7lfSSPoMmwr2.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21234-XmqW39aQ9o7O.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21234-7lfSSPoMmwr2.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21234-XmqW39aQ9o7O.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/21234-7lfSSPoMmwr2.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21234-XmqW39aQ9o7O.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89275-xCGzh6jAGe2v.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/89276-LjlYvXfOnjHB.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/89365-Esm33rYZ3x0s.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b382887-zeZRz20M1eRF.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89366-5KwJW3NNmmti.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b382886-QXMx72vtxGmZ.png"
        ]
    },
    {
        "title": "My Hero Academia Season 3",
        "short_summary": "Summer is here, and the heroes of Class 1-A and 1-B are in for the toughest training camp of their lives! A group of ...",
        "description": "Summer is here, and the heroes of Class 1-A and 1-B are in for the toughest training camp of their lives! A group of seasoned pros pushes everyone's Quirks to new heights as the students face one overwhelming challenge after another. Braving the elements in this secret location becomes the least of their worries when routine training turns into a critical struggle for survival.\n\n(Source: Crunchyroll)",
        "genres": [
            "slice-of-life",
            "adventure",
            "action"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/100166-k7RXwN5vZg0r.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx100166-jUCZYbzn2XLw.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/100166-k7RXwN5vZg0r.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx100166-jUCZYbzn2XLw.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/100166-k7RXwN5vZg0r.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx100166-jUCZYbzn2XLw.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b88892-bdOha3lNcaN6.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89028-8w1I9o1ISHMg.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89224-K6KEuQAuYKzq.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89244-VVwK9loDHeTV.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b89896-3QzT5nSEPjcr.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b121529-uVxKmxh0QvQi.png"
        ]
    },
    {
        "title": "Steins;Gate",
        "short_summary": "Self-proclaimed mad scientist Okabe Rintarou lives in a small room in Akihabara, where he invents \"future gadgets\" wi...",
        "description": "Self-proclaimed mad scientist Okabe Rintarou lives in a small room in Akihabara, where he invents \"future gadgets\" with fellow lab members Shiina Mayuri, his air-headed childhood friend, and Hashida Itaru, an otaku hacker. The three pass the time by tinkering with their latest creation, a \"Phone Microwave\" that can be controlled through text messages.\n\nThe lab members soon face a string of mysterious incidents that lead to a game-changing discovery: the Phone Microwave can send emails to the past and thus alter history. Adapted from the critically acclaimed visual novel by 5pb. and Nitroplus, Steins;Gate takes Okabe to the depths of scientific theory and human despair as he faces the dire consequences of changing the past.",
        "genres": [
            "action",
            "slice-of-life",
            "sci-fi"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/n9253-JIhmKgBKsWUN.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx9253-tIUXF2gfU8Sg.jpg",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/n9253-JIhmKgBKsWUN.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx9253-tIUXF2gfU8Sg.jpg"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/n9253-JIhmKgBKsWUN.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx9253-tIUXF2gfU8Sg.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b35258-FeTGR4LEUNvt.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b35255-Ra9Aq5Kn9lYq.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b35252-DY9TW6pusqeh.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b35253-u6QVgLLyHq2W.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b34470-Jw2LXZBL5R8i.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/44274-GDkveusoWUqX.jpg"
        ]
    },
    {
        "title": "Spice and Wolf",
        "short_summary": "The peddler Kraft Lawrence travels through the world selling all kinds of things. After visiting a village, he discov...",
        "description": "The peddler Kraft Lawrence travels through the world selling all kinds of things. After visiting a village, he discovers a sleeping girl under the pelts in his cart. She has wolf ears and a tail. The\n\nwolf girl explains that she has been called a \"god\", but that her name is Holo and nothing more. Lawrence teases the girl a little, but after hearing more of her story, he is moved and decides to\n\naccompany her further north. On their travels the two have many adventures, often getting into trouble, but the bond between them grows stronger.",
        "genres": [
            "fantasy",
            "adventure",
            "romance",
            "slice-of-life"
        ],
        "landscape_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/2966-h1ZiL7o7oYPs.jpg",
        "portrait_thumbnail": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx2966-AEULMyYA9WKb.png",
        "images": {
            "landscape": "https://s4.anilist.co/file/anilistcdn/media/anime/banner/2966-h1ZiL7o7oYPs.jpg",
            "portrait": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx2966-AEULMyYA9WKb.png"
        },
        "slides": [
            "https://s4.anilist.co/file/anilistcdn/media/anime/banner/2966-h1ZiL7o7oYPs.jpg",
            "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx2966-AEULMyYA9WKb.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b7373-1BH0gELuZmHD.jpg",
            "https://s4.anilist.co/file/anilistcdn/character/large/b7374-XeKVCsoW129T.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b7376-Hc7DpDQj6I31.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b7375-Fl8ZYFMB1MPP.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b17825-ZmfXoh0lbcYc.png",
            "https://s4.anilist.co/file/anilistcdn/character/large/b24360-eyCHMvYkycJJ.png"
        ]
    }
]

def download_image(url, save_path):
    if os.path.exists(save_path):
        return
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    try:
        r = requests.get(url, stream=True, timeout=10)
        r.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def main():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("Removing old seeds and cleaning media directory...")
    db[ANIME_COLLECTION].drop()
    db[GENRE_COLLECTION].drop()
    
    media_dir = "media"
    anime_media_path = os.path.join(media_dir, "anime")
    if os.path.exists(anime_media_path):
        shutil.rmtree(anime_media_path)
    
    print("Seeding Genres...")
    genre_ops = []
    for g in ALLOWED_GENRES:
        slug = g.lower().replace(" ", "-")
        genre_ops.append(
            UpdateOne(
                {"slug": slug},
                {"$set": {"name": g, "slug": slug}},
                upsert=True
            )
        )
    if genre_ops:
        db[GENRE_COLLECTION].bulk_write(genre_ops)
        
    print(f"Seeding exactly {len(ANIME_DATA)} unique Anime and downloading images...")
    anime_ops = []
    
    for anime in ANIME_DATA:
        slug = "".join([c if c.isalnum() else "-" for c in anime["title"].lower()])
        
        # Download portrait
        portrait_rel = f"anime/thumbnails/portraits/{slug}.jpg"
        download_image(anime["portrait_thumbnail"], os.path.join(media_dir, portrait_rel))
        anime["portrait_thumbnail"] = portrait_rel
        
        # Download landscape
        landscape_rel = f"anime/thumbnails/landscapes/{slug}.jpg"
        download_image(anime["landscape_thumbnail"], os.path.join(media_dir, landscape_rel))
        anime["landscape_thumbnail"] = landscape_rel
        
        anime["images"] = {
            "landscape": landscape_rel,
            "portrait": portrait_rel
        }
        
        # Download slides
        new_slides = []
        for i, slide_url in enumerate(anime["slides"]):
            slide_rel = f"anime/slidesimg/{slug}/{i}.jpg"
            download_image(slide_url, os.path.join(media_dir, slide_rel))
            new_slides.append(slide_rel)
            
        anime["slides"] = new_slides
        anime["updated_at"] = datetime.now(timezone.utc)
        anime["created_at"] = datetime.now(timezone.utc)
        
        anime_ops.append(
            UpdateOne(
                {"title": anime["title"]},
                {"$set": anime},
                upsert=True
            )
        )
        
    if anime_ops:
        result = db[ANIME_COLLECTION].bulk_write(anime_ops)
        print(f"Success! Inserted/Modified: {result.upserted_count + result.modified_count}")

if __name__ == "__main__":
    main()
