import sys
import select

_poll = select.poll()
_poll.register(sys.stdin, select.POLLIN)

def get_key():
    if _poll.poll(0):
        line = sys.stdin.readline()
        while _poll.poll(0):
            sys.stdin.read(1)
        text = line.strip()
        if text:
            print("KEY:", repr(text))
        if text.upper() == "ESC":
            return "ESC"
        return text if text else None
    return None