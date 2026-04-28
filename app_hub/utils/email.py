import requests
from django.conf import settings


def send_contact_email(name, email, message):
    html_content = f"""
    <h2>New Contact Message</h2>
    <p><strong>Name:</strong> {name}</p>
    <p><strong>Email:</strong> {email}</p>
    <p><strong>Message:</strong><br>{message}</p>
    """

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {settings.RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [settings.CONTACT_RECEIVER_EMAIL],
            "subject": f"New message from {name}",
            "html": html_content,
        },
        timeout=10,
    )

    return response.json()
