
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from yt_dlp import YoutubeDL
import uuid
import os
import glob

app = FastAPI()

os.makedirs("downloads", exist_ok=True)

class SongRequest(BaseModel):
    url: str

@app.get("/")
async def home():

    return {
        "status": "running"
    }

@app.post("/download")
async def download_song(data: SongRequest):

    try:

        unique_id = str(uuid.uuid4())

        output_template = f"downloads/{unique_id}.%(ext)s"

        ydl_opts = {

            "format": "bestaudio/best",

            "outtmpl": output_template,

            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],

            "extractor_args": {
                "youtube": {
                    "player_client": ["android"]
                }
            }

        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([data.url])

        mp3_files = glob.glob(
            f"downloads/{unique_id}*.mp3"
        )

        if not mp3_files:

            return {
                "success": False
            }

        filename = os.path.basename(mp3_files[0])

        return {

            "success": True,

            "download_url": f"/file/{filename}"

        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }

@app.get("/file/{filename}")
async def get_file(filename: str):

    path = f"downloads/{filename}"

    return FileResponse(
        path,
        media_type="audio/mpeg",
        filename=filename
        )
