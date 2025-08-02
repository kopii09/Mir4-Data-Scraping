# Mir4-Data-Scraping

Will extract players on a specific server and will display Player Name, Power Score, and Clan Name

Below are the steps on how to setup and get your own credentials.json

Step 1: Create a Google Sheet
Go to https://sheets.google.com
Create a new sheet, name it something like: "MIR4 Player Rankings"

---

Step 2: Create a Google Cloud Project & Enable Sheets API
Visit: https://console.developers.google.com

    Click the project dropdown (top left) → "New Project"
        Name the project (e.g., Mir4SheetsProject) → click Create

    After it’s created, click “Select Project”

    Enable the Google Sheets API:
        Go to APIs & Services > Library
        Search for Google Sheets API
        Click it → Click Enable

---

Step 3: Create a Service Account and Download credentials.json
Go to APIs & Services > Credentials

    Click “+ Create Credentials” → “Service account”
    Fill in:
    Name: mir4-service or anything you'd like
    Click Create and Continue → skip roles → click Done

    Create a JSON Key:
        Find your new service account in the list

        Click on it → Go to the “KEYS” tab

            Click “Add Key” → “Create New Key”
            Select JSON → click Create
            This downloads a .json file to your computer

        After downloading the file:
            Rename the file to: "credentials.json"
            Move it into the same directory as your Python script (e.g., test-gspread.py)

---

Step 4: Share Your Google Sheet with the Service Account
Open your Google Sheet

    Click Share

    Open credentials.json in a text editor and copy the "client_email" value, e.g.: "mir4-service@your-project-id.iam.gserviceaccount.com"

    Paste that email into the Share dialog

    Give Editor access → Click Send

---

Step 5: Install Python Libraries (if not yet installed)

    "pip install gspread oauth2client selenium"

    Now you're ready to run your script:
    "python test-gspread.py"
