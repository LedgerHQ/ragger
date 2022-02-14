from struct import pack


def pack_APDU(cla: int, ins: int,
              p1: int = 0, p2: int = 0,
              data: bytes = b"") -> int:
    return pack(">BBBBB", cla, ins, p1, p2, len(data)) + data
