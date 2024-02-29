import calendar
from datetime import date, timedelta, datetime

from bs4 import BeautifulSoup
import requests
import streamlit as st
from operator import itemgetter

colors = {"none": "black", "low": "green", "medium": "orange", "heavy": "red", "extremely heavy": "red"}
img_url = "https://www.houstonhealth.org/sites/g/files/zsnnfi171/files/styles/coh_small/public/2023-08/{type}-400-3.jpg"


def parse_date(dt: datetime) -> tuple:
    return dt.strftime('%A'), calendar.month_name[dt.month], f"{dt.day}{dt.year}"


def construct_url(dt: datetime) -> str:
    day_name, month_name, day_year = parse_date(dt)
    return f"https://www.houstonhealth.org/services/pollen-mold/houston-pollen-mold-count-{day_name.lower()}-{month_name.lower()}-{day_year}"


def get(dt: datetime) -> tuple[BeautifulSoup, datetime, str]:
    url = construct_url(dt)
    r = requests.get(url)
    if r.status_code == 404:
        prev_dt = dt - timedelta(days=1)
        return get(prev_dt)

    return BeautifulSoup(r.content, "lxml"), dt, url


def parse_overall_counts(soup: BeautifulSoup) -> list[list]:
    tags = soup.findAll("strong")
    counts = [s.text.split("\n") for s in tags[0:4]]  # type, quality, quantity
    return [[c[0].lower().replace("pollen", "").replace("spores", "").strip(), c[1].lower(), c[2]] for c in counts]


def sort_and_filter_pollen_counts(counts: list[tuple]) -> list[tuple]:
    return [i for i in sorted(counts, key=itemgetter(1), reverse=True) if i[1] > 0]


def parse_specific_counts(soup: BeautifulSoup) -> list[tuple]:
    lis = soup.findAll("li")
    lis_parsed = [i.text.encode("ascii", "ignore").decode().split(":") for i in lis]
    specific_counts = [(i[0], int(i[1].strip())) for i in lis_parsed if len(i) == 2]

    names = list(map(itemgetter(0), specific_counts))
    weed_index = names.index("Ambrosia (Ragweed)")
    mold_index = names.index("Algae")

    tree_pollen = sort_and_filter_pollen_counts(specific_counts[0:weed_index])
    weed_pollen = sort_and_filter_pollen_counts(specific_counts[weed_index:mold_index])
    mold_pollen = sort_and_filter_pollen_counts(specific_counts[mold_index::])
    return tree_pollen, weed_pollen, mold_pollen


soup, dt, url = get(date.today())
counts = parse_overall_counts(soup)
tree_pollen, weed_pollen, mold_pollen = parse_specific_counts(soup)
day_name, month_name, _ = parse_date(dt)

st.subheader(f"Latest Counts for {day_name} {month_name} {dt.day}, {dt.year}")

cols = st.columns(4)
for col, count in zip(cols, counts):
    count_type, quality, quantity = count
    color = colors.get(quality, 'black')
    col.image(img_url.format(type=count_type), use_column_width="auto")
    col.markdown(f"<h3 style='text-align: center; color: {color};'>{quality}", unsafe_allow_html=True)
    col.markdown(f"<h3 style='text-align: center; color: {color};'>{quantity}", unsafe_allow_html=True)

cols = st.columns(3)
for col, counts in zip(cols, (tree_pollen, weed_pollen, mold_pollen)):
    for count in counts:
        col.write(f"{count[0]}: {count[1]}")

st.link_button("Houston Health Site", url, use_container_width=True)
