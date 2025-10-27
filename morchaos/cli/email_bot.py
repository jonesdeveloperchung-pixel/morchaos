"""CLI for email bot."""

import argparse

from ..email.bot import TorrentBot, EmailBot
from ..core.logging import get_logger, set_log_level
from ..core.config import load_config


def main():
    """Main CLI entry point for email bot."""
    parser = argparse.ArgumentParser(description="Run email bot")
    parser.add_argument("--config", required=True,
                        help="Configuration file path")
    parser.add_argument(
        "--type", choices=["generic", "torrent"], default="generic",
        help="Bot type"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        set_log_level("DEBUG")

    log = get_logger(__name__)

    # Load configuration
    config = load_config(args.config)

    if "email" not in config:
        log.error("Email configuration not found in config file")
        exit(1)

    email_config = config["email"]

    # Create bot based on type
    if args.type == "torrent":
        if "torrent_program" not in config:
            log.error("torrent_program not specified in config")
            exit(1)

        bot = TorrentBot(
            bot_email=email_config["username"],
            password=email_config["password"],
            torrent_program=config["torrent_program"],
            imap_server=email_config.get("imap_server", "imap.gmail.com"),
            smtp_server=email_config.get("smtp_server", "smtp.gmail.com"),
            authorized_senders=email_config.get("authorized_senders", []),
            poll_interval=email_config.get("poll_interval", 300),
        )
    else:
        bot = EmailBot(
            bot_email=email_config["username"],
            password=email_config["password"],
            imap_server=email_config.get("imap_server", "imap.gmail.com"),
            smtp_server=email_config.get("smtp_server", "smtp.gmail.com"),
            authorized_senders=email_config.get("authorized_senders", []),
            poll_interval=email_config.get("poll_interval", 300),
        )

        # Register some basic commands
        bot.register_command("ping", lambda args: "pong")
        bot.register_command("echo", lambda args: args)

    log.info(f"Starting {args.type} email bot")

    try:
        bot.run()
    except KeyboardInterrupt:
        log.info("Bot stopped by user")


if __name__ == "__main__":
    main()
