import calendar
from datetime import datetime

from bs4 import BeautifulSoup
import requests
import streamlit as st

dt = datetime.now()
day_name = dt.strftime('%A')
month_name = calendar.month_name[dt.month]
day_year = f"{dt.day}{dt.year}"

colors = {"none": "black", "low": "green", "heavy": "red"}

url = f"https://www.houstonhealth.org/services/pollen-mold/houston-pollen-mold-count-{day_name.lower()}-{month_name.lower()}-{day_year}"
img_url = "https://www.houstonhealth.org/sites/g/files/zsnnfi171/files/styles/coh_small/public/2023-08/{type}-400-3.jpg"

r = requests.get(url)
soup = BeautifulSoup(r.content, "lxml")
strong_tags = soup.findAll("strong")
if len(strong_tags) == 0:
    st.error("No counts yet (either it's early in the morning or it's the weekend)")
    st.stop()

counts = [s.text.split("\n") for s in strong_tags[0:4]]  # type, quality, quantity
counts = [[c[0].lower().replace("pollen", "").replace("spores", "").strip(), c[1].lower(), c[2]] for c in counts]

st.header(f"{day_name} {month_name} {dt.day} {dt.year}")

cols = st.columns(4)
for col, count in zip(cols, counts):
    count_type, quality, quantity = count
    color = colors.get(quality, 'black')

    col.image(img_url.format(type=count_type))
    col.markdown(f"<h3 style='text-align: center; color: {color};'>{quality}", unsafe_allow_html=True)
    col.markdown(f"<h3 style='text-align: center; color: {color};'>{quantity}", unsafe_allow_html=True)

st.link_button("Houston Health Site", url)
