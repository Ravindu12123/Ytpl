from flask import Flask, request, jsonify, send_file
import os
import shutil
from yt_dlp import YoutubeDL
import math

app = Flask(__name__)

# Directory to store downloaded videos
DOWNLOAD_DIR = "downloads"

# Create the directory if it doesn't exist
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Configure yt-dlp options for downloading 1080p videos
YDL_OPTIONS = {
    "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
    "geo_bypass": True,  # Bypass regional restrictions
}


def human_readable_size(size):
    """Convert size in bytes to a human-readable format."""
    if size == 0:
        return "0B"
    units = ["B", "KB", "MB", "GB", "TB"]
    index = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, index)
    return f"{size / p:.2f} {units[index]}"


@app.route("/download_playlist", methods=["GET"])
def download_playlist():
    playlist_url = request.args.get("url")

    if not playlist_url:
        return jsonify({"error": "Playlist URL is required"}), 400

    try:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            ydl.download([playlist_url])
        return jsonify({"message": "Playlist downloaded successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download_video", methods=["GET"])
def download_video():
    video_url = request.args.get("url")

    if not video_url:
        return jsonify({"error": "Video URL is required"}), 400

    try:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            ydl.download([video_url])
        return jsonify({"message": "Video downloaded successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/list_files", methods=["GET"])
def list_files():
    try:
        files = os.listdir(DOWNLOAD_DIR)
        file_details = []

        for file in files:
            file_path = os.path.join(DOWNLOAD_DIR, file)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                file_details.append({
                    "filename": file,
                    "size": human_readable_size(file_size)
                })

        return jsonify({"files": file_details}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/clear", methods=["GET"])
def clear_directory():
    try:
        shutil.rmtree(DOWNLOAD_DIR)
        os.makedirs(DOWNLOAD_DIR)
        return jsonify({"message": "Download directory cleared"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_file/<filename>", methods=["GET"])
def get_file(filename):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        return jsonify({
            "filename": filename,
            "size": human_readable_size(file_size),
            "download_link": request.url_root + f"download/{filename}"
        })
    else:
        return jsonify({"error": "File not found"}), 404


@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8000)
