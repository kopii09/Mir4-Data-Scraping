import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------- Google Sheets setup ----------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
gc = gspread.authorize(creds)
sheet = gc.open("MIR4 Player Rankings").sheet1   # first/tabbed worksheet

# ---------- Helpers ----------
def score_to_int(score_str: str) -> int:
    """Remove commas → int (e.g., '1,234,567' → 1234567)."""
    return int(score_str.replace(",", "").strip())

# ---------- Pull current sheet into memory ----------
# If the sheet is brand-new, add the header row first
if sheet.row_count == 0 or not sheet.get_all_values():
    sheet.append_row(["Rank", "Player Name", "Power Score", "Clan Name"])

existing_rows = sheet.get_all_values()
headers       = existing_rows[0]                       # ['Rank', 'Player Name', 'Power Score', 'Clan Name']
name_col      = headers.index("Player Name")           # 1 (zero-based)
power_col     = headers.index("Power Score")           # 2
clan_col      = headers.index("Clan Name")             # 3
rank_col      = headers.index("Rank")                  # 0

# Build a lookup: {player_name: (row_number, current_best_score)}
player_index = {}
for row_num, row in enumerate(existing_rows[1:], start=2):   # data starts on row 2
    if len(row) > power_col:
        pname = row[name_col]
        pscore = score_to_int(row[power_col]) if row[power_col] else 0
        player_index[pname] = (row_num, pscore)

# ---------- Scrape the ranking pages ----------
new_data = []  # will store [rank, name, score_str, clan]
rank_counter = 1
page = 1

while True:
    print(f"Fetching page {page}...")
    url  = f"https://forum.mir4global.com/rank?ranktype=1&worldgroupid=1&worldid=824&page={page}"
    resp = requests.get(url, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")

    rows = soup.select("tr.list_article, tr.first.list_article, tr.second.list_article, tr.third.list_article")
    if not rows:
        break  # no more pages

    for row in rows:
        user_span  = row.select_one(".user_name")
        power_span = row.select_one("td.text_right span")
        clan_span  = row.select_one("td:nth-of-type(3) span")

        if user_span and power_span and clan_span:
            player_name = user_span.text.strip()
            power_score = power_span.text.strip()          # keep comma version for display
            clan_name   = clan_span.text.strip()
            new_data.append([rank_counter, player_name, power_score, clan_name])
            rank_counter += 1
    page += 1

print(f"Fetched {len(new_data)} players.")

# ---------- Apply updates ----------
updates = []           # batch_update payloads
new_rows_to_append = []  # rows for players not yet in sheet

for rank, pname, pscore_str, clan in new_data:
    pscore_int = score_to_int(pscore_str)

    if pname in player_index:
        # Player already in sheet → compare scores
        row_num, best_score = player_index[pname]

        # Always refresh Rank & Clan (they change often)
        updates.append({
            "range": gspread.utils.rowcol_to_a1(row_num, rank_col + 1),
            "values": [[rank]]
        })
        updates.append({
            "range": gspread.utils.rowcol_to_a1(row_num, clan_col + 1),
            "values": [[clan]]
        })

        # Only overwrite Power Score if the new one is HIGHER
        if pscore_int > best_score:
            updates.append({
                "range": gspread.utils.rowcol_to_a1(row_num, power_col + 1),
                "values": [[pscore_str]]
            })
    else:
        # Brand-new player → append later
        new_rows_to_append.append([rank, pname, pscore_str, clan])

# Batch-update existing rows (fewer API calls)
if updates:
    sheet.batch_update([{"range": u["range"], "values": u["values"]} for u in updates])

# Append new players
if new_rows_to_append:
    sheet.append_rows(new_rows_to_append, value_input_option="USER_ENTERED")

print(f"Sheet updated: {len(updates)} cell edits, {len(new_rows_to_append)} new players.")
