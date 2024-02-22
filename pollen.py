import calendar
from datetime import date, timedelta, datetime

from bs4 import BeautifulSoup
import requests
import streamlit as st

colors = {"none": "black", "low": "green", "heavy": "red"}
img_url = "https://www.houstonhealth.org/sites/g/files/zsnnfi171/files/styles/coh_small/public/2023-08/{type}-400-3.jpg"


def parse_date(dt: datetime) -> tuple:
    return dt.strftime('%A'), calendar.month_name[dt.month], f"{dt.day}{dt.year}"


def construct_url(dt: datetime) -> str:
    day_name, month_name, day_year = parse_date(dt)
    return f"https://www.houstonhealth.org/services/pollen-mold/houston-pollen-mold-count-{day_name.lower()}-{month_name.lower()}-{day_year}"


def get(dt: datetime) -> tuple[list, datetime, str]:
    url = construct_url(dt)
    r = requests.get(url)
    if r.status_code == 404:
        prev_dt = dt - timedelta(days=1)
        return get(prev_dt)

    return BeautifulSoup(r.content, "lxml").findAll("strong"), dt, url


tags, dt, url = get(date.today())
day_name, month_name, _ = parse_date(dt)

counts = [s.text.split("\n") for s in tags[0:4]]  # type, quality, quantity
counts = [[c[0].lower().replace("pollen", "").replace("spores", "").strip(), c[1].lower(), c[2]] for c in counts]

st.subheader(f"Latest Counts for {day_name} {month_name} {dt.day}, {dt.year}")

cols = st.columns(4)
for col, count in zip(cols, counts):
    count_type, quality, quantity = count
    color = colors.get(quality, 'black')

    col.image(img_url.format(type=count_type), use_column_width="auto")
    col.markdown(f"<h3 style='text-align: center; color: {color};'>{quality}", unsafe_allow_html=True)
    col.markdown(f"<h3 style='text-align: center; color: {color};'>{quantity}", unsafe_allow_html=True)

st.link_button("Houston Health Site", url, use_container_width=True)
