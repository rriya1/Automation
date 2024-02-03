import os
import csv
from datetime import datetime
from pytube import Playlist
from moviepy.editor import *
import time


def get_song_names_from_playlist(url):
    playlist = Playlist(url)
    return [video.title for video in playlist.videos]


def get_existing_songs(csv_path):
    if not os.path.exists(csv_path):
        with open(csv_path, 'w', newline='', encoding='utf-8') as file:
            pass  # Just create an empty file
        return []

    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        return [row[0] for row in reader]


def save_new_songs_to_csv(csv_path, new_songs):
    with open(csv_path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows([song] for song in new_songs)


def sanitize_filename(filename):
    invalid_chars = '<>:"/\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


# def download_song_to_directory(video, directory):
#     sanitized_title = sanitize_filename(video.title)
#     video_stream = video.streams.filter(only_audio=True).first()
#     video_path = video_stream.download(directory, filename=sanitized_title)
#     audio_path = os.path.join(directory, sanitized_title + ".mp3")

#     try:
#         # Convert video to mp3
#         clip = AudioFileClip(video_path)
#         clip.write_audiofile(audio_path)
#         os.remove(video_path)
#     except Exception as e:
#         print(f"Error downloading {sanitized_title}: {e}")
def download_song_to_directory(video, directory, retries=3):
    sanitized_title = sanitize_filename(video.title)
    for _ in range(retries):
        try:
            video_stream = video.streams.filter(only_audio=True).first()
            video_path = video_stream.download(
                directory, filename=sanitized_title)
            audio_path = os.path.join(directory, sanitized_title + ".mp3")
            # Convert video to mp3
            clip = AudioFileClip(video_path)
            clip.write_audiofile(audio_path)
            os.remove(video_path)
            break  # If successful, break out of retry loop
        except Exception as e:
            print(f"Error downloading {sanitized_title}. Retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying


# def main():
#     playlist_url = input("Enter the YouTube playlist URL: ")
#     songs_directory = input(
#         "Enter the path to the directory where you want to save the songs: ")
#     csv_path = os.path.join(songs_directory, "songs.csv")

#     playlist = Playlist(playlist_url)
#     existing_songs = get_existing_songs(csv_path)

#     new_songs = [
#         video for video in playlist.videos if video.title not in existing_songs]

#     if new_songs:
#         current_date = datetime.now().strftime('%b%d')
#         new_folder_path = os.path.join(songs_directory, current_date)
#         os.makedirs(new_folder_path, exist_ok=True)

#         for video in new_songs:
#             download_song_to_directory(video, new_folder_path)
#             time.sleep(10)

#         save_new_songs_to_csv(csv_path, [video.title for video in new_songs])
#         print(f"Downloaded {len(new_songs)} new songs to {new_folder_path}")
#     else:
#         print("No new songs found in the playlist.")

def main():
    playlist_url = input("Enter the YouTube playlist URL: ")
    songs_directory = input(
        "Enter the path to the directory where you want to save the songs: ")

    # Ensure songs directory exists
    os.makedirs(songs_directory, exist_ok=True)

    playlist = Playlist(playlist_url)
    playlist_title = playlist.title
    sanitized_playlist_title = sanitize_filename(playlist_title)
    csv_name = sanitized_playlist_title + ".csv"

    csv_path = os.path.join(songs_directory, csv_name)
    existing_songs = get_existing_songs(csv_path)

    new_songs = [
        video for video in playlist.videos if video.title not in existing_songs]

    if not new_songs:
        print("No new songs found in the playlist.")
        return

    # Determine the new folder name for today's date and current hour
    # today = datetime.datetime.now().strftime("%b%d_%Hh")
    today = datetime.now().strftime("%b%d_%Hh")
    new_folder_path = os.path.join(songs_directory, today)
    os.makedirs(new_folder_path, exist_ok=True)

    for video in new_songs:
        download_song_to_directory(video, new_folder_path)

    save_new_songs_to_csv(csv_path, [video.title for video in new_songs])

    print("All songs have been downloaded successfully!")


if __name__ == "__main__":
    main()
