"""Email bot for automated command execution."""

import time
import subprocess
from typing import Dict, Any, Optional, Callable

from .imap import IMAPClient
from .smtp import SMTPClient
from ..core.logging import get_logger

log = get_logger(__name__)


class EmailBot:
    """Generic email bot that processes commands from emails."""

    def __init__(
        self,
        bot_email: str,
        password: str,
        imap_server: str = "imap.gmail.com",
        smtp_server: str = "smtp.gmail.com",
        authorized_senders: Optional[list] = None,
        poll_interval: int = 300,
    ):
        self.bot_email = bot_email
        self.password = password
        self.imap_server = imap_server
        self.smtp_server = smtp_server
        self.authorized_senders = authorized_senders or []
        self.poll_interval = poll_interval

        self.imap_client = IMAPClient(imap_server, bot_email, password)
        self.smtp_client = SMTPClient(smtp_server, 587, bot_email, password)

        self.commands = {}
        self.running = False

    def register_command(self, command: str, handler: Callable[[str], str]) -> None:
        """Register a command handler."""
        self.commands[command.lower()] = handler

    def is_authorized(self, sender: str) -> bool:
        """Check if sender is authorized."""
        if not self.authorized_senders:
            return True  # Allow all if no restrictions

        return any(auth in sender.lower() for auth in self.authorized_senders)

    def process_email(self, email_data: Dict[str, Any]) -> None:
        """Process a single email for commands."""
        sender = email_data["from"]
        subject = email_data["subject"]

        if not self.is_authorized(sender):
            log.warning(f"Unauthorized command attempt from {sender}")
            return

        # Extract command from subject
        if not subject.lower().startswith("cmd:"):
            return

        command_line = subject[4:].strip()
        parts = command_line.split(" ", 1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        log.info(f"Processing command '{command}' from {sender}")

        if command in self.commands:
            try:
                result = self.commands[command](args)
                self.send_response(sender, f"Command '{command}' completed", result)
            except Exception as e:
                error_msg = f"Command '{command}' failed: {str(e)}"
                log.error(error_msg)
                self.send_response(sender, f"Command '{command}' failed", error_msg)
        else:
            available = ", ".join(self.commands.keys())
            msg = f"Unknown command '{command}'. Available: {available}"
            self.send_response(sender, "Unknown command", msg)

    def send_response(self, to_address: str, subject: str, body: str) -> None:
        """Send response email."""
        full_subject = f"Bot Response: {subject}"
        self.smtp_client.send_email(to_address, full_subject, body)

    def run_once(self) -> None:
        """Process emails once."""
        if not self.imap_client.connect():
            log.error("Failed to connect to IMAP server")
            return

        try:
            if not self.imap_client.select_folder("INBOX"):
                return

            # Get unread emails
            message_ids = self.imap_client.search_emails("UNSEEN")

            for msg_id in message_ids:
                email_data = self.imap_client.get_email(msg_id)
                if email_data:
                    self.process_email(email_data)
                    # Mark as read by deleting the UNSEEN flag
                    self.imap_client.connection.store(str(msg_id), "-FLAGS", "\\Seen")

        finally:
            self.imap_client.disconnect()

    def run(self) -> None:
        """Run the bot continuously."""
        self.running = True
        log.info(f"Email bot started, polling every {self.poll_interval} seconds")

        while self.running:
            try:
                self.run_once()
                time.sleep(self.poll_interval)
            except KeyboardInterrupt:
                log.info("Bot stopped by user")
                break
            except Exception as e:
                log.error(f"Bot error: {e}")
                time.sleep(60)  # Wait before retrying

    def stop(self) -> None:
        """Stop the bot."""
        self.running = False


class TorrentBot(EmailBot):
    """Specialized bot for torrent management."""

    def __init__(self, bot_email: str, password: str, torrent_program: str, **kwargs):
        super().__init__(bot_email, password, **kwargs)
        self.torrent_program = torrent_program

        # Register torrent commands
        self.register_command("start", self._start_torrent)
        self.register_command("status", self._get_status)

    def _start_torrent(self, args: str) -> str:
        """Start torrent program with optional torrent file/magnet."""
        try:
            if args:
                # Start with specific torrent
                subprocess.Popen([self.torrent_program, args])
                return f"Started torrent program with: {args}"
            else:
                # Just start the program
                subprocess.Popen([self.torrent_program])
                return "Started torrent program"
        except Exception as e:
            return f"Failed to start torrent program: {e}"

    def _get_status(self, args: str) -> str:
        """Get system status."""
        return "Torrent bot is running"
