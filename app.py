from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


def get_sheet():
    creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(os.environ["GOOGLE_SHEET_ID"]).sheet1
    return sheet


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "API running"})


@app.route("/batch", methods=["GET"])
def get_batch():
    # Normalize incoming batch ID (case-insensitive)
    batch_id = request.args.get("batch_id", "").strip().upper()

    if not batch_id:
        return jsonify({"error": "batch_id parameter missing"}), 400

    sheet = get_sheet()
    records = sheet.get_all_records(value_render_option="FORMULA")

    for row in records:
        sheet_batch = str(row.get("batch_id", "")).strip().upper()
        if sheet_batch == batch_id:
            return jsonify(row)

    return jsonify({"error": "Batch not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


