#!/usr/bin/env python3
"""
Send a test frame via TCP, then read & print KISS frames from a TCP Socket.

For use with programs like Dire Wolf.
"""
import os

from ax253 import Frame, FrameType
import kiss


MYCALL = os.environ.get("MYCALL", "N0CALL")
KISS_HOST = os.environ.get("KISS_HOST", "192.168.6.115")
KISS_PORT = os.environ.get("KISS_PORT", "8102")


def print_frame(frame):
    print(Frame.from_bytes(frame))


def main():
    ki = kiss.TCPKISS(host=KISS_HOST, port=int(KISS_PORT), strip_df_start=True)
    ki.start()
    frame = Frame.ui(
        destination="PYKISS",
        source=MYCALL,
        path=[],
        info="",
        control=FrameType.S_RR.value | (1 << 4), 
    )
    ki.write(frame)
    ki.read(callback=print_frame, min_frames=None)


if __name__ == "__main__":
    main()