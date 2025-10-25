"""Email template utilities."""

from string import Template
from typing import Dict, Any, Optional
from pathlib import Path


class EmailTemplate:
    """Simple email template class."""

    def __init__(self, subject_template: str, body_template: str):
        self.subject_template = Template(subject_template)
        self.body_template = Template(body_template)

    def render(self, **kwargs) -> tuple[str, str]:
        """Render template with provided variables."""
        subject = self.subject_template.safe_substitute(**kwargs)
        body = self.body_template.safe_substitute(**kwargs)
        return subject, body

    @classmethod
    def from_files(cls, subject_file: Path, body_file: Path) -> "EmailTemplate":
        """Create template from files."""
        subject = subject_file.read_text(encoding="utf-8").strip()
        body = body_file.read_text(encoding="utf-8")
        return cls(subject, body)


# Predefined templates
NOTIFICATION_TEMPLATE = EmailTemplate(
    "Notification: $title",
    """
Hello,

This is a notification from PyUtils:

$message

Time: $timestamp
System: $hostname

Best regards,
PyUtils Bot
    """.strip(),
)

ERROR_TEMPLATE = EmailTemplate(
    "Error Alert: $error_type",
    """
An error has occurred:

Error Type: $error_type
Error Message: $error_message
Location: $location
Time: $timestamp

Stack Trace:
$stack_trace

Please investigate this issue.

Best regards,
PyUtils Error Monitor
    """.strip(),
)

REPORT_TEMPLATE = EmailTemplate(
    "Daily Report: $date",
    """
Daily Report for $date

Summary:
- Total files processed: $files_processed
- Errors encountered: $error_count
- Warnings: $warning_count
- Execution time: $execution_time

Details:
$details

Best regards,
PyUtils Reporter
    """.strip(),
)
