import os
import time
from pytube import Playlist, YouTube
from openpyxl import Workbook
from openpyxl.drawing.image import Image
import requests
import tempfile


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


def get_excel_path(directory, playlist_title):
    sanitized_title = sanitize_filename(playlist_title)
    filename = f"{sanitized_title}.xlsx"
    return os.path.join(directory, filename)


def download_thumbnail(url, temp_dir):
    response = requests.get(url)
    if response.status_code == 200:
        temp_image_path = os.path.join(
            temp_dir, tempfile.mktemp(suffix=".jpg"))
        with open(temp_image_path, 'wb') as f:
            f.write(response.content)
        return temp_image_path
    else:
        return None


def main():
    playlist_url = input("Enter the YouTube playlist URL: ")
    directory = input(
        "Enter the directory where you want to save the Excel file: ")

    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    temp_dir = tempfile.mkdtemp()  # Create a temporary directory for thumbnail images
    temp_files = []  # List to keep track of temporary file paths

    playlist_title = get_playlist_title(playlist_url)
    if playlist_title is None:
        print("Failed to retrieve playlist title. Exiting.")
        return

    excel_path = get_excel_path(directory, playlist_title)
    workbook = Workbook()
    ws = workbook.active
    ws.append(["Thumbnail", "Title", "URL"])

    row = 2
    for url in Playlist(playlist_url).video_urls:
        try:
            time.sleep(2)  # Delay to avoid rate limits
            video = YouTube(url)
            print(f"Retrieving: {video.title}")
            thumbnail_path = download_thumbnail(video.thumbnail_url, temp_dir)
            if thumbnail_path:
                img = Image(thumbnail_path)
                ws.add_image(img, f'A{row}')
                temp_files.append(thumbnail_path)  # Track the temporary file
            ws[f'B{row}'] = video.title
            ws[f'C{row}'] = video.watch_url
            row += 1
        except Exception as e:
            print(f"Error retrieving video details: {e}")

    workbook.save(filename=excel_path)

    # Delete temporary files after saving the workbook
    for temp_file in temp_files:
        os.remove(temp_file)
    os.rmdir(temp_dir)  # Remove the temporary directory


if __name__ == "__main__":
    main()
