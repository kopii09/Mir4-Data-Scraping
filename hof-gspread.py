import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

# === Google Sheets Setup ===
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
gc = gspread.authorize(creds)

# Open your spreadsheet (must exist and be shared with the service account)
sheet = gc.open("MIR4 Player Rankings").sheet1

# === Scraping Setup ===
BASE_URL = "https://www.hofgamer.com/leaderboard/"
data = [["Rank", "Name", "Combat Power", "Merit", "Class", "Alliance", "Region", "Server", "Clan"]]

# Scrape only pages 1 to 4
for page in range(1, 5):
    print(f"Fetching page {page}...")
    params = {
        "region": "ASIA1",
        "server": "ASIA024",
        "job": "all",
        "alliance": "all",
        "sort_by": "power",
        "page": page
    }

    resp = requests.get(BASE_URL, params=params)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    table = soup.find("table")
    if not table:
        print("No table found on page", page)
        continue

    trs = table.find_all("tr")[1:]  # Skip header
    if not trs:
        print("No rows found on page", page)
        continue

    for tr in trs:
        cols = [td.text.strip() for td in tr.find_all("td")]
        if len(cols) >= 9:
            data.append(cols[:9])  # Rank, Name, CP, Merit, Class, Alliance, Region, Server, Clan

    time.sleep(1)  # Be polite

# === Push to Google Sheets ===
sheet.clear()
sheet.append_rows(data)
print(f"Wrote {len(data)-1} player rows to 'HofGamer Leaderboard'.")
