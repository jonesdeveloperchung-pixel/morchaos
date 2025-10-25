"""SMTP email sending utilities."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Union, Optional, Dict, Any

from ..core.logging import get_logger

log = get_logger(__name__)


class SMTPClient:
    """SMTP client for sending emails."""

    def __init__(
        self,
        server: str,
        port: int = 587,
        username: str = "",
        password: str = "",
        use_tls: bool = True,
    ):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    def send_email(
        self,
        to_addresses: Union[str, List[str]],
        subject: str,
        body: str,
        from_address: Optional[str] = None,
        attachments: Optional[List[Union[str, Path]]] = None,
        html: bool = False,
    ) -> bool:
        """Send an email."""
        if isinstance(to_addresses, str):
            to_addresses = [to_addresses]

        from_address = from_address or self.username

        # Create message
        msg = MIMEMultipart()
        msg["From"] = from_address
        msg["To"] = ", ".join(to_addresses)
        msg["Subject"] = subject

        # Add body
        body_type = "html" if html else "plain"
        msg.attach(MIMEText(body, body_type))

        # Add attachments
        if attachments:
            for attachment_path in attachments:
                self._add_attachment(msg, attachment_path)

        try:
            # Connect and send
            with smtplib.SMTP(self.server, self.port) as server:
                if self.use_tls:
                    server.starttls()

                if self.username and self.password:
                    server.login(self.username, self.password)

                server.send_message(msg)

            log.info(f"Email sent to {to_addresses}")
            return True

        except Exception as e:
            log.error(f"Failed to send email: {e}")
            return False

    def _add_attachment(self, msg: MIMEMultipart, file_path: Union[str, Path]) -> None:
        """Add file attachment to email."""
        file_path = Path(file_path)

        if not file_path.exists():
            log.warning(f"Attachment not found: {file_path}")
            return

        with file_path.open("rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())

        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition", f"attachment; filename= {file_path.name}"
        )

        msg.attach(part)


def send_simple_email(
    smtp_server: str,
    username: str,
    password: str,
    to_address: str,
    subject: str,
    body: str,
    port: int = 587,
) -> bool:
    """Send a simple text email."""
    client = SMTPClient(smtp_server, port, username, password)
    return client.send_email(to_address, subject, body)


def send_gmail(
    username: str, password: str, to_address: str, subject: str, body: str
) -> bool:
    """Send email via Gmail SMTP."""
    return send_simple_email(
        "smtp.gmail.com", username, password, to_address, subject, body
    )
