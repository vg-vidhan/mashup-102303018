import os
import zipfile
import smtplib
from email.message import EmailMessage

from flask import Flask, render_template, request
from moviepy import VideoFileClip
from pydub import AudioSegment
import yt_dlp

# ==========================
# FLASK SETUP
# ==========================
app = Flask(__name__)

BASE_DIR = os.getcwd()
VIDEO_DIR = os.path.join(BASE_DIR, "videos")
AUDIO_DIR = os.path.join(BASE_DIR, "audios")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================
# 🔴 GMAIL CONFIG (EDIT THIS)
# ==========================
SENDER_EMAIL = "divyemahajan3@gmail.com"
SENDER_PASSWORD = "1234567891234567"

# ==========================
# DOWNLOAD YOUTUBE VIDEOS
# ==========================
def download_videos(singer, num_videos):
    ydl_opts = {
        # Let yt-dlp decide best working formats
        "format": "bv*+ba/best",
        "merge_output_format": "mp4",

        # Output location
        "outtmpl": os.path.join(VIDEO_DIR, "%(id)s.%(ext)s"),

        # Avoid junk
        "noplaylist": True,
        "quiet": True,

        # Required for YouTube reliability
        "nocheckcertificate": True,
        "ignoreerrors": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"ytsearch{num_videos}:{singer}"])

# ==========================
# CREATE MASHUP
# ==========================
def create_mashup(singer, num_videos, duration):
    audio_clips = []

    download_videos(singer, num_videos)

    video_files = os.listdir(VIDEO_DIR)[:num_videos]

    for i, video in enumerate(video_files):
        video_path = os.path.join(VIDEO_DIR, video)
        audio_path = os.path.join(AUDIO_DIR, f"audio_{i}.mp3")

        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(audio_path, logger=None)
        clip.close()

        audio = AudioSegment.from_file(audio_path)
        audio_clips.append(audio[:duration * 1000])

    final_audio = AudioSegment.empty()
    for clip in audio_clips:
        final_audio += clip

    output_file = os.path.join(OUTPUT_DIR, "mashup.mp3")
    final_audio.export(output_file, format="mp3")

    return output_file

# ==========================
# ZIP OUTPUT
# ==========================
def zip_output(mp3_path):
    zip_path = mp3_path.replace(".mp3", ".zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        zipf.write(mp3_path, arcname="mashup.mp3")
    return zip_path

# ==========================
# SEND EMAIL
# ==========================
def send_email(receiver_email, zip_path):
    msg = EmailMessage()
    msg["Subject"] = "Your Music Mashup"
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email
    msg.set_content("Your mashup ZIP file is attached.")

    with open(zip_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="zip",
            filename="mashup.zip"
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

# ==========================
# FLASK ROUTE
# ==========================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        singer = request.form["singer"]
        videos = int(request.form["videos"])
        duration = int(request.form["duration"])
        email = request.form["email"]

        if videos <= 10 or duration <= 20:
            return "Error: Videos must be >10 and duration must be >20 seconds"

        mp3 = create_mashup(singer, videos, duration)
        zip_file = zip_output(mp3)
        send_email(email, zip_file)

        return "Mashup created and sent to your email successfully!"

    return render_template("index.html")

# ==========================
# RUN SERVER
# ==========================
if __name__ == "__main__":
    app.run(debug=True)
