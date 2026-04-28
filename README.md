# 🎵 Music Mashup Web Application  
### 📌 Roll Number: 102303568  

---

## 🌟 Project Overview

This project implements a **Music Mashup Generator Web Application** using Python and Flask.

The system automatically:

- 🔍 Searches YouTube videos of a given singer  
- ⬇️ Downloads multiple videos  
- 🎧 Extracts audio from each video  
- ✂️ Trims the first *Y seconds* of each audio  
- 🔀 Merges all trimmed clips into a single mashup  
- 📦 Compresses the final output into a ZIP file  
- 📧 Sends the ZIP file to the user's email  

This project fulfills the **Mashup Assignment requirements** using PyPI libraries.

---

## 🛠 Technologies Used

| Technology | Purpose |
|------------|----------|
| **Python 3** | Core programming language |
| **Flask** | Web framework |
| **yt-dlp** | YouTube video downloading |
| **MoviePy** | Video-to-audio conversion |
| **Pydub** | Audio trimming & merging |
| **FFmpeg** | Media processing backend |
| **SMTP (Gmail)** | Email delivery |

All external libraries are installed via **PyPI**.

---

## 📂 Project Structure


> Note: Runtime folders are used dynamically and may not contain files in the repository.

---

## ⚙️ How the System Works

1️⃣ User enters:
- Singer name  
- Number of videos (>10)  
- Duration per clip (>20 seconds)  
- Email address  

2️⃣ Backend performs:
- YouTube search via `yt-dlp`
- Video download
- Audio extraction via MoviePy
- Audio trimming via Pydub
- Audio merging
- ZIP compression
- Email delivery via Gmail SMTP

---

## ▶️ How to Run the Application

### 1️⃣ Install Dependencies

```bash
pip install flask yt-dlp moviepy pydub

ffmpeg -version

SENDER_EMAIL = "yourgmail@gmail.com"
SENDER_PASSWORD = "your_gmail_app_password"

python app.py
