from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime
import os
import json

app = Flask(__name__)

# Load service account info from environment variable
service_account_info = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_ID = os.getenv("CALENDAR_ID", "antozreju800@gmail.com")

# Create credentials from service account info
credentials = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES
)

service = build("calendar", "v3", credentials=credentials)

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

