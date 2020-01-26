import pandas as pd
import numpy as np
from typing import List


def known_regions() -> List[str]:
    """
    known regions in Sollentuna
    """
    return [
        "VIBY",
        "NORRVIKEN",
        "TÖJNAN",
        "EDSVIKEN",
        "HELENELUND",
        "ROTEBRO",
        "HÄGGVIK",
        "FÅGELSÅNGEN",
        "SILVERDAL",
        "TEGELHAGEN",
        "TÖRNSKOGEN",
        "SJÖBERG",
        "ROTSUNDA",
        "KÄRRDAL",
        "TUREBERG",
        "GILLBO",
        "EDSÄNGEN",
        "LANDSNORA",
        "VAXMORA",
        "SOLÄNGEN",
        "VÄSJÖN",
        "KVARNSKOGEN",
    ]


def known_brokers() -> List[str]:
    return [
        "Fastighetsbyrån",
        "Mäklarhuset",
        "Bjurfors",
        "Susanne Persson",
        "Notar",
        "Länsförsäkringar",
        "HusmanHagberg",
        "Svensk Fastighetsförmedling",
        "SkandiaMäklarna",
        "ERA",
        "Erik Olsson",
    ]


def clean_region(region: str):
    u_region = region.upper()
    if "VIBY" in u_region:
        return "VIBY"
    if "NORRVIKEN" in u_region:
        return "NORRVIKEN"
    if "TÖJNAN" in u_region:
        return "TÖJNAN"
    if "EDSVIKEN" in u_region:
        return "EDSVIKEN"
    if "HELENELUND" in u_region:
        return "HELENELUND"
    if "ROTEBRO" in u_region:
        return "ROTEBRO"
    if "HÄGGVIK" in u_region:
        return "HÄGGVIK"
    if "FÅGELSÅNGEN" in u_region:
        return "FÅGELSÅNGEN"
    if "SILVERDAL" in u_region:
        return "SILVERDAL"
    if "TEGELHAGEN" in u_region:
        return "TEGELHAGEN"
    if "TÖRNSKOGEN" in u_region:
        return "TÖRNSKOGEN"
    if "SJÖBERG" in u_region:
        return "SJÖBERG"
    if "ROTSUNDA" in u_region:
        return "ROTSUNDA"
    if "KÄRRDAL" in u_region:
        return "KÄRRDAL"
    if "TUREBERG" in u_region:
        return "TUREBERG"
    if "GILLBO" in u_region:
        return "GILLBO"
    if "EDSÄNGEN" in u_region:
        return "EDSÄNGEN"
    if "LANDSNORA" in u_region:
        return "LANDSNORA"
    if "VAXMORA" in u_region:
        return "VAXMORA"
    if "SOLÄNGEN" in u_region:
        return "SOLÄNGEN"
    if "VÄSJÖN" in u_region:
        return "VÄSJÖN"
    if "KVARNSKOGEN" in u_region:
        return "KVARNSKOGEN"
    return "SOLLENTUNA"


def clean_broker(broker_name: str) -> str:
    for name in known_brokers():
        if name in broker_name:
            return name
    return "Other"


def clean_data(
    input_file: str,
    output_file: str,
    cat_output_file: str = "data/processed/houses_w_cat.csv",
):
    df = pd.read_csv(input_file)

    # remove any houses that don't have area set
    df = df[df.area.isnull() == False]

    # set missing rooms based on an avg. room size of 25
    df["rooms"].fillna(df.area / 25.0, inplace=True)

    # land_area is 0 for condos
    df["land_area"].fillna(0, inplace=True)
    df = df[df.land_area < 5000]
    df["is_condo"] = df.monthly_fee > 0

    # add a few new features based on old
    df["total_area"] = df.area + df.sup_area
    df["price_per_sqm"] = df.price / df.area
    df["price_per_tsqm"] = df.price / df.total_area
    df["list_price"] = (
        np.round((df.price * 100 / (100 + df.price_change)) / 1000, 0) * 1000
    )
    df["price_tkr"] = df.price / 1000
    df["listprice_tkr"] = df.list_price / 1000

    # clean up the region
    df["region"].fillna("UNKNOWN", inplace=True)
    df["region"] = df.apply(lambda row: clean_region(row["region"]), axis=1)

    # clean up the brokers
    df["broker"].fillna("UNKNOWN", inplace=True)
    df["broker"] = df.apply(lambda row: clean_broker(row["broker"]), axis=1)

    # add more time values
    df["date_sold"] = pd.to_datetime(df["date_sold"])
    df["year"] = df["date_sold"].dt.year
    df["month"] = df["date_sold"].dt.month
    df["running_month"] = (df["year"] - 2013) * 12 + df["month"]

    # clean up crazy price changes
    df = df[df.price_change < 50]

    # save to new file
    df.to_csv(output_file, index=False)

    # make some features categorical
    df.house_type = pd.Categorical(df.house_type)
    df.house_type = df.house_type.cat.codes
    df.is_condo = pd.Categorical(df.is_condo)
    df.is_condo = df.is_condo.cat.codes
    df.region = pd.Categorical(df.region)
    df.region = df.region.cat.codes
    df.broker = pd.Categorical(df.broker)
    df.broker = df.broker.cat.codes

    df.to_csv(cat_output_file, index=False)


if __name__ == "__main__":
    clean_data("data/interim/houses.csv", "data/processed/houses.csv")
