#!/usr/bin/env python3
"""Punto de entrada del servidor spacedesk para Linux.

Requiere el Python del sistema (/usr/bin/python3), no un venv/conda, porque
necesita los bindings PyGObject (gi) del sistema para GStreamer/D-Bus.
Ejecutar: /usr/bin/python3 main.py
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from spacedesk_server.server import main  # noqa: E402

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="spacedesk Linux server")
    parser.add_argument("--usb-only", action="store_true",
                        help="Only accept USB connections (disable TCP/WebSocket and UDP discovery)")
    args = parser.parse_args()
    main(usb_only=args.usb_only)
