import os

from src.logger import get_logger

logger = get_logger()


def download(url: str, input_dir: str):
    import yt_dlp

    os.makedirs(input_dir, exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(input_dir, "%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get("title", url)
        logger.info(f'Download YouTube: "{title}"')
        ydl.download([url])
        logger.info("Download completato. Il watcher elaborerà il file automaticamente.")
