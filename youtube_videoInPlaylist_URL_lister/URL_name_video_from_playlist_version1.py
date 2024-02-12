# first fetch all videos and then write the data
import os
import csv
import time
from pytube import Playlist, YouTube


def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def get_playlist_title(url):
    try:
        playlist = Playlist(url)
        return playlist.title
    except Exception as e:
        print(f"Error retrieving playlist title: {e}")
        return None


def get_csv_path(directory, playlist_title):
    sanitized_title = sanitize_filename(playlist_title)
    filename = f"{sanitized_title}.csv"
    return os.path.join(directory, filename)


def get_existing_videos(csv_path):
    if not os.path.exists(csv_path):
        with open(csv_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Create file with header if it doesn't exist
            writer.writerow(["Title", "URL"])
        return {}
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return {row["URL"]: row["Title"] for row in reader}


def save_new_videos_to_csv(csv_path, new_videos):
    with open(csv_path, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for video in new_videos:
            writer.writerow([video['title'], video['url']])


def main():
    playlist_url = input("Enter the YouTube playlist URL: ")
    directory = input(
        "Enter the directory where you want to save the CSV file: ")

    os.makedirs(directory, exist_ok=True)

    playlist_title = get_playlist_title(playlist_url)
    if playlist_title is None:
        print("Failed to retrieve playlist title. Exiting.")
        return

    csv_path = get_csv_path(directory, playlist_title)
    existing_videos = get_existing_videos(csv_path)

    playlist = Playlist(playlist_url)
    new_videos = []

    for url in playlist.video_urls:
        try:
            time.sleep(2)  # Delay to avoid rate limits
            video = YouTube(url)  # Fetch video details
            print(f"Retrieving: {video.title}")
            if video.watch_url not in existing_videos:
                new_videos.append(
                    {'title': video.title, 'url': video.watch_url})
        except Exception as e:
            print(f"Error retrieving video details: {e}")

    if new_videos:
        save_new_videos_to_csv(csv_path, new_videos)
        print(f"Added {len(new_videos)} new videos to {csv_path}")
    else:
        print("No new videos found in the playlist.")


if __name__ == "__main__":
    main()
