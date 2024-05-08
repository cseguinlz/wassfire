from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from src.config import settings

router = APIRouter()

# Configuration for FastMail using settings from config.py
email_conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.MAIL_USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
)


@router.post("/send-email/")
async def send_contact_email(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    reason: str = Form(...),
    message: str = Form(...),
):
    subject = "New Contact Message from WassFire"
    body = f"Message from {name} ({email}) about {reason}:\n{message}"

    email_message = MessageSchema(
        subject=subject,
        recipients=[settings.MAIL_USERNAME],  # or any admin/recipient email
        body=body,
        subtype="html",
    )

    fm = FastMail(email_conf)
    await fm.send_message(email_message)
    content = (
        f"<p>Thanks {name}, we've got your message ✅, well get back to you soon<p>"
    )
    # Returning HTML snippet for user feedback
    return HTMLResponse(content=content, status_code=200)
