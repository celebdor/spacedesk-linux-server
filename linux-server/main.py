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


def autodetect_tablet() -> tuple[int, int]:
    """List connected USB devices and let the user pick the tablet."""
    import usb.core

    devices = list(usb.core.find(find_all=True))
    # Filter out AOA devices (already in accessory mode) and USB hubs
    candidates = [d for d in devices
                  if d.idVendor != 0x18D1 and d.bDeviceClass != 9]
    if not candidates:
        print("No USB devices found.")
        sys.exit(1)

    print("Connected USB devices:")
    for i, d in enumerate(candidates):
        try:
            mfr = d.manufacturer or "?"
        except Exception:
            mfr = "?"
        try:
            prod = d.product or "?"
        except Exception:
            prod = "?"
        print(f"  [{i}] {d.idVendor:04x}:{d.idProduct:04x}  {mfr} — {prod}")

    try:
        choice = int(input("Select device number: "))
        dev = candidates[choice]
    except (ValueError, IndexError):
        print("Invalid selection.")
        sys.exit(1)

    print(f"Selected {dev.idVendor:04x}:{dev.idProduct:04x}")
    return dev.idVendor, dev.idProduct


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="spacedesk Linux server")
    parser.add_argument("--usb-only", action="store_true",
                        help="Only accept USB connections (disable TCP/WebSocket and UDP discovery)")

    vid_group = parser.add_mutually_exclusive_group()
    vid_group.add_argument("--autodetect", action="store_true",
                           help="List connected USB devices and prompt to select the tablet")
    vid_group.add_argument("--vid", type=lambda x: int(x, 16), default=None,
                           help="Tablet VID in normal mode (hex, e.g. 04e8)")

    parser.add_argument("--pid", type=lambda x: int(x, 16), default=None,
                        help="Tablet PID in normal mode (hex, e.g. 6860)")

    VALID_SCALES = [1.0 + 0.25 * i for i in range(13)]  # 1.0, 1.25, ..., 4.0
    parser.add_argument(
        "--scale", type=float, default=1.0,
        help="GNOME display scale for the virtual monitor (1.0-4.0 in 0.25 steps). "
             "Fractional values require: gsettings set org.gnome.mutter "
             "experimental-features \"['scale-monitor-framebuffer']\"")

    args = parser.parse_args()

    if args.autodetect and (args.vid is not None or args.pid is not None):
        parser.error("--autodetect cannot be combined with --vid/--pid")
    if (args.vid is None) != (args.pid is None):
        parser.error("--vid and --pid must be specified together")
    if args.scale not in VALID_SCALES:
        parser.error(f"--scale must be one of: {', '.join(f'{s:.2f}' for s in VALID_SCALES)}")

    normal_vid, normal_pid = None, None
    if args.autodetect:
        normal_vid, normal_pid = autodetect_tablet()
    elif args.vid is not None:
        normal_vid, normal_pid = args.vid, args.pid

    main(usb_only=args.usb_only,
         normal_vid=normal_vid,
         normal_pid=normal_pid,
         scale=args.scale)
