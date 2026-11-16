"""Talk to RetroArch over its network command interface (UDP).

Turn it on in RetroArch: Settings > Network > Network Commands (port 55355),
or set network_cmd_enable = "true" in retroarch.cfg.
"""

import socket


class RetroArchError(RuntimeError):
    pass


class RetroArch:
    def __init__(self, host: str = "127.0.0.1", port: int = 55355, timeout: float = 1.0):
        self.address = (host, port)
        self.timeout = timeout

    def _send(self, message: str, expect_reply: bool) -> str:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(self.timeout)
            sock.sendto(message.encode("ascii"), self.address)
            if not expect_reply:
                return ""
            try:
                data, _ = sock.recvfrom(65535)
            except (socket.timeout, ConnectionResetError) as exc:
                raise RetroArchError(
                    "No reply from RetroArch. Is it running with Network Commands turned on (port %d)?" % self.address[1]
                ) from exc
        return data.decode("ascii", "replace").strip()

    def command(self, name: str) -> None:
        """Send a command with no reply, such as PAUSE_TOGGLE, RESET, SAVE_STATE or LOAD_STATE."""
        self._send(name, expect_reply=False)

    def status(self) -> str:
        """PLAYING, PAUSED or CONTENTLESS (first word of GET_STATUS)."""
        reply = self._send("GET_STATUS", expect_reply=True)
        parts = reply.split()
        return parts[1] if len(parts) > 1 and parts[0] == "GET_STATUS" else (parts[0] if parts else "")

    def read_memory(self, address: int, length: int) -> bytes:
        """Read bytes from the running game's system RAM."""
        reply = self._send("READ_CORE_MEMORY %x %d" % (address, length), expect_reply=True)
        parts = reply.split()
        if len(parts) < 3 or parts[0] != "READ_CORE_MEMORY":
            raise RetroArchError("Unexpected reply from RetroArch: %r" % reply[:80])
        if parts[2] == "-1":
            raise RetroArchError("RetroArch couldn't read memory: %s" % (" ".join(parts[3:]) or "unknown error"))
        values = bytes(int(b, 16) for b in parts[2:])
        if len(values) != length:
            raise RetroArchError("RetroArch returned %d bytes, expected %d" % (len(values), length))
        return values
