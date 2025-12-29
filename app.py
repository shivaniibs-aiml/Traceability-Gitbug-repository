from flask import Flask, jsonify, request
import os
import json
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

def get_sheet():
    creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    client = gspread.authorize(creds)
    return client.open_by_key(os.environ["GOOGLE_SHEET_ID"]).sheet1

@app.route("/")
def health():
    return jsonify({"status": "API running"})

@app.route("/batch")
def get_batch():
    batch_id = request.args.get("batch_id")
    if not batch_id:
        return jsonify({"error": "batch_id is required"}), 400

    sheet = get_sheet()
    records = sheet.get_all_records()

    for row in records:
        if str(row.get("batch_id")).strip() == batch_id:
            return jsonify(row)

    return jsonify({"error": "Batch not found"}), 404

if __name__ == "__main__":
    app.run()

