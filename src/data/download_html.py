import requests


def download_file(page: int, save_path: str = 'data/raw'):
    page_str = str(page)
    base_url = "https://www.hemnet.se/salda/bostader?item_types%5B%5D=villa&item_types%5B%5D=radhus&location_ids%5B%5D=18027&sold_age=all&page="
    content = requests.get(base_url + page_str).content
    with open(f'{save_path}/{page_str}.html', 'w') as f:
        f.write(str(content))


def main():
    for i in range(1, 70):
        download_file(i)


if __name__ == "__main__":
    main()
