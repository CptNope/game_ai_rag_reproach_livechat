import socket
import threading

import pytest

from mario_ai.retroarch import RetroArch, RetroArchError


def serve(reply_for):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]

    def loop():
        while True:
            try:
                data, addr = sock.recvfrom(1024)
            except OSError:
                return
            reply = reply_for(data.decode())
            if reply is not None:
                sock.sendto(reply.encode(), addr)

    threading.Thread(target=loop, daemon=True).start()
    return sock, port


def test_read_memory_parses_hex_bytes():
    sock, port = serve(lambda msg: "READ_CORE_MEMORY 756 01 0a ff" if msg == "READ_CORE_MEMORY 756 3" else None)
    try:
        assert RetroArch("127.0.0.1", port).read_memory(0x756, 3) == bytes([1, 10, 255])
    finally:
        sock.close()


def test_read_memory_error_reply():
    sock, port = serve(lambda msg: "READ_CORE_MEMORY 756 -1 no memory map defined")
    try:
        with pytest.raises(RetroArchError, match="no memory map"):
            RetroArch("127.0.0.1", port).read_memory(0x756, 1)
    finally:
        sock.close()


def test_status():
    sock, port = serve(lambda msg: "GET_STATUS PAUSED nes,Game,crc32=0" if msg == "GET_STATUS" else None)
    try:
        assert RetroArch("127.0.0.1", port).status() == "PAUSED"
    finally:
        sock.close()


def test_no_reply_explains_how_to_turn_it_on():
    sock, port = serve(lambda msg: None)
    try:
        with pytest.raises(RetroArchError, match="Network Commands"):
            RetroArch("127.0.0.1", port, timeout=0.2).read_memory(0, 1)
    finally:
        sock.close()
