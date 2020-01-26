from bs4 import BeautifulSoup
from datetime import datetime
import glob
import numpy as np
import os.path
import pandas as pd
from progressbar import ProgressBar
import re


def read_content(filename: str):
    with open(filename) as f:
        encoded_content = f.readline()
    content = bytes(encoded_content, 'utf-8').decode('unicode-escape')
    content = content.replace('Ã¥', 'å').replace('Ã¤', 'ä').replace('Ã¶', 'ö').replace('Ã©', 'é').replace('Ã\x85', 'Å').replace('Ã\x96', 'Ö').replace('â\x80\x93', '-')
    return content


def extract_houses(content: str):
    soup = BeautifulSoup(content, 'html.parser')
    return soup.find_all(class_="sold-results__normal-hit")


def extract_house_type(house):
    try:
        return house.find(class_="svg-icon__fallback-text").get_text()
    except AttributeError:
        return ''


def extract_address(house):
    # TODO: URL Encode
    try:
        return house.find(class_="sold-property-listing__heading").find(class_="item-link").get_text()
    except AttributeError:
        return ''


def extract_region(house):
    try:
        region = house.find(class_="sold-property-listing__location").find("div", recursive=False).find(class_="item-link").get_text().strip().replace(",", "")
        return region
    except AttributeError:
        return ""


def clean_numeric_string(unicode_str: str):
    # remove white space
    cleaned_str = re.sub(r"\s+", "", unicode_str, flags=re.UNICODE)
    # remove control characters
    cleaned_str = cleaned_str.replace('Â', '')
    # turn into a "US" float
    cleaned_str = cleaned_str.replace(",", ".")
    return cleaned_str


def extract_area(house):
    try:
        size_rows = house.find(
            class_="sold-property-listing__size").find(
                class_="sold-property-listing__subheading").get_text().splitlines()
        return (float)(clean_numeric_string(size_rows[1]).replace('m²', ''))
    except AttributeError:
        return np.NaN
    except ValueError:
        return np.NaN


def extract_sup_area(house):
    try:
        sup_area_str = house.find(class_="sold-property-listing__supplemental-area").get_text()
        sup_area_str = clean_numeric_string(sup_area_str).replace('m²biarea', '')
        return (float)(sup_area_str)
    except AttributeError:
        return 0.0


def extract_rooms(house):
    try:
        size_rows = house.find(
            class_="sold-property-listing__size").find(
                class_="sold-property-listing__subheading").get_text().splitlines()
        room_str = size_rows[3]
        return (float)(clean_numeric_string(room_str).replace('rum', ''))
    except AttributeError:
        return np.NaN
    except ValueError:
        return np.NaN


def extract_land_area(house):
    try:
        land_area_str = house.find(class_="sold-property-listing__land-area").get_text()
        land_area_str = clean_numeric_string(land_area_str).replace("m²tomt", "")
        return (float)(land_area_str)
    except AttributeError:
        return np.NaN


def extract_monthly_fee(house):
    try:
        monthly_fee_str = house.find(class_="sold-property-listing__fee").get_text().strip()
        monthly_fee_str = re.sub(r"\s+", "", monthly_fee_str, flags=re.UNICODE).replace("kr/mån", "").replace('Â', '').replace(",", ".")
        return (float)(monthly_fee_str)
    except AttributeError:
        return 0.0


def convert_to_date(swedish_date):
    us_date = swedish_date.replace("januari","Jan").replace("februari", "Feb").replace("mars", "Mar").replace("april", "Apr").replace("maj", "May").replace("juni", "Jun").replace("juli", "Jul").replace("augusti", "Aug").replace("september", "Sep").replace("oktober", "Oct").replace("november", "Nov").replace("december", "Dec")
    return datetime.strptime(us_date, "%d %b %Y")


def extract_date_sold(house):
    try:
        date_sold = house.find(class_="sold-property-listing__sold-date").get_text().replace("Såld", "").strip()
        return convert_to_date(date_sold)
    except AttributeError:
        return np.NaN


def extract_broker(house):
    try:
        return house.find(class_="sold-property-listing__broker").get_text().strip()
    except AttributeError:
        return ''


def extract_price_change(house):
    try:
        price_change_pct_str = house.find(class_="sold-property-listing__price-change").get_text()
        price_change_pct_str = clean_numeric_string(price_change_pct_str).replace('%', '')
        return (float)(price_change_pct_str)
    except AttributeError:
        return 0.0
    except ValueError:
        return 0.0


def extract_price(house):
    try:
        price_str = house.find(class_="sold-property-listing__price").find(class_="sold-property-listing__subheading").get_text()
        price_str = clean_numeric_string(price_str).replace("Slutpris", "").replace("kr", "")
        return (float)(price_str)
    except AttributeError:
        return np.NaN


def process_file(filename: str):
    content = read_content(filename)
    houses_data = extract_houses(content)
    houses = [{"house_type": extract_house_type(house),
               "address": extract_address(house),
               "region": extract_region(house),
               "area": extract_area(house),
               "sup_area": extract_sup_area(house),
               "rooms": extract_rooms(house),
               "land_area": extract_land_area(house),
               "monthly_fee": extract_monthly_fee(house),
               "date_sold": extract_date_sold(house),
               "broker": extract_broker(house),
               "price_change": extract_price_change(house),
               "price": extract_price(house)}
              for house in houses_data]
    return houses


def process_html_files(input_path: str, output_path: str):
    all_houses = []
    input_files = glob.glob(input_path + "/*.html")

    progress = ProgressBar(maxval=len(input_files))
    progress.start()

    for i, filename in enumerate(input_files):
        # print(f"processing {filename}")
        all_houses += process_file(filename)
        progress.update(i)

    progress.finish()

    output_file = os.path.join(output_path, "houses.csv")
    df = pd.DataFrame(all_houses)
    df.to_csv(output_file, index=False)

    print(f"processed {len(all_houses)} houses")


if __name__ == "__main__":
    process_html_files('data/raw', 'data/interim')
