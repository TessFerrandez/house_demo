import os
import requests
from dotenv import find_dotenv, load_dotenv


def download_file(base_url: str, page: int, save_path: str = "data/raw"):
    page_str = str(page)
    content = requests.get(base_url + page_str).content
    with open(f"{save_path}/{page_str}.html", "w") as f:
        f.write(str(content))


def main():
    base_url = os.environ.get("BASE_URL")
    for i in range(1, 70):
        download_file(base_url, i)


if __name__ == "__main__":
    load_dotenv(find_dotenv())
    main()
