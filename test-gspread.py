import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets setup
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
gc = gspread.authorize(creds)
sheet = gc.open("MIR4 Player Rankings").sheet1

data = [["Rank", "Player Name", "Power Score", "Clan Name"]]
rank_counter = 1
page = 1

while True:
    print(f"Fetching page {page}...")
    url = f"https://forum.mir4global.com/rank?ranktype=1&worldgroupid=1&worldid=824&page={page}"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    rows = soup.select("tr.list_article, tr.first.list_article, tr.second.list_article, tr.third.list_article")
    if not rows:
        break

    for row in rows:
        user_span = row.select_one(".user_name")
        power_span = row.select_one("td.text_right span")  # ✅ updated selector
        clan_span = row.select_one("td:nth-of-type(3) span")

        if user_span and power_span and clan_span:
            player_name = user_span.text.strip()
            power_score = power_span.text.strip()
            clan_name = clan_span.text.strip()
            data.append([rank_counter, player_name, power_score, clan_name])
            rank_counter += 1

    page += 1

# Push to Google Sheet
sheet.clear()
sheet.append_rows(data)
print(f"Wrote {len(data) - 1} player rankings to Google Sheet.")
