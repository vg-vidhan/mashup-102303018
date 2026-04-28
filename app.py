import os
import uuid
import shutil
import zipfile
import smtplib
from email.message import EmailMessage

from flask import Flask, render_template, request
from moviepy import VideoFileClip
from pydub import AudioSegment
import yt_dlp

# ==================================================
# FLASK APP CONFIG
# ==================================================
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VIDEO_DIR = os.path.join(BASE_DIR, "videos")
AUDIO_DIR = os.path.join(BASE_DIR, "audios")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

for folder in [VIDEO_DIR, AUDIO_DIR, OUTPUT_DIR]:
    os.makedirs(folder, exist_ok=True)

# ==================================================
# EMAIL CONFIG
# Use environment variables for security
# ==================================================
SENDER_EMAIL = os.getenv("EMAIL_USER")
SENDER_PASSWORD = os.getenv("EMAIL_PASS")

# ==================================================
# HELPERS
# ==================================================
def clear_folder(folder_path):
    """Delete all files inside folder."""
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)


def validate_inputs(video_count, duration):
    if video_count < 11:
        raise ValueError("Number of videos must be greater than 10.")

    if duration < 20:
        raise ValueError("Duration must be at least 20 seconds.")


# ==================================================
# DOWNLOAD VIDEOS
# ==================================================
def download_videos(artist_name, video_count):
    clear_folder(VIDEO_DIR)

    options = {
        "format": "bv*+ba/best",
        "merge_output_format": "mp4",
        "outtmpl": os.path.join(VIDEO_DIR, "%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "ignoreerrors": True,
        "nocheckcertificate": True,
    }

    query = f"ytsearch{video_count}:{artist_name}"

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([query])


# ==================================================
# CREATE MASHUP
# ==================================================
def create_mashup(artist_name, video_count, duration):
    clear_folder(AUDIO_DIR)
    clear_folder(OUTPUT_DIR)

    download_videos(artist_name, video_count)

    video_files = os.listdir(VIDEO_DIR)
    collected_clips = []

    for index, filename in enumerate(video_files[:video_count]):
        video_path = os.path.join(VIDEO_DIR, filename)
        audio_path = os.path.join(AUDIO_DIR, f"clip_{index}.mp3")

        try:
            video = VideoFileClip(video_path)
            video.audio.write_audiofile(audio_path, logger=None)
            video.close()

            audio = AudioSegment.from_file(audio_path)
            trimmed_audio = audio[: duration * 1000]
            collected_clips.append(trimmed_audio)

        except Exception as error:
            print(f"Skipping file {filename}: {error}")

    final_mix = AudioSegment.empty()

    for clip in collected_clips:
        final_mix += clip.fade_in(500).fade_out(500)

    unique_name = f"mashup_{uuid.uuid4().hex[:8]}.mp3"
    output_path = os.path.join(OUTPUT_DIR, unique_name)

    final_mix.export(output_path, format="mp3")
    return output_path


# ==================================================
# ZIP FILE
# ==================================================
def create_zip(mp3_file_path):
    zip_path = mp3_file_path.replace(".mp3", ".zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(mp3_file_path, arcname=os.path.basename(mp3_file_path))

    return zip_path


# ==================================================
# SEND EMAIL
# ==================================================
def send_email(receiver_email, attachment_path):
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        raise Exception("Email credentials not configured.")

    message = EmailMessage()
    message["Subject"] = "Your Music Mashup"
    message["From"] = SENDER_EMAIL
    message["To"] = receiver_email
    message.set_content("Your mashup file is attached.")

    with open(attachment_path, "rb") as file:
        message.add_attachment(
            file.read(),
            maintype="application",
            subtype="zip",
            filename=os.path.basename(attachment_path),
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(message)


# ==================================================
# FLASK ROUTE
# ==================================================
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            artist_name = request.form["singer"].strip()
            video_count = int(request.form["videos"])
            duration = int(request.form["duration"])
            receiver_email = request.form["email"].strip()

            validate_inputs(video_count, duration)

            mp3_path = create_mashup(
                artist_name=artist_name,
                video_count=video_count,
                duration=duration,
            )

            zip_path = create_zip(mp3_path)
            send_email(receiver_email, zip_path)

            return "Mashup created and sent successfully!"

        except Exception as error:
            return f"Error: {str(error)}"

    return render_template("index.html")


# ==================================================
# RUN APP
# ==================================================
if __name__ == "__main__":
    app.run(debug=True)