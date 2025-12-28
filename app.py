{\rtf1\ansi\ansicpg1252\cocoartf2709
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 traceability-api/\
\uc0\u9500 \u9472 \u9472  app.py\
\uc0\u9500 \u9472 \u9472  requirements.txt\
\uc0\u9500 \u9472 \u9472  Procfile\
\uc0\u9492 \u9472 \u9472  .gitignore\
}
from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from google.oauth2.service_account import Credentials
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Load credentials from environment variable
creds_json = json.loads(os.environ.get("GOOGLE_CREDS_JSON"))

scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = Credentials.from_service_account_info(creds_json, scopes=scopes)
client = gspread.authorize(creds)

# Open Google Sheet
SHEET_NAME = "Batch_Register"
sheet = client.open(SHEET_NAME).sheet1


@app.route("/api/verify-batch", methods=["POST"])
def verify_batch():
    data = request.get_json()
    batch_id = data.get("batch_id")

    if not batch_id:
        return jsonify({"status": "error", "message": "Batch ID is required"}), 400

    records = sheet.get_all_records()

    for row in records:
        if row["batch_id"] == batch_id and row["qc_status"] == "Approved":
            return jsonify({
                "status": "success",
                "batch_id": row["batch_id"],
                "sku": row["sku"],
                "product_name": row["product_name"],
                "fpo_name": row["fpo_name"],
                "fpo_location": row["fpo_location"],
                "harvest_period": row["harvest_period"],
                "processing_date": row["processing_date"],
                "packaging_date": row["packaging_date"],
                "qc_certificate_url": row["qc_certificate_url"],
                "verified_on": datetime.utcnow().isoformat()
            })

    return jsonify({
        "status": "error",
        "message": "Invalid or unapproved batch ID"
    }), 404


if __name__ == "__main__":
    app.run()
