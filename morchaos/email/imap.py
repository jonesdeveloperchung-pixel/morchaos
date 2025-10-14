"""IMAP email reading utilities."""

import imaplib
import email
from email.header import decode_header
from typing import List, Dict, Any, Optional, Tuple

from ..core.logging import get_logger

log = get_logger(__name__)

class IMAPClient:
    """IMAP client for reading emails."""
    
    def __init__(self, server: str, username: str, password: str, 
                 port: int = 993, use_ssl: bool = True):
        self.server = server
        self.username = username
        self.password = password
        self.port = port
        self.use_ssl = use_ssl
        self.connection = None
    
    def connect(self) -> bool:
        """Connect to IMAP server."""
        try:
            if self.use_ssl:
                self.connection = imaplib.IMAP4_SSL(self.server, self.port)
            else:
                self.connection = imaplib.IMAP4(self.server, self.port)
            
            self.connection.login(self.username, self.password)
            log.info(f"Connected to IMAP server: {self.server}")
            return True
            
        except Exception as e:
            log.error(f"Failed to connect to IMAP server: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from IMAP server."""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
            except:
                pass
            self.connection = None
    
    def list_folders(self) -> List[str]:
        """List all folders."""
        if not self.connection:
            return []
        
        try:
            status, folders = self.connection.list()
            if status == 'OK':
                folder_names = []
                for folder in folders:
                    # Parse folder name from IMAP response
                    folder_str = folder.decode() if isinstance(folder, bytes) else folder
                    # Extract folder name (last part after quotes)
                    parts = folder_str.split('"')
                    if len(parts) >= 3:
                        folder_names.append(parts[-2])
                return folder_names
        except Exception as e:
            log.error(f"Failed to list folders: {e}")
        
        return []
    
    def select_folder(self, folder: str = 'INBOX') -> bool:
        """Select a folder."""
        if not self.connection:
            return False
        
        try:
            status, messages = self.connection.select(folder)
            if status == 'OK':
                log.info(f"Selected folder: {folder}")
                return True
        except Exception as e:
            log.error(f"Failed to select folder {folder}: {e}")
        
        return False
    
    def search_emails(self, criteria: str = 'ALL') -> List[int]:
        """Search for emails matching criteria."""
        if not self.connection:
            return []
        
        try:
            status, messages = self.connection.search(None, criteria)
            if status == 'OK':
                message_ids = messages[0].split()
                return [int(mid) for mid in message_ids]
        except Exception as e:
            log.error(f"Failed to search emails: {e}")
        
        return []
    
    def get_email(self, message_id: int) -> Optional[Dict[str, Any]]:
        """Get email by message ID."""
        if not self.connection:
            return None
        
        try:
            status, msg_data = self.connection.fetch(str(message_id), '(RFC822)')
            if status == 'OK':
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                # Decode subject
                subject = decode_header(email_message['Subject'])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                
                return {
                    'id': message_id,
                    'subject': subject,
                    'from': email_message['From'],
                    'to': email_message['To'],
                    'date': email_message['Date'],
                    'message': email_message
                }
        except Exception as e:
            log.error(f"Failed to get email {message_id}: {e}")
        
        return None
    
    def get_email_body(self, email_message: email.message.EmailMessage) -> str:
        """Extract plain text body from email."""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = email_message.get_payload(decode=True).decode()
        
        return body
    
    def delete_email(self, message_id: int) -> bool:
        """Delete an email."""
        if not self.connection:
            return False
        
        try:
            self.connection.store(str(message_id), '+FLAGS', '\\Deleted')
            self.connection.expunge()
            log.info(f"Deleted email {message_id}")
            return True
        except Exception as e:
            log.error(f"Failed to delete email {message_id}: {e}")
            return False

def check_gmail(username: str, password: str, folder: str = 'INBOX') -> List[Dict[str, Any]]:
    """Check Gmail for new messages."""
    client = IMAPClient('imap.gmail.com', username, password)
    
    if not client.connect():
        return []
    
    try:
        if not client.select_folder(folder):
            return []
        
        message_ids = client.search_emails('UNSEEN')  # Unread messages
        emails = []
        
        for msg_id in message_ids[-10:]:  # Get last 10 unread
            email_data = client.get_email(msg_id)
            if email_data:
                emails.append(email_data)
        
        return emails
        
    finally:
        client.disconnect()