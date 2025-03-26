import os
import shutil
import eyed3
import requests
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from collections import defaultdict

# GUI Setup
root = tk.Tk()
root.title("Music Organizer")
root.geometry("500x450")

# Function to select a folder
def select_folder():
    folder_selected = filedialog.askdirectory()
    entry_folder.delete(0, tk.END)
    entry_folder.insert(0, folder_selected)

# Function to fetch album artwork
def fetch_album_artwork(artist, title):
    try:
        url = f"https://itunes.apple.com/search?term={artist}+{title}&entity=song&limit=1"
        response = requests.get(url).json()
        if response["results"]:
            return response["results"][0]["artworkUrl100"]
    except Exception as e:
        print(f"Error fetching artwork: {e}")
    return None

# Function to organize music
def organize_music():
    music_dir = entry_folder.get()
    if not music_dir:
        messagebox.showerror("Error", "Please select a folder!")
        return

    organized_dir = os.path.join(music_dir, "Organized")
    playlists_dir = os.path.join(music_dir, "Playlists")

    genre_folders = {
        "Rock": ["rock", "alternative", "metal"],
        "Pop": ["pop", "dance", "synthpop"],
        "Hip-Hop": ["hip-hop", "rap", "trap"],
        "Afrobeats": ["afrobeats", "afropop"],
        "Instrumental": ["instrumental", "classical", "soundtrack"],
        "Other": []
    }

    # Create necessary directories
    for folder in genre_folders.keys():
        os.makedirs(os.path.join(organized_dir, folder), exist_ok=True)
    os.makedirs(playlists_dir, exist_ok=True)

    # Function to determine genre folder
    def get_genre_folder(genre):
        genre = genre.lower()
        for folder, keywords in genre_folders.items():
            if any(keyword in genre for keyword in keywords):
                return folder
        return "Other"

    # Dictionary to store playlist data
    playlists = defaultdict(list)

    music_files = [f for f in os.listdir(music_dir) if f.endswith((".mp3", ".wav", ".flac"))]
    total_files = len(music_files)
    
    if total_files == 0:
        messagebox.showwarning("No Music Files", "No music files found in the selected folder.")
        return

    progress_var.set(0)
    progress_bar["maximum"] = total_files

    for index, file in enumerate(music_files):
        file_path = os.path.join(music_dir, file)

        # Read metadata
        audiofile = eyed3.load(file_path)
        if audiofile and audiofile.tag:
            artist = audiofile.tag.artist or "Unknown Artist"
            title = audiofile.tag.title or os.path.splitext(file)[0]
            genre = audiofile.tag.genre.name if audiofile.tag.genre else None
        else:
            artist, title, genre = "Unknown Artist", os.path.splitext(file)[0], None

        # Allow manual genre selection if missing
        if not genre:
            genre = simpledialog.askstring("Genre Missing", f"Enter genre for: {artist} - {title}") or "Other"

        # Rename file
        new_filename = f"{artist} - {title}{os.path.splitext(file)[1]}"
        new_filename = new_filename.replace("/", "-")  # Fix invalid characters

        # Move to genre folder
        genre_folder = get_genre_folder(genre)
        new_path = os.path.join(organized_dir, genre_folder, new_filename)
        shutil.move(file_path, new_path)

        # Add to playlist
        playlists[genre_folder].append(new_path)

        # Fetch album artwork
        artwork_url = fetch_album_artwork(artist, title)
        if artwork_url:
            print(f"Artwork found: {artwork_url}")

        # Update progress bar
        progress_var.set(index + 1)
        status_label.config(text=f"Processing: {new_filename}")
        root.update_idletasks()

    # Create .m3u playlists
    for genre, songs in playlists.items():
        playlist_path = os.path.join(playlists_dir, f"{genre}.m3u")
        with open(playlist_path, "w", encoding="utf-8") as playlist:
            for song in songs:
                playlist.write(song + "\n")

    messagebox.showinfo("Success", "Music organized successfully!")
    status_label.config(text="✅ Organization Complete!")

# GUI Elements
tk.Label(root, text="Select Music Folder:", font=("Arial", 12)).pack(pady=5)
entry_folder = tk.Entry(root, width=50)
entry_folder.pack(pady=5)
btn_browse = tk.Button(root, text="Browse", command=select_folder)
btn_browse.pack(pady=5)

btn_organize = tk.Button(root, text="Organize Music", font=("Arial", 12), bg="green", fg="white", command=organize_music)
btn_organize.pack(pady=10)

progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, length=400)
progress_bar.pack(pady=10)

status_label = tk.Label(root, text="", font=("Arial", 10))
status_label.pack(pady=10)

root.mainloop()
