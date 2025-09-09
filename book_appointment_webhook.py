from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime
import os

app = Flask(__name__)

SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "service_account.json")
SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_ID = os.getenv("CALENDAR_ID", "antozreju800@gmail.com")

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
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
