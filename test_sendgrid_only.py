import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from main import FROM_NAME, SMTP_EMAIL, write_debug_log

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # If dotenv is not available, just skip; environment variables may still be set
    pass


def main():
    location = "test_sendgrid_only.py:main"

    # Read API key from environment (do NOT log or print the key)
    sendgrid_api_key = os.environ.get("SENDGRID_API_KEY", "")

    if not sendgrid_api_key:
        print("[ERROR] SENDGRID_API_KEY is not set in environment.")
        write_debug_log(location, "SendGrid API key missing", {"source": "env/dotenv_not_found"}, "G")
        return

    # Basic debug log (no secrets)
    write_debug_log(location, "SendGrid test starting", {"from_email": SMTP_EMAIL}, "G")

    to_email = os.environ.get("SENDGRID_TEST_EMAIL", "vanshjhamb9@gmail.com")

    subject = "SendGrid Test - Bodhih Assessments"
    html_content = """
    <html>
    <body>
        <h2>SendGrid Test Email</h2>
        <p>This is a test email sent via SendGrid from the Bodhih assessment system.</p>
    </body>
    </html>
    """

    message = Mail(
        from_email=f"{FROM_NAME} <{SMTP_EMAIL}>",
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        print(f"[SUCCESS] SendGrid test email sent to {to_email}. Status code: {response.status_code}")
        write_debug_log(location, "SendGrid email sent", {"to": to_email, "status_code": response.status_code}, "G")
    except Exception as e:
        print(f"[ERROR] SendGrid test failed: {e}")
        write_debug_log(location, "SendGrid email failed", {"error": str(e)}, "G")


if __name__ == "__main__":
    main()
