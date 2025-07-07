#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import logging
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scrapper.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


def setup_logging(log_file='application.log', console_level=logging.INFO, file_level=logging.DEBUG):
    """
    Configures the logging system once for the entire application.
    """
    # Create a logger for the root (or specific top-level logger if preferred)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Set the lowest level for the logger

    # Clear any existing handlers to prevent duplicate output if called multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 1. Console Handler (for real-time feedback)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 2. File Handler (for persistent logs)
    file_handler = logging.FileHandler(log_file, mode='a')  # 'a' for append
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Optional: Set a specific logger's level higher if it's too noisy
    # logging.getLogger('requests').setLevel(logging.WARNING)
    # logging.getLogger('urllib3').setLevel(logging.WARNING)


if __name__ == '__main__':
    # Configure logging at the very beginning of your application
    setup_logging(log_file='python.log', console_level=logging.INFO, file_level=logging.DEBUG)
    main()
