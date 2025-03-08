import os
import random
import subprocess
from colorama import Fore, Style, init

init(autoreset=True)

def get_albums(music_directory):
    """Scans the music directory and returns a list of album folders."""
    albums = []
    paths = []
    for root, dirs, files in os.walk(music_directory):
        if files:  # Only consider directories that contain files (assuming music files are present)
            album_name = os.path.basename(root)  # Extract only the album name
            artist_name = os.path.basename(os.path.dirname(root))  # Extract artist name
            albums.append((artist_name, album_name))
            paths.append(root)
    return albums, paths

def pick_random_albums(albums, paths, num=5, used_artists=set(), start_num=1):
    """Selects albums ensuring each artist has an equal chance of selection."""
    
    # Organize albums by artist
    artist_albums = {}
    for (artist, album), path in zip(albums, paths):
        if artist not in artist_albums:
            artist_albums[artist] = []
        artist_albums[artist].append((album, path))

    # Create a list of artists who haven't been used yet
    available_artists = [artist for artist in artist_albums if artist not in used_artists]

    # If not enough unique artists, reset used artists
    if len(available_artists) < num:
        print(Fore.LIGHTRED_EX + "✨ Not enough unique artists available, resetting selection. ✨")
        used_artists.clear()
        available_artists = list(artist_albums.keys())

    # Randomly pick artists
    selected_artists = random.sample(available_artists, min(num, len(available_artists)))

    # Pick a random album from each selected artist
    selected = []
    for artist in selected_artists:
        album, path = random.choice(artist_albums[artist])
        selected.append((artist, album, path))
        used_artists.add(artist)  # Mark artist as used

    return [(i + start_num, f"{artist} - {album}", path) for i, (artist, album, path) in enumerate(selected)], used_artists

def open_album_in_foobar(album_path):
    """Opens the selected album in Foobar2000 and sets default playback mode."""
    foobar_path = r"H:\\New Folder\\foobar2000\\foobar2000.exe"
    if not os.path.exists(foobar_path):
        print(Fore.LIGHTRED_EX + "💔 Foobar2000 not found. Make sure it's installed and the path is correct. 💔")
        return
    try:
        subprocess.run([foobar_path, "/stop"], check=True)  # Stop current playback
        subprocess.run([foobar_path, "/command:Default"], check=True)  # Reset to default playback mode
        subprocess.run([foobar_path, "/add", album_path], check=True)  # Add album to playlist
        subprocess.run([foobar_path, "/play"], check=True)  # Start playback
    except PermissionError:
        print(Fore.LIGHTRED_EX + "🚨 Permission denied. Try running the script as Administrator. 🚨")
    except FileNotFoundError:
        print(Fore.LIGHTRED_EX + "❌ Error launching Foobar2000. Check if the application is installed. ❌")

def main():
    music_directory = r"H:\\New Folder\\music"
    albums, paths = get_albums(music_directory)
    
    if not albums:
        print(Fore.LIGHTRED_EX + "💔 No albums found in the specified directory. 💔")
        return
    
    used_artists = set()
    start_num = 1
    all_selected_albums = []
    
    while True:
        new_albums, used_artists = pick_random_albums(albums, paths, used_artists=used_artists, start_num=start_num)
        all_selected_albums.extend(new_albums)
        
        print(Fore.LIGHTRED_EX + "💖 Here are your random albums 💖")
        for num, album, _ in all_selected_albums:
            print(Fore.LIGHTYELLOW_EX + f"✨ {num}. {album} ✨")
        
        choice = input(Fore.LIGHTRED_EX + "💅 Enter the number of the album you want to play in Foobar2000 (or 0 to get new recommendations): ")
        if choice.isdigit():
            choice = int(choice)
            if choice == 0:
                start_num = all_selected_albums[-1][0] + 1  # Continue numbering
                continue  # Generate new recommendations
            for num, _, path in all_selected_albums:
                if num == choice:
                    open_album_in_foobar(path)
                    return
        else:
            print(Fore.LIGHTRED_EX + "💔 Invalid input. Exiting. 💔")
            return

if __name__ == "__main__":
    main()
