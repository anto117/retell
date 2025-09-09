import os
import json
from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime
import sys

app = Flask(__name__)

# Reconstruct service account JSON from environment variables
service_account_info = {
    "type": os.getenv("SERVICE_ACCOUNT_TYPE"),
    "project_id": os.getenv("SERVICE_ACCOUNT_PROJECT_ID"),
    "private_key_id": os.getenv("SERVICE_ACCOUNT_PRIVATE_KEY_ID"),
    "private_key": os.getenv("SERVICE_ACCOUNT_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("SERVICE_ACCOUNT_CLIENT_EMAIL"),
    "client_id": os.getenv("SERVICE_ACCOUNT_CLIENT_ID"),
    "auth_uri": os.getenv("SERVICE_ACCOUNT_AUTH_URI"),
    "token_uri": os.getenv("SERVICE_ACCOUNT_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("SERVICE_ACCOUNT_AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("SERVICE_ACCOUNT_CLIENT_CERT_URL"),
}

try:
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=["https://www.googleapis.com/auth/calendar"]
    )
except Exception as e:
    print(f"Failed to initialize credentials: {e}", file=sys.stderr)
    sys.exit(1)

service = build("calendar", "v3", credentials=credentials)
CALENDAR_ID = os.getenv("CALENDAR_ID")

@app.route("/book-appointment", methods=["POST"])
def book_appointment():
    data = request.get_json()
    name = data.get("name")
    phone = data.get("phone")
    date_time = data.get("date_time")
    email = data.get("email") or f"{name.replace(' ', '').lower()}@placeholder.com"

    try:
        event = {
            "summary": f"Appointment - {name}",
            "description": f"Phone: {phone}",
            "start": {"dateTime": date_time, "timeZone": "Asia/Kolkata"},
            "end": {
                "dateTime": (datetime.datetime.fromisoformat(date_time)
                             + datetime.timedelta(minutes=30)).isoformat(),
                "timeZone": "Asia/Kolkata",
            },
            "attendees": [{"email": email}],
        }

        event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        return jsonify({
            "success": True,
            "message": "Appointment booked",
            "link": event.get("htmlLink")
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
