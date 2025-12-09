from fastapi import FastAPI
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import base64
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()

SCOPES = [os.getenv("GMAIL_SCOPE")]

TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "token.json")

def get_email_service():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return build("gmail", "v1", credentials=creds)

def extract_body(payload):
    """Recursively extract email body from MIME parts."""
    if "parts" in payload:
        for part in payload["parts"]:
            # If HTML part exists, prioritize it
            if part.get("mimeType") == "text/html":
                data = part["body"].get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8")

            # Fallback to plain text
            if part.get("mimeType") == "text/plain":
                data = part["body"].get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8")

            # Nested inside sub-parts
            if "parts" in part:
                nested = extract_body(part)
                if nested:
                    return nested

    # If body is directly in payload
    if payload["body"].get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")

    return None


@app.get("/emails/unread")
def get_unread_emails():
    service = get_email_service()

    results = service.users().messages().list(
        userId="me",
        q="is:unread"
    ).execute()

    messages = results.get("messages", [])

    emails = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me", id=msg["id"], format="full"
        ).execute()

        headers = msg_data["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), None)
        sender = next((h["value"] for h in headers if h["name"] == "From"), None)

        body = extract_body(msg_data["payload"])

        emails.append({
            "id": msg["id"],
            "subject": subject,
            "from": sender,
            "body": body
        })

    return {
        "count": len(emails),
        "emails": emails
    }
