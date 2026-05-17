import os
import sys

import yaml

from src.downloader import download


def load_input_dir(config_path: str = "config.yaml") -> str:
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return os.environ.get("VTN_PATHS_INPUT") or config["paths"]["input"]


def main():
    if len(sys.argv) < 2:
        print("Usage: python download.py <youtube-url>")
        print("Example: python download.py https://www.youtube.com/watch?v=...")
        sys.exit(1)

    url = sys.argv[1]
    input_dir = load_input_dir()
    download(url, input_dir)


if __name__ == "__main__":
    main()
