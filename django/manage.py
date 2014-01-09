#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # FIXME:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.server")
    os.environ.setdefault('ZOONAS_EMBEDLY_KEY', '')

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
