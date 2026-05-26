from fastapi import FastAPI
from pydantic import BaseModel
from yt_dlp import YoutubeDL
from supabase import create_client
from datetime import datetime
import os
import uuid

# =========================
# SUPABASE CONFIG
# =========================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# =========================
# FASTAPI
# =========================

app = FastAPI()

class VideoRequest(BaseModel):
    url: str

# =========================
# ROUTES
# =========================

@app.get("/")
def home():
    return {
        "message": "API Running"
    }

@app.post("/convert")
def convert_video(data: VideoRequest):

    try:

        video_url = data.url

        unique_id = str(uuid.uuid4())

        ydl_opts = {
            "format": "bestaudio/best",

            "outtmpl": f"{unique_id}.%(ext)s",

            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],

            "extractor_args": {
                "youtube": {
                    "player_client": ["android"]
                }
            },

            "quiet": True
        }

        # DOWNLOAD
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                video_url,
                download=True
            )

            title = info.get(
                "title",
                "Unknown"
            )

        mp3_file = f"{unique_id}.mp3"

        if not os.path.exists(mp3_file):
            return {
                "success": False,
                "error": "MP3 not found"
            }

        storage_name = f"{unique_id}.mp3"

        # UPLOAD TO SUPABASE
        with open(mp3_file, "rb") as f:

            supabase.storage.from_("songs").upload(
                path=storage_name,
                file=f,
                file_options={
                    "content-type": "audio/mpeg"
                }
            )

        # PUBLIC URL
        public_url = supabase.storage.from_("songs").get_public_url(
            storage_name
        )

        # SAVE DATABASE
        supabase.table("songs").insert({
            "title": title,
            "file_url": public_url,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        # DELETE LOCAL FILE
        os.remove(mp3_file)

        return {
            "success": True,
            "title": title,
            "url": public_url
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
  }
