#!/usr/bin/env python
"""Django's command-line utility for administrative tasks (SADE v1.0)."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Install dependencies from "
            "backend/requirements.txt and ensure the virtualenv is active."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
