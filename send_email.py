import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape

from dotenv import load_dotenv
from fetch_news import fetch_articles, HOURS_BACK

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")


def build_html(articles):
    items = ""
    for a in articles:
        items += f"""
        <li style="margin-bottom:14px;">
          <a href="{escape(a["link"])}" style="font-size:16px;color:#1a5fb4;text-decoration:none;">
            {escape(a["title"])}
          </a><br>
          <span style="font-size:13px;color:#666;">{escape(a["source"])}</span>
        </li>"""

    return f"""
    <html><body style="font-family:Arial,sans-serif;max-width:640px;margin:auto;">
      <h2 style="color:#222;">AI Daily Digest</h2>
      <p style="color:#555;">{len(articles)} stories from the last {HOURS_BACK} hours</p>
      <ul style="padding-left:18px;">{items}</ul>
    </body></html>"""


def send_digest():
    articles = fetch_articles()
    if not articles:
        print("No articles found, skipping email.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"AI Daily Digest - {datetime.now().strftime('%b %d, %Y')}"
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL
    msg.attach(MIMEText(build_html(articles), "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(msg)

    print(f"Sent digest with {len(articles)} articles to {RECIPIENT_EMAIL}")


if __name__ == "__main__":
    send_digest()
