#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import yt_dlp


def get_video_formats(url: str):
    """
    Récupère les formats vidéo disponibles avec leurs résolutions.
    """

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "encoding": "utf-8"  # Assure que les titres avec caractères spéciaux sont bien encodés
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    formats = info.get("formats", [])

    # On garde uniquement les formats vidéo avec résolution
    video_formats = [
        f for f in formats
        if f.get("height") and f.get("vcodec") != "none"
    ]

    # Suppression doublons résolution
    unique_formats = {}
    for f in video_formats:
        unique_formats[f["height"]] = f

    return sorted(unique_formats.values(), key=lambda x: x["height"], reverse=True)


def download_video(url: str, format_id: str, output_path="downloads"):
    """
    Télécharge la vidéo selon le format sélectionné, en mp4 avec audio+vidéo fusionnés.
    """

    # Création du dossier si nécessaire
    os.makedirs(output_path, exist_ok=True)

    ydl_opts = {
        "format": f"{format_id}+bestaudio/best",
        "outtmpl": f"{output_path}/%(title)s.%(ext)s",
        "merge_output_format": "mp4",  # Fusion automatique audio + vidéo
        "encoding": "utf-8",  # UTF-8 pour les noms de fichiers
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4"
        }],
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def main():

    url = input("👉 Colle l'URL YouTube : ").strip()

    print("\n🔍 Récupération des résolutions disponibles...\n")

    formats = get_video_formats(url)

    if not formats:
        print("❌ Aucun format vidéo trouvé")
        return

    print("📺 Résolutions disponibles :\n")

    for i, f in enumerate(formats):
        print(f"{i + 1}. {f['height']}p")

    while True:
        try:
            choice = int(input("\n👉 Choisis une résolution (numéro) : "))
            selected_format = formats[choice - 1]
            break
        except (ValueError, IndexError):
            print("❌ Choix invalide")

    print("\n⬇️ Téléchargement en cours...\n")

    download_video(url, selected_format["format_id"])

    print("✅ Téléchargement terminé")


if __name__ == "__main__":
    main()

