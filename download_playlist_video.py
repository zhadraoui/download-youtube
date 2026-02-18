#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import yt_dlp


# -------------------------------------------------
# Récupération playlist (léger, sans formats lourds)
# -------------------------------------------------
def get_playlist_entries(url: str):

    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if "entries" in info:
        return info["entries"]

    return [info]


# -------------------------------------------------
# Récupération formats vidéo d'une seule vidéo
# -------------------------------------------------
def get_video_formats(video_url: str):

    ydl_opts = {
        "quiet": True,
        "skip_download": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)

    formats = info.get("formats", [])

    video_formats = [
        f for f in formats
        if f.get("height") and f.get("vcodec") != "none"
    ]

    # déduplication par résolution
    unique_formats = {}
    for f in video_formats:
        height = f["height"]

        # garder le meilleur bitrate pour une résolution
        if height not in unique_formats or f.get("tbr", 0) > unique_formats[height].get("tbr", 0):
            unique_formats[height] = f

    return sorted(unique_formats.values(), key=lambda x: x["height"], reverse=True)


# -------------------------------------------------
# Construction du format yt-dlp
# -------------------------------------------------
def build_format_selector(height: int):
    return f"bestvideo[height<={height}]+bestaudio/best"


# -------------------------------------------------
# Téléchargement playlist complète
# -------------------------------------------------
def download_playlist(url: str, resolution: int, output_path: str):

    os.makedirs(output_path, exist_ok=True)

    ydl_opts = {
        "format": build_format_selector(resolution),
        "merge_output_format": "mp4",

        # Téléchargement parallèle fragments
        "concurrent_fragment_downloads": 5,

        # reprise téléchargement
        "continuedl": True,

        # Progression plus lisible
        "progress_with_newline": True,

        # Nom fichier stable
        "outtmpl": os.path.join(output_path, "%(playlist_index)02d_%(title)s.%(ext)s"),

        "encoding": "utf-8",

        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4"
        }],

        "noplaylist": False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


# -------------------------------------------------
# Programme principal
# -------------------------------------------------
def main():

    url = input("👉 Colle l'URL YouTube ou playlist : ").strip()
    output_path = "downloads"

    print("\n🔍 Analyse playlist...\n")

    entries = get_playlist_entries(url)

    if not entries:
        print("❌ Playlist vide")
        return

    # --- analyser uniquement la première vidéo ---
    first_video_id = entries[0]["id"]
    first_video_url = f"https://www.youtube.com/watch?v={first_video_id}"

    formats = get_video_formats(first_video_url)

    if not formats:
        print("❌ Aucun format vidéo trouvé")
        return

    print("📺 Résolutions disponibles :")
    for i, f in enumerate(formats):
        print(f"{i + 1}. {f['height']}p")

    # --- choix utilisateur ---
    while True:
        try:
            choice = int(input("\n👉 Choisis une résolution pour toute la playlist : "))
            selected_resolution = formats[choice - 1]["height"]
            break
        except (ValueError, IndexError):
            print("❌ Choix invalide")

    print(f"\n🚀 Téléchargement playlist en {selected_resolution}p...\n")

    download_playlist(url, selected_resolution, output_path)

    print("\n✅ Téléchargement terminé")


# -------------------------------------------------
if __name__ == "__main__":
    main()
