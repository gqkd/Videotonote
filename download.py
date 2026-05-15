import sys
import os
import yaml


def load_input_dir(config_path: str = "config.yaml") -> str:
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config["paths"]["input"]


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
        print(f'Download: "{title}"')
        print(f"Destinazione: {input_dir}")
        ydl.download([url])
        print("Download completato. Il watcher elaborerà il file automaticamente.")


def main():
    if len(sys.argv) < 2:
        print("Uso: python download.py <url-youtube>")
        print("Esempio: python download.py https://www.youtube.com/watch?v=...")
        sys.exit(1)

    url = sys.argv[1]
    input_dir = load_input_dir()
    download(url, input_dir)


if __name__ == "__main__":
    main()
