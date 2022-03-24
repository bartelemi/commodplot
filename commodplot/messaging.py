import logging
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid
from os import environ
from pathlib import Path
from smtplib import SMTP, SMTPException

logger = logging.getLogger(__name__)


class EmailBuilder:
    """Easily compose multipart e-mail messages, set headers and add attachments."""

    def __init__(self):
        self.message = MIMEMultipart()

    def set_sender(self, email: str):
        self.message["From"] = email
        return self

    def set_receiver(self, email: str):
        self.message["To"] = email
        return self

    def set_bcc(self, email: str):
        self.message["Bcc"] = email
        return self

    def set_subject(self, subject: str):
        self.message["Subject"] = subject
        return self

    def set_body(self, body: str, content_type: str = "html"):
        self.message.attach(MIMEText(body, content_type))
        self.message.set
        return self

    def attach_file(self, file_name: str, attachment_name: str = None, content_id: str = None):
        file_path = Path(file_name)
        try:
            with file_path.open("rb") as attachment:
                part = MIMEApplication(attachment.read())
        except OSError:
            logger.error(f"Cannot add an e-mail attachment {file_name}")
            raise
        # Add headers describing the attachment.
        # Use either the provided attachment name, or file name.
        content_id = content_id or make_msgid(domain="energy.local")
        content_name = attachment_name or file_path.name
        part.add_header("Content-ID", f"<{content_id}>")
        part.add_header("Content-Disposition", f"attachment; filename= {content_name}")
        # Finally, add attachment to the message.
        self.message.attach(part)
        return self

    def attach_image(self, image: str | bytes, content_id: str = None):
        """Attach image part to the message, optionally set the content-id header."""
        content_id = content_id or make_msgid(domain="energy.local")
        part = MIMEImage(image)
        part.add_header("Content-ID", f"<{content_id}>")
        part.add_header("Content-Disposition", f"inline; filename={content_id}")
        self.message.attach(part)
        return self

    def build(self) -> str:
        """Complete the process and return the entire email message as a text."""
        return self.message.as_string()


def compose_and_send_report(subject: str, content: str) -> None:
    """
    Compose an e-mail message containing the report and send.

    Configuration:
    * ENV: SENDER_EMAIL - email address of the sender
    * ENV: RECEIVER_EMAIL - email address for the recipients
    * ENV: SMTP_HOST - hostname of the SMTP server
    * ENV: SMTP_PORT - port of the SMTP server (default: 25)
    * ENV: SMTP_TIMEOUT - timeout for SMTP operations (default: 60 seconds)
    """
    sender_email = environ.get("SENDER_EMAIL")
    receiver_email = environ.get("RECEIVER_EMAIL")
    smtp_host = environ.get("SMTP_HOST")
    smtp_port = int(environ.get("SMTP_PORT", "25"))
    smtp_timeout = int(environ.get("SMTP_TIMEOUT", "60"))
    message = (
        EmailBuilder()
        .set_sender(sender_email)
        .set_receiver(receiver_email)
        .set_subject(subject)
        .set_body(content)
        .build()
    )
    logger.info("Sending report e-mail to %s", receiver_email)
    try:
        with SMTP(smtp_host, smtp_port, timeout=smtp_timeout) as client:
            client.starttls()
            client.sendmail(sender_email, receiver_email, message)
        logger.info("Report sent successfully")
    except SMTPException:
        logger.exception("Failed to send a report")
